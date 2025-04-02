---
created: 2025-04-02T12:18:34+09:00
modified: 2025-04-02T12:19:05+09:00
---

# 2025-04-02-Django SERVER 모듈 상세 설명

# Django SERVER 모듈 상세 설명

## 1. 프로젝트 구조

```
django_server/
├── manage.py
├── requirements.txt
├── django_server/
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   └── templates/
│       ├── admin_home.html
│       └── unauthorized.html
└── frontend/
    ├── models.py
    ├── admin.py
    ├── middleware.py
    └── templates/
        ├── access_statistics.html
        └── server_status.html
```

## 2. 주요 파일 설명

### 2.1 manage.py
Django 프로젝트 관리 명령어 실행 파일

### 2.2 settings.py
프로젝트 설정 파일
- IP 기반 사용자 접근 관리
- 사용자별 Streamlit 포트 매핑

```python
STREAMLIT_PORTS = {
    '192.168.1.100': 8500,  # 관리자
    '192.168.1.101': 8501,
    '192.168.1.102': 8502,
}
```

### 2.3 urls.py
URL 라우팅 설정

### 2.4 views.py
사용자 IP 확인 후 접근 권한 관리 및 Streamlit 포트로 리다이렉트

### 2.5 templates/
- admin_home.html: 관리자 홈 화면
- unauthorized.html: 미허가 사용자 접근 차단 페이지

### 2.6 middleware.py
사용자 IP 주소 기반 접근 관리 미들웨어

## 3. 서버 부하 관리
- 프로덕션 환경에서는 Waitress와 Nginx를 사용하여 서버 운영 권장

### 3.1 Waitress 역할
- Python 애플리케이션을 실행할 때 사용하는 서버 (WSGI 서버)
- Django 애플리케이션을 실제로 실행하고 사용자 요청 처리

### 3.2 Nginx 역할
- 사용자의 요청을 처음 받아들이는 웹 서버 (리버스 프록시)
- 정적 파일을 빠르게 제공
- 사용자의 요청을 Waitress로 전달하고, Waitress의 응답을 다시 사용자에게 전달

## 4. Django에서 Streamlit으로 직접 리다이렉트
Django에 연결된 사용자를 IP 주소에 따라 바로 Streamlit 포트로 리다이렉트 가능

### 작동 원리 및 네트워크 과정 설명:
- 사용자가 웹브라우저로 서버 접속 시 Nginx가 처음 요청을 받음
- Nginx는 요청을 Waitress가 구동 중인 Django 서버로 전달
- Django 서버의 `views.py`에서 사용자 IP 주소 확인 후, Streamlit 포트 번호 결정
- HTTP 리다이렉트(response 302)를 통해 웹브라우저가 자동으로 해당 사용자의 Streamlit 포트 주소로 다시 요청
- 사용자는 리다이렉트된 주소에서 직접 Streamlit 애플리케이션과 상호작용 가능

## 5. 실행 방법

### Django 서버 실행 (Waitress 사용)
```bash
cd django_server
python manage.py makemigrations
python manage.py migrate
waitress-serve --listen=*:8000 django_server.wsgi:application
```

### Nginx 설정 (예시)

```nginx
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 6. 보안 관련 권장 사항
- SSL/TLS 적용 (HTTPS)
- 방화벽을 통한 외부 접근 차단
- 관리자 페이지 강력한 비밀번호 설정 및 접근 제한
