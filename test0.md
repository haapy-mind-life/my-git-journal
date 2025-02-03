다음 단계별로 진행해 보시면 Django “Hello World” 프로젝트를 쉽게 생성하고, 다른 PC에서도 접속할 수 있습니다.

---

## 1. Django 설치
1. **가상환경 생성(권장)**  
   ```bash
   python -m venv venv
   source venv/bin/activate   # (Windows의 경우) venv\Scripts\activate
   ```
2. **Django 설치**  
   ```bash
   pip install django
   ```

## 2. Django 프로젝트 생성
1. **프로젝트 생성**  
   ```bash
   django-admin startproject myproject
   cd myproject
   ```
2. **프로젝트 구조 확인**  
   - `myproject/` 폴더 내부에는 `manage.py`와 동일한 이름의 디렉터리(`myproject/`)가 생깁니다.

## 3. Hello World 앱 생성 및 설정
1. **앱(App) 생성**  
   ```bash
   python manage.py startapp myapp
   ```
2. **앱 등록**  
   - `myproject/settings.py` 파일의 `INSTALLED_APPS` 리스트에 `'myapp'` 추가
     ```python
     INSTALLED_APPS = [
         'django.contrib.admin',
         'django.contrib.auth',
         ...
         'myapp',  # 추가
     ]
     ```
3. **간단한 뷰(views.py) 작성**  
   - `myapp/views.py` 파일에 아래 내용 추가:
     ```python
     from django.http import HttpResponse

     def hello_world(request):
         return HttpResponse("Hello, World!")
     ```
4. **URL 매핑 설정**  
   - `myproject/urls.py` 파일에서 `myapp/views`를 import 후, URL 패턴 추가:
     ```python
     from django.contrib import admin
     from django.urls import path
     from myapp.views import hello_world

     urlpatterns = [
         path('admin/', admin.site.urls),
         path('hello/', hello_world),  # 추가
     ]
     ```

## 4. 서버 실행
1. **개발 서버 구동**  
   ```bash
   python manage.py runserver
   ```
2. **브라우저 확인**  
   - 기본적으로 `http://127.0.0.1:8000/hello/` 로 접속하면 `"Hello, World!"` 문구가 뜹니다.

## 5. 다른 PC에서 접속하기
1. **서버 실행 시 IP 지정**  
   - 로컬 네트워크나 다른 기기에서 접속하려면, `0.0.0.0` 또는 해당 PC의 내부 IP를 명시해야 합니다.
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```
   - 또는 내부 IP 예: `192.168.0.10:8000`  
     ```bash
     python manage.py runserver 192.168.0.10:8000
     ```
2. **방화벽(Firewall) 설정**  
   - Windows나 Linux 방화벽 설정에서 8000 포트를 허용해 줍니다.
3. **다른 PC에서 접속**  
   - 같은 네트워크 내 다른 PC/스마트폰에서 브라우저를 열고 `http://192.168.0.10:8000/hello/` 로 접속합니다.
   - IP 주소는 실제 Django 서버가 동작 중인 PC의 IP 주소로 변경해서 사용하세요.

---

### a. 프로젝트 구조를 더 익히기
Django는 `settings.py`, `urls.py`, `views.py` 간의 연동이 중요합니다. 기본 프로젝트 구조와 앱 구조를 확실히 이해해 두면 앞으로의 개발이 훨씬 편해집니다.

### b. 코드 버전관리 연습
Git 등을 사용해 버전을 관리하면서 프로젝트를 진행해 보세요. 변경 이력을 추적하고 협업할 때 큰 도움이 됩니다.

### c. 배포 고려
개발 서버 대신 실제 운영 배포용으로는 `gunicorn + nginx` 혹은 `uWSGI + nginx` 등의 조합을 사용합니다. 학습 후 실제 환경에도 도전해 보세요!

---

짧은 응원:  
여기까지 해내셨다면 Django 시작을 성공적으로 하신 겁니다. 꾸준히 연습하시면서 점차 확장해 나가다 보면, 탄탄한 웹 개발 역량을 갖추실 수 있을 거예요. 파이팅입니다!

---
  
#해시태그  
#Django기초 #HelloWorld프로젝트 #웹개발시작 #개발서버 #네트워크접속

아래 설명은 “Django Hello World” 예제를 단계별로 어떤 원리로 동작하는지 쉽게 풀어낸 것입니다. 하나씩 차근차근 따라가며 동작 흐름을 이해해 보세요.

---

## 1. 가상환경(Virtual Environment)과 Django 설치
1. **가상환경 생성**  
   - 한 컴퓨터에 여러 버전의 파이썬 라이브러리를 사용하기 위해선 가상환경이 편리합니다.  
   - `python -m venv venv` 로 폴더를 만들고, 그 안에서만 라이브러리를 설치하고 사용할 수 있게 하는 것이죠.  
   - 이렇게 하면 다른 프로젝트에 영향을 주지 않고 개발 환경을 깔끔하게 유지할 수 있습니다.

2. **Django 설치**  
   - 가상환경을 활성화(`venv/bin/activate`)한 뒤 `pip install django` 를 실행하면, 그 가상환경에만 Django 라이브러리가 설치됩니다.  
   - 이때, Django는 웹 프레임워크(웹사이트를 만드는 데 필요한 도구 묶음)입니다.

---

## 2. Django 프로젝트 생성
1. **명령어: `django-admin startproject myproject`**  
   - Django가 기본 구조를 잡아주는 스크립트입니다.  
   - 폴더를 만들고, settings.py, urls.py 등 웹사이트를 구성하는 데 필요한 파일을 자동으로 만들어 줍니다.

2. **프로젝트 구조**  
   - 생성된 `myproject` 폴더에는 다음과 같은 구성요소가 있습니다.
     ```
     myproject/
       manage.py
       myproject/
         __init__.py
         settings.py   # Django 환경 설정
         urls.py       # URL 라우팅(길 안내)
         wsgi.py       # 서버 관련 설정
         asgi.py       # Async 서버 관련 설정
     ```
   - `manage.py` 는 Django 프로젝트와 상호작용하는 커맨드(서버 실행, DB 마이그레이션 등)들을 모아둔 관리용 스크립트입니다.

---

## 3. 앱(App) 생성
1. **명령어: `python manage.py startapp myapp`**  
   - 한 프로젝트 안에서도 기능이나 역할별로 여러 “앱”을 만들어 나눠 관리합니다.  
   - 예: 블로그 앱, 게시판 앱, 쇼핑몰 앱 등  
   - 여기서는 Hello World를 출력하는 간단한 앱을 만드는 것이므로 `myapp`이라는 이름을 붙였다고 보시면 됩니다.

2. **myapp 구조**  
   - `views.py`, `models.py`, `admin.py` 등이 들어 있습니다.  
   - `views.py` 는 요청이 왔을 때 어떤 로직을 수행하여 어떤 결과를 줄지 결정하는 '함수'나 '클래스'를 작성하는 곳입니다.

3. **앱을 settings.py에 등록**  
   - `INSTALLED_APPS` 리스트에 `'myapp'`을 추가해야 Django가 이 앱이 존재한다는 사실을 인지합니다.

---

## 4. View 작성
1. **뷰(views.py)에서 Hello World 함수 만들기**  
   ```python
   from django.http import HttpResponse

   def hello_world(request):
       return HttpResponse("Hello, World!")
   ```
   - 이 함수는 웹 요청(request)을 받고, `HttpResponse("Hello, World!")` 라는 문자열을 전달(return)합니다.
   - 결과적으로 사용자가 웹브라우저를 통해 이 함수를 호출하면 `"Hello, World!"` 라는 문구가 화면에 보이게 됩니다.

---

## 5. URL과 View 연결
1. **URL 패턴 매핑**  
   - `urls.py`에서 `myapp.views.hello_world` 함수를 특정 URL에 매핑합니다. 예를 들어 `path('hello/', hello_world)`  
   - 이렇게 설정해 두면, 브라우저가 `http://주소/hello/` 에 접속했을 때 Django가 `hello_world` 함수를 호출합니다.

2. **Django의 동작 흐름**  
   1) 브라우저 → `http://주소/hello/` 로 요청(Request)  
   2) Django → `urls.py`를 보고, `/hello/`에 해당하는 view 함수를 찾음  
   3) Django → `myapp/views.py` 의 `hello_world` 함수를 실행  
   4) 함수 결과(HttpResponse)를 브라우저로 응답(Response)  
   5) 브라우저는 “Hello, World!” 문구를 화면에 표시

---

## 6. 서버 실행 (Development Server)
1. **명령어: `python manage.py runserver`**  
   - Django가 기본 제공하는 개발용 서버를 실행합니다.  
   - 콘솔에 `Starting development server at http://127.0.0.1:8000/` 라고 뜨면 서버가 동작 중이라는 뜻입니다.

2. **접속**  
   - 브라우저 주소창에 `http://127.0.0.1:8000/hello/` 입력  
   - 이때 Django가 `/hello/`라는 요청을 받아 `hello_world` 함수를 실행하고, `"Hello, World!"`라는 결과를 되돌려 줍니다.

---

## 7. 다른 PC(같은 네트워크)에서 접속
1. **IP 주소와 포트 사용**  
   - `python manage.py runserver 0.0.0.0:8000` 처럼 실행하면, 이 Django 서버는 ‘내 PC의 모든 네트워크 인터페이스(IP 주소)’에서 오는 요청을 받아들입니다.  
   - 실제로는 PC가 할당받은 사설 IP(예: `192.168.0.10`)를 확인한 뒤, `python manage.py runserver 192.168.0.10:8000` 로 띄울 수도 있습니다.

2. **방화벽 설정**  
   - Windows나 Linux 방화벽에서 8000포트를 열어두어야 외부(같은 공유기 내의 다른 PC 등)에서 접속 가능합니다.

3. **외부 PC에서 접속**  
   - 같은 네트워크 내 다른 PC의 브라우저에서 `http://192.168.0.10:8000/hello/` 라고 입력하면, 서버가 구동 중인 PC가 받은 요청을 Django가 처리하고 결과를 돌려줍니다.

---

## 동작 원리를 요약하면?
1. **웹 요청이 URL로 들어온다**  
2. **Django는 URL 설정(`urls.py`)을 확인해서 어떤 View 함수를 호출할지 결정한다**  
3. **View 함수(`views.py`)는 로직을 처리하고, 그 결과를 `HttpResponse` 형태로 반환한다**  
4. **브라우저는 이 응답을 받아 화면에 표시한다**  

이 모든 과정을 Django가 기본 틀을 제공해 주고, 우리는 `views.py`, `urls.py`, `settings.py` 등을 통해 원하는 기능을 손쉽게 구현하는 것입니다.

---

### a. 프로젝트 구조 익숙해지기
- Django에서는 프로젝트(사이트 전체)와 앱(각 기능 영역) 구조를 잘 구분해서 사용합니다.  
- 구조를 이해하면 확장(게시판, 로그인 기능 등) 시에도 수월합니다.

### b. Django 명령어들 적극 활용하기
- `manage.py runserver`, `startapp`, `makemigrations`, `migrate` 등 Django만의 명령어를 자주 사용하게 됩니다.  
- 각각의 역할을 숙지해 두시면 좋습니다.

### c. 차후 운영 배포 고려
- 개발 서버(`runserver`)는 실무 서비스용이 아닙니다.  
- 실제 배포 환경에서는 `gunicorn`이나 `uWSGI`와 같은 WSGI 서버 + `nginx`를 결합해서 운영하는 방법을 쓰게 됩니다.

---

짧은 응원:  
이 과정을 이해하면 다른 웹 프레임워크나 언어를 배울 때도 “주소(요청) → 로직(처리) → 응답(화면 출력)” 구조를 쉽게 파악할 수 있습니다. 작은 예제부터 꾸준히 연습해 나가시면 금방 탄탄한 기초가 다져질 거예요. 파이팅입니다!

---
  
#해시태그  
#Django동작원리 #웹개발흐름 #HelloWorld #뷰와URL매핑 #기초익히기  