---
created: 2025-03-28T14:00:00+09:00
modified: 2025-03-28T14:00:44+09:00
---

# Django 서버 폴더 전체 구조와 파일

아래는 최종 정리된 Django 서버 폴더(**`django_server`**)의 전체 구조와 파일들입니다.  
필요한 스켈레톤 코드와 주요 설정들을 포함하고 있습니다.

---

## **`django_server` 폴더 전체 구조 및 파일**

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
    ├── middleware.py
    ├── admin.py
    └── templates/
        ├── access_statistics.html
        └── server_status.html
```

---

### **1) `manage.py`**

기본 Django 프로젝트 실행 파일 (변경 사항 없음)

```python
#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_server.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django."
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
```

---

### **2) `requirements.txt`**

필요한 주요 패키지 목록

```
Django==5.0.3
requests==2.31.0
psutil==5.9.8
```

---

### **3) `django_server/settings.py` (중요)**

Django 기본 설정 + IP 및 포트 관리 예시 추가

```python
# settings.py (일부만 발췌)
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'frontend',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'frontend.middleware.IPCheckMiddleware',  # IP 체크 미들웨어 추가
]

# Streamlit 포트 매핑 (사용자별)
STREAMLIT_PORTS = {
    '192.168.1.100': 8500,  # 관리자
    '192.168.1.101': 8501,  # 사용자 A
    '192.168.1.102': 8502,  # 사용자 B
}

# 템플릿 경로 추가
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates', BASE_DIR / 'frontend/templates'],
        'APP_DIRS': True,
        'OPTIONS': {'context_processors': []},
    },
]

# 보안 권장 설정
ALLOWED_HOSTS = ['*']  # 운영 시 실제 호스트로 변경 필요
```

---

### **4) `django_server/urls.py`**

페이지 라우팅 설정 (핵심)

```python
from django.contrib import admin
from django.urls import path
from .views import main, admin_home

urlpatterns = [
    path('secure-admin/', admin.site.urls),  # 관리자 페이지 URL 변경
    path('', main, name='main'),  # IP 기반 리다이렉트
    path('admin_home/', admin_home, name='admin_home'),  # 관리자 홈 페이지
]
```

---

### **5) `django_server/views.py`**

메인 페이지 및 Streamlit 리다이렉트 처리

```python
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.conf import settings

def main(request):
    user_ip = request.META.get('REMOTE_ADDR')
    streamlit_ports = settings.STREAMLIT_PORTS

    if user_ip in streamlit_ports:
        port = streamlit_ports[user_ip]
        streamlit_url = f"http://{request.get_host().split(':')[0]}:{port}"
        return HttpResponseRedirect(streamlit_url)

    return render(request, 'unauthorized.html')

def admin_home(request):
    return render(request, 'admin_home.html')
```

---

### **6) `django_server/templates/unauthorized.html`**

접근 제한 페이지

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>접근 제한</title>
</head>
<body>
    <h2>🚫 접근 제한 🚫</h2>
    <p>등록되지 않은 사용자입니다. 관리자에게 문의하세요.</p>
</body>
</html>
```

---

### **7) `django_server/templates/admin_home.html`**

관리자 전용 페이지 예시

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>관리자 페이지</title>
</head>
<body>
    <h2>🛠️ 관리자 페이지 🛠️</h2>
    <p><a href="/secure-admin/">Django Admin 접속</a></p>
    <p><a href="/">Streamlit 앱 접속하기</a></p>
</body>
</html>
```

---

### **8) `frontend/models.py`**

사용자 접속 통계 및 서버 상태 저장

```python
from django.db import models

class UserAccessLog(models.Model):
    ip_address = models.GenericIPAddressField()
    access_time = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(default=0)  # 체류 시간 (초)
```

---

### **9) `frontend/middleware.py` (중요)**

IP 기반 사용자 접근 관리 미들웨어 예시

```python
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.shortcuts import render

class IPCheckMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user_ip = request.META.get('REMOTE_ADDR')
        if user_ip not in settings.STREAMLIT_PORTS:
            return render(request, 'unauthorized.html')
        return None
```

---

### **10) `frontend/admin.py`**

Django 관리자 페이지 등록 예시

```python
from django.contrib import admin
from .models import UserAccessLog

@admin.register(UserAccessLog)
class UserAccessLogAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'access_time', 'duration')
```

---

### **11) `frontend/templates/access_statistics.html` (예시)**

접속 통계 페이지 (관리자용, 실제 구현 필요)

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>접속 통계</title>
</head>
<body>
    <h2>📊 접속 통계 📊</h2>
    <p>사용자 접속 통계는 Django Admin에서 확인 가능합니다.</p>
</body>
</html>
```

---

### **12) `frontend/templates/server_status.html` (예시)**

서버 부하 모니터링 페이지 (관리자용, 실제 구현 필요)

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>서버 상태</title>
</head>
<body>
    <h2>🖥️ 서버 상태 모니터링 🖥️</h2>
    <p>서버 부하 정보는 Django Admin 페이지에서 확인 가능합니다.</p>
</body>
</html>
```

---

## 📌 **서버 실행 방법**
```bash
python manage.py runserver 0.0.0.0:8000
```

실행 후 Django가 사용자 IP 기반으로 Streamlit 앱과 자동 연동하여 동작합니다.

---

추가로 필요한 사항이나 수정이 필요한 경우 말씀해 주세요!
