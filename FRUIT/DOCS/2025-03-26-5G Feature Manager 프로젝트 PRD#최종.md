---
created: 2025-03-26T18:31:13+09:00
modified: 2025-03-26T18:31:37+09:00
---

# 2025-03-26-5G Feature Manager 프로젝트 PRD#최종

최신 내용을 반영하여 업데이트된 **PRD 문서 (최종)**를 다음과 같이 정리하여 드립니다.

---

# **5G Feature Manager 프로젝트 PRD (최종 업데이트)**

## **1. 개요**

### **1.1 프로젝트 개요**
기존 로컬 기반 5G Feature 관리 도구를 Django와 Streamlit 기반 웹 애플리케이션으로 전환하여 접근성과 유지보수성을 강화합니다. IP 기반 사용자 관리를 통해 보안성을 높이고, Streamlit 앱을 사용자별 독립 프로세스로 실행하여 효율적인 자원 관리가 가능한 구조입니다.

### **1.2 목표**
- Django 기반의 사용자(IP) 인증을 통한 접근 제한 및 보안 강화
- Streamlit 앱의 사용자별 포트 분리를 통한 자원 효율적 관리
- 데이터 파일은 서버 저장 없이 사용자 PC에 직접 저장
- CI/CD를 통한 코드 품질 관리 및 유지보수 용이성 확보

### **1.3 주요 기능**
|기능|설명|
|---|---|
|**Home (Django)**|IP 기반 자동 리다이렉트 및 접근 권한 관리|
|**Carrier Feature Generator (Streamlit)**|NEW FORMAT 체크, Legacy Feature 설정, JSON 파일 생성|
|**파일 비교 (Streamlit)**|5G 프로토콜 Feature 지원 여부 파일 비교|
|**데이터 시각화 (Streamlit)**|Pandas/Matplotlib 활용 표, 차트 등 시각화|
|**관리자 페이지 (Django)**|접속자 통계(일별/주간), 서버 부하 모니터링|

---

## **2. 사용자 대상 및 기대 효과**

### **2.1 주요 사용자**
- 기존 로컬 툴 사용자 (관리자, 일반 사용자)
- 신규 웹 애플리케이션 사용자

### **2.2 기대 효과**
- 웹 기반 통합 솔루션으로 접근성 및 생산성 향상
- IP 기반 사용자 관리로 보안성 및 관리 용이성 증대
- 독립된 Streamlit 프로세스로 안정성 및 리소스 효율성 증가

---

## **3. 최종 폴더 구조**

```
5G_feature_manager/
├── django_server/
│   ├── manage.py
│   ├── django_server/
│   │   ├── settings.py        # IP 기반 사용자 및 포트 관리
│   │   ├── urls.py            # 페이지 라우팅
│   │   ├── views.py           # 메인 페이지 및 리다이렉트 처리
│   │   └── templates/
│   │       ├── home.html
│   │       └── unauthorized.html
│   └── frontend/
│       ├── models.py          # 사용자 세션 및 로그 관리
│       ├── middleware.py      # IP 기반 사용자 인증 미들웨어
│       ├── admin.py           # 관리자 페이지 설정
│       └── templates/
│           ├── server_status.html
│           └── access_statistics.html
├── streamlit_app/
│   ├── main.py                # Streamlit 앱 진입점
│   ├── views/
│   │   ├── home.py
│   │   ├── carrier_feature_generator.py
│   │   ├── file_comparison.py
│   │   └── data_visualization.py
│   ├── modules/
│   │   ├── config_loader.py
│   │   ├── security.py
│   │   ├── visitor_log.py
│   │   ├── json_utils.py
│   │   ├── file_utils.py
│   │   ├── visualization.py
│   │   └── config.yaml
│   └── tests/
│       ├── test_json_utils.py
│       ├── test_file_utils.py
│       ├── test_visualization.py
│       └── test_security.py
├── .github/workflows/
│   └── ci.yml                 # CI/CD 자동화 설정
├── requirements.txt           # 프로젝트 의존성 관리
└── README.md                  # 프로젝트 설명서
```

---

## **4. 서버 구성 및 세션 관리**

### 4.1 사용자 구분 (IP 기반)
- **관리자**: 모든 접근 가능, 관리자 페이지 접근 허용
- **일반 사용자**: Streamlit 앱으로 바로 연결
- **미등록 사용자**: 접근 제한 페이지 표시

### 4.2 사용자별 Streamlit 포트 관리
| 사용자 | IP 주소 예시 | Streamlit 포트 |
|---|---|---|
| 관리자 | 192.168.1.100 | 8500 |
| 사용자 A | 192.168.1.101 | 8501 |
| 사용자 B | 192.168.1.102 | 8502 |
| 사용자 C | 192.168.1.103 | 8503 |

- Django에서 IP 확인 후 해당 사용자 포트로 리다이렉트하여 연결

### 4.3 세션 관리 방식
- Django 세션: 쿠키 기반 관리 (브라우저 종료 시 만료 가능)
- Streamlit 세션: 브라우저 탭 종료 시 초기화
- 세션 만료 시 사용자는 메인 페이지로 다시 리다이렉트 및 초기 상태로 재접속
- 데이터 유지는 필요 시 DB 또는 파일로 별도 저장 관리 가능

---

## **5. 보안 점검 및 권장 사항**

| 보안 항목 | 현황 | 권장 사항 |
|---|---|---|
|IP 기반 인증|적용|추가 인증(비밀번호, OTP 등) 권장|
|Streamlit 앱 접근 제한|적용|내부 접근(localhost)만 허용, 외부 방화벽 차단 필수|
|관리자 페이지 보호|적용|관리자 URL 변경, 강력한 비밀번호 정책 적용|
|SSL/TLS(HTTPS)|미적용|SSL 인증서 적용 필수|
|서버 소프트웨어 최신 업데이트|필수|정기적 업데이트 및 패치 관리|

---

## **6. CI/CD 자동화**

GitHub Actions를 활용한 코드 품질 관리 및 자동 테스트:

```yaml
name: Django + Streamlit CI (Lint + Test)

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
      - name: Checkout repository
        uses: actions/checkout@v2

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install flake8 pytest

      - name: Run Lint
        run: flake8 .

      - name: Run Tests
        run: pytest streamlit_app/tests/
```

---

## **7. 실행 및 배포 방법**

### 7.1 Django 서버 실행 (24시간 자동 실행)
- Windows 작업 스케줄러를 통한 자동 실행  
- NSSM을 통한 서비스 등록 및 관리 권장

### 7.2 Streamlit 앱 실행
- 사용자 접속 시 자동 실행 (Django 프록시 접근 방식)
- 외부에서 직접 접근 차단, 내부 localhost에서만 바인딩

---

## **8. 일정 계획 및 향후 작업**

| 단계 | 진행 상태 | 내용 |
|---|---|---|
| POC 평가 | ✅ 완료 | 프로젝트 가능성 및 기술적 검토 완료 |
| MVP 개발 | ⚠️ 진행 중 | 주요 기능 구현 및 최적화 중 |
| 사용자 테스트 | ❌ 예정 | 사용자 피드백 수집 및 개선 |
| 제품 최적화 | ❌ 예정 | 성능 최적화 및 보안 강화 |
| 내부 배포 | 🚀 예정 | 내부 서버 환경 배포 및 교육 |
| 유지보수 | ❌ 예정 | 지속적인 관리 및 기능 추가 |

### **우선순위**
1. MVP 완성 및 내부 테스트
2. 보안 강화 및 사용자 추가 인증 도입
3. SSL/TLS(HTTPS) 적용
4. 사용자 피드백 기반의 지속적인 기능 개선 및 유지보수

---

추가적인 요청 사항이나 수정할 부분이 있다면 언제든지 말씀해 주세요!
