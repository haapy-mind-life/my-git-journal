---
created: 2025-03-28T14:58:32+09:00
modified: 2025-03-28T14:58:44+09:00
---

# Django 서버 코드#2

아래는 지금까지의 대화에서 정리된 **Django 서버 코드**와 **Streamlit 앱 코드**를 하나씩 순서대로 모두 출력합니다. 파일 크기가 클 수 있으므로 **각 파일 단위**로 나누어 안내드립니다.  
**(필요 시 "다음"이라고 해주시면 이어서 계속 코드 전부를 출력해 드립니다.)**

---

## **1. `django_server` 폴더 구조**

```
django_server/
├── manage.py
├── requirements.txt
├── django_server/
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   └── templates/
│       ├── unauthorized.html
│       └── admin_home.html
└── frontend/
    ├── models.py
    ├── admin.py
    ├── middleware.py
    └── templates/
        ├── access_statistics.html
        └── server_status.html
```

### (1) **`manage.py`**

```python
#!/usr/bin/env python
import os
import sys

def main():
    """Django's command-line utility for administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_server.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
```

### (2) **`requirements.txt`** (예시)

```plaintext
Django==4.2
psutil==5.9.8
requests==2.31.0
```

---

## **2. `django_server/django_server` 내부**

### (1) **`settings.py`**

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'your-secret-key'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'frontend',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # IP 기반 인증 미들웨어
    'frontend.middleware.IPAccessMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'django_server.urls'
WSGI_APPLICATION = 'django_server.wsgi.application'

# DB (SQLite 예시)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'

# 사용자 IP별 포트 할당 (예시)
STREAMLIT_PORTS = {
    '192.168.1.100': 8500,  # 관리자
    '192.168.1.101': 8501,  # 사용자 A
    '192.168.1.102': 8502,  # 사용자 B
}
```

### (2) **`urls.py`**

```python
from django.contrib import admin
from django.urls import path
from .views import main, admin_home

urlpatterns = [
    path('secure-admin/', admin.site.urls),  # 관리자 페이지 접근
    path('', main, name='main'),
    path('admin_home/', admin_home, name='admin_home'),
]
```

### (3) **`views.py`**

```python
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.conf import settings


def main(request):
    """IP 확인 후 Streamlit 포트로 리다이렉트 or 미등록 사용자 페이지."""
    user_ip = request.META.get('REMOTE_ADDR')
    port = settings.STREAMLIT_PORTS.get(user_ip)

    if port:
        # Streamlit 앱 주소로 리다이렉트
        host_ip = request.get_host().split(':')[0]
        return HttpResponseRedirect(f"http://{host_ip}:{port}")
    else:
        return render(request, 'unauthorized.html')


def admin_home(request):
    """관리자용 홈."""
    return render(request, 'admin_home.html')
```

### (4) **`templates/unauthorized.html`**

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>접근 제한</title>
</head>
<body>
  <h2>🚫 접근 제한 🚫</h2>
  <p>등록되지 않은 사용자입니다.</p>
</body>
</html>
```

### (5) **`templates/admin_home.html`**

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>관리자 페이지</title>
</head>
<body>
  <h2>🛠️ 관리자 전용 페이지</h2>
  <p><a href="/secure-admin/">Django Admin 접속</a></p>
  <p><a href="/">Streamlit 앱 접속</a></p>
</body>
</html>
```

---

## **3. `django_server/frontend` 내부**

### (1) **`models.py`**

```python
from django.db import models

class UserAccessLog(models.Model):
    ip_address = models.GenericIPAddressField()
    access_time = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(default=0)  # 체류 시간(초)

    def __str__(self):
        return f"{self.ip_address} @ {self.access_time}"
```

### (2) **`admin.py`**

```python
from django.contrib import admin
from .models import UserAccessLog

@admin.register(UserAccessLog)
class UserAccessLogAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'access_time', 'duration')
    ordering = ('-access_time',)
    list_filter = ('ip_address',)
    search_fields = ('ip_address',)
```

### (3) **`middleware.py`**

```python
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.shortcuts import render

class IPAccessMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user_ip = request.META.get('REMOTE_ADDR')
        # 미들웨어에서 허가되지 않은 사용자면 unauthorized 페이지 반환
        if user_ip not in settings.STREAMLIT_PORTS:
            return render(request, 'unauthorized.html')
        return None
```

### (4) **`templates/access_statistics.html` (옵션)**

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>접속 통계</title>
</head>
<body>
  <h2>접속 통계 페이지</h2>
  <p>추후 Django Admin 또는 별도 로직으로 통계 표시 예정</p>
</body>
</html>
```

### (5) **`templates/server_status.html` (옵션)**

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>서버 상태</title>
</head>
<body>
  <h2>서버 부하 모니터링</h2>
  <p>psutil로 CPU, 메모리 사용량 등을 표시할 수 있음.</p>
</body>
</html>
```

---

**(필요 시, "다음"이라고 해주시면 Streamlit 영역(`src/`) 코드 전체를 이어서 출력하겠습니다.)**
