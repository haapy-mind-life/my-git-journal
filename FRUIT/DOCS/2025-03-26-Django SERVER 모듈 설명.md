---
created: 2025-03-26T16:46:04+09:00
modified: 2025-03-26T16:46:36+09:00
---

# 2025-03-26-Django SERVER 모듈 설명

아래는 최신 PRD 기준으로 **Django SERVER 모듈**의 구성과 동작 방식을 설명하고, 데스크탑(윈도우 OS)을 24시간 자동 서버로 운영하기 위한 실질적인 가이드를 제공합니다.

---

## **Django SERVER 모듈 구성 및 동작 방식 설명**

### 1. 모듈 구성 (최신 PRD 기준)

```
django_server/
├── manage.py
├── django_server/
│   ├── settings.py (사용자 IP 및 포트 설정)
│   ├── urls.py (경로 설정 및 라우팅)
│   ├── wsgi.py
│   └── asgi.py
└── frontend/
    ├── views.py (사용자 관리 및 Streamlit 프록시 관리)
    ├── middleware.py (IP 기반 사용자 인증)
    └── templates/
        ├── home.html (메인 페이지)
        └── unauthorized.html (미등록 사용자 접근 제한 페이지)
```

### 2. 주요 기능

- **IP 기반 사용자 관리**:
  - 관리 IP 목록에서 사용자 인증 및 권한 부여(관리자, 사용자, 미등록)
  - 관리자 및 일반 사용자에게만 Streamlit 앱 접근 허용
  - 미등록 사용자는 접근 제한
  
- **Streamlit 앱 실행 관리 (내부 접근)**:
  - 사용자가 Django에 접속하면 해당 IP에 맞는 Streamlit 앱을 자동 실행
  - Streamlit 앱은 외부 접근이 차단되고 Django에서만 접근 가능(`localhost` 바인딩)

### 3. 주요 기술 스택

- Django (프론트엔드 서버 및 사용자 인증 관리)
- Streamlit (내부에서 실행되는 데이터 시각화 및 분석 앱)
- psutil (서버 프로세스 관리)
- requests (Django ↔ Streamlit 내부 프록시 통신)

---

## **Windows OS에서 Django 서버를 24시간 자동 실행 방법**

아래 방법으로 파트너 및 내부 직원이 안정적으로 서버를 사용할 수 있게 설정합니다.

### **방법 1. Windows 작업 스케줄러(Task Scheduler) 이용 (추천)**

Windows 작업 스케줄러를 이용하여 시스템 부팅 시 Django 서버를 자동 실행할 수 있습니다.

**설정 방법**:

1. **스크립트 파일 작성 (`run_server.bat`)**

   바탕화면 또는 프로젝트 폴더에 배치 파일을 생성합니다.

   ```batch
   @echo off
   cd C:\your_project\django_server
   python manage.py runserver 0.0.0.0:8000
   ```

2. **작업 스케줄러 설정**  
   - "작업 스케줄러" 앱을 열고, "기본 작업 만들기"를 클릭합니다.
   - 이름: `DjangoServer`, 트리거: `컴퓨터 시작 시`, 동작: `프로그램 시작`
   - 프로그램 경로에 위에서 만든 `run_server.bat` 파일을 지정합니다.
   - 설정에서 "가장 높은 수준의 권한으로 실행" 체크를 설정해 주세요.

3. **설정 완료 후**  
   - 시스템 부팅 시 자동으로 Django 서버가 실행됩니다.

---

### **방법 2. NSSM (Non-Sucking Service Manager)를 이용한 서비스 등록 (추천)**

NSSM은 Windows에서 간편하게 Python 앱을 시스템 서비스로 등록하는 도구입니다.

1. **NSSM 다운로드**  
   [NSSM 공식 홈페이지](https://nssm.cc/download)에서 최신 버전을 다운로드 후 압축 해제합니다.

2. **NSSM을 이용한 Django 서버 등록**

   관리자 권한으로 명령 프롬프트를 열고 다음을 실행:

   ```batch
   cd C:\path_to_nssm\nssm.exe
   nssm install DjangoServer
   ```

   NSSM GUI 창에서 다음과 같이 설정:

   - **Path**: `C:\Python311\python.exe` (본인의 Python 경로 지정)
   - **Startup directory**: `C:\your_project\django_server`
   - **Arguments**: `manage.py runserver 0.0.0.0:8000`

3. **서비스 시작**
   ```batch
   nssm start DjangoServer
   ```

4. **서비스 관리**  
   윈도우 서비스 창(`services.msc`)에서 "DjangoServer"를 시작/중지 및 상태 확인 가능합니다.

---

## **안정적인 운영 및 유지보수 방법**

- **자동 재시작 설정**  
  서비스가 중단되는 경우 자동 재시작 옵션을 서비스 설정에서 활성화하세요.

- **서버 부하 관리**  
  최대 동시 사용자 5명 이내, 최대 20명의 사용자가 접근하는 환경이라면  
  별도의 로드밸런싱 없이 Django의 내장 서버로도 안정적인 운영이 가능합니다.  
  장기적으로 사용자가 증가하면 Apache나 Nginx 등 웹서버와 WSGI 모듈(gunicorn 등)을 고려하세요.

---

## **추천 서버 스펙 (파트너 사용 목적 기준)**

| 항목 | 권장 사양 |
|------|-----------|
| CPU  | Intel Core i5 이상 |
| RAM  | 8GB 이상 |
| SSD  | 256GB 이상 |
| OS   | Windows 10/11 |

---

## **결론 및 기대효과**

- **Django 서버 모듈**을 활용하여 IP 기반 사용자 관리 및 보안성을 강화
- Windows OS 기반 데스크탑을 이용한 24시간 안정적 운영 환경 구축
- NSSM 또는 Windows 작업 스케줄러를 통한 자동 서버 구동으로 유지보수 간소화
- 중소규모 사용자 환경(최대 동시 사용자 5명, 최대 사용자 20명)에서 효율적으로 운영 가능

추가적으로 필요한 부분이나 질문 있으시면 언제든 말씀해 주세요!
