---
created: 2025-03-26T16:31:07+09:00
modified: 2025-03-26T16:31:41+09:00
---

# 2025-03-26-5G Feature Manager 프로젝트 PRD

# **5G Feature Manager 프로젝트 PRD (최신 업데이트)**

## **1. 프로젝트 개요**

본 프로젝트는 기존 로컬 기반의 5G Feature 관리 도구를 Django 및 Streamlit 기반의 웹 애플리케이션으로 전환하여 접근성 및 보안성을 강화하고, 5G 프로토콜 관점에서 Feature 관리 및 비교를 효율적으로 수행할 수 있는 솔루션입니다.

---

## **2. 프로젝트 목표**

- Django 프론트엔드 도입을 통한 보안성 강화(IP 기반 사용자 인증)
- Django에서 Streamlit 앱 내부 실행 및 외부 접근 차단
- 데이터 파일을 서버에 저장하지 않고 사용자 PC에서 직접 다운로드
- CI/CD 자동화를 통한 코드 품질 관리 및 유지보수성 향상

---

## **3. 사용자 구분 및 권한**

| 사용자 유형 | IP 등록 여부 | 권한 및 접근 |
|------------|--------------|--------------|
| 관리자     | 등록된 IP (관리자용)  | 모든 기능 접근 및 관리 기능 |
| 일반 사용자 | 등록된 IP (일반용)   | 제한된 기능 접근 |
| 미등록 사용자 | 등록되지 않은 IP    | 접근 차단 |

---

## **4. 시스템 아키텍처 구성**

```
[사용자] → Django(사용자 IP 체크 및 프록시) → Streamlit(내부 Localhost 접근)
```

- Django는 외부 사용자의 IP 주소를 기반으로 인증
- 인증된 사용자에게만 Streamlit 프로세스 실행 후 접근 허용
- Streamlit 앱은 반드시 localhost에서만 접근 가능

---

## **5. 주요 기능**

| 기능 | 설명 |
|------|------|
| **IP 기반 사용자 관리** | 관리자, 일반 사용자, 미등록 사용자 3단계로 사용자 관리 |
| **Carrier Feature Generator** | NEW FORMAT 여부 확인, 파일 업로드, Feature 설정, CF JSON 파일 생성 |
| **파일 비교** | 5G 프로토콜 관점에서 Feature 지원 여부 비교 |
| **데이터 시각화** | Pandas와 matplotlib를 활용한 데이터 시각화 |

---

## **6. 폴더 구조 (최신)**

```
5G_feature_manager/
├── django_server/
│   ├── manage.py
│   ├── django_server/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   └── frontend/
│       ├── views.py
│       ├── middleware.py
│       └── templates/
│           ├── home.html
│           └── unauthorized.html
├── streamlit_app/
│   ├── src/
│   │   ├── main.py
│   │   ├── views/
│   │   └── modules/
│   └── requirements.txt
├── .github/workflows/
│   └── ci.yml
├── requirements.txt
└── README.md
```

---

## **7. 기술 스택 및 의존성**

- Python
- Django
- Streamlit
- Pandas
- psutil
- requests

---

## **8. CI/CD 자동화 (GitHub Actions)**

- 코드 품질 관리 및 배포 자동화 설정

```yaml
name: Django & Streamlit CI

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  build-and-test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install flake8 pytest
      - name: Lint
        run: flake8 .
      - name: Test
        run: pytest django_server/tests/
```

---

## **9. 실행 및 배포 방법**

- Django 서버 실행

```bash
python manage.py runserver 0.0.0.0:8000
```

- Streamlit 앱은 Django에서 자동으로 실행 (사용자가 접근 시)

---

## **10. 기대 효과 및 향후 계획**

- 명확한 IP 기반 사용자 인증과 접근 제어로 보안 강화
- 효율적인 로드밸런싱과 사용자 관리로 동시 사용자 대응
- 유지보수 용이성과 확장성을 고려한 아키텍처

| 단계 | 상태 | 내용 |
|------|------|------|
| POC 평가 | ✅ 완료 | 보안성 및 접근성 평가 |
| MVP 개발 | ⚠️ 진행 중 | 주요 기능 구현 및 테스트 |
| 사용자 테스트 | ❌ 예정 | 사용자 피드백 및 개선 |
| 제품 최적화 | ❌ 예정 | 기능 확장 및 성능 최적화 |
| 시장 출시 | 🚀 예정 | 내부 배포 및 사용자 교육 |
| 유지보수 | ❌ 예정 | 지속적인 기능 개선 및 유지보수 |
