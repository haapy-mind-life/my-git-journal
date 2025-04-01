---
created: 2025-03-26T03:10:20+09:00
modified: 2025-03-26T03:10:49+09:00
---

# 5G Feature Manager 프로젝트 PRD (최신 업데이트)

# **5G Feature Manager 프로젝트 PRD (최신 업데이트)**

## **1. 개요**

### **1.1 프로젝트 개요**

기존 로컬 기반 5G Feature 관리 도구를 **Streamlit** 기반 웹 애플리케이션으로 전환하여, 접근성 및 유지보수성을 강화하고, 5G 프로토콜 관점에서 Feature 지원 여부를 효율적으로 관리할 수 있도록 합니다.

### **1.2 목표**

- 웹 기반으로 접근성 및 협업성 향상
- 데이터 보안 강화(사용자 PC 직접 다운로드 방식)
- CI/CD 자동화를 통한 품질 관리 및 유지보수 편의성 증대

### **1.3 주요 기능**

|기능|설명|
|---|---|
|**Home**|프로젝트 개요, README, PRD 문서, GitHub 링크 제공|
|**Carrier Feature Generator**|파일 업로드(.h 파일), NEW FORMAT 체크 여부에 따른 Legacy Feature 설정, JSON 파일 생성 및 다운로드|
|**파일 비교**|업로드된 파일 기반 5G 프로토콜 Feature 지원 여부 비교|
|**데이터 시각화**|Pandas 및 matplotlib 기반 데이터 시각화|

---

## **2. 사용자 대상 및 기대 효과**

### **2.1 주요 사용자**

- 기존 로컬 툴 사용자
- 신규 웹 애플리케이션 사용자

### **2.2 기대 효과**

- 웹 기반 솔루션 제공으로 5G Feature 관리 업무 효율화
- 직관적인 UI 제공을 통해 업무 생산성 및 사용자 편의성 향상
- 데이터 파일 보안성 증대(서버에 데이터 파일 미저장)

---

## **3. 폴더 구조**

```
5G_feature_manager/
├── src/
│   ├── main.py                             # 앱 진입점 및 라우팅 처리
│   ├── views/                              # 각 기능별 페이지 구현
│   │   ├── home.py                         # Home 페이지 (README, PRD, GitHub 링크 등)
│   │   ├── carrier_feature_generator.py    # Carrier Feature Generator UI 및 로직
│   │   ├── file_comparison.py              # 파일 비교 기능
│   │   └── data_visualization.py           # 데이터 시각화
│   ├── modules/                            # 공통 기능 모듈
│   │   ├── config_loader.py                # 설정(config.yaml) 로딩
│   │   ├── security.py                     # 보안(IP 체크 및 권한 관리)
│   │   ├── visitor_log.py                  # 방문자 기록 관리
│   │   ├── json_utils.py                   # JSON 생성 유틸리티
│   │   ├── file_utils.py                   # 파일 전처리 및 파싱 유틸리티
│   │   ├── visualization.py                # 데이터 시각화 유틸리티
│   │   └── config.yaml                     # 앱 설정 관리
│   └── tests/                              # 테스트 코드
│       ├── test_json_utils.py
│       ├── test_file_utils.py
│       ├── test_visualization.py
│       ├── test_visitor_log.py
│       └── test_security.py
├── .github/workflows/
│   └── ci.yml                              # CI/CD 자동화 설정
├── requirements.txt                        # 의존성 관리
└── README.md                               # 프로젝트 설명서
```

---

## **4. CI/CD 자동화**

- GitHub Actions를 통해 코드 품질 관리 및 테스트 자동화

```yaml
name: Streamlit CI (Lint + Test)

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
        run: |
          flake8 .

      - name: Run Tests
        run: |
          pytest src/tests/
```

---

## **5. 실행 및 배포 방법**

```bash
streamlit run src/main.py --server.address 0.0.0.0 --server.port 8501
```

- Windows 환경에서 Nginx와 배포:
    ```bash
    cd C:\nginx
    start nginx
    ```

- Nginx 설정 (`C:\nginx\conf\nginx.conf`):

```nginx
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

- Windows 방화벽 설정 (TCP 80, 8501 포트 허용)

---

## **6. 일정 계획 및 향후 작업**

|단계|진행 상태|내용|
|---|---|---|
|POC 평가|✅ 완료|기능 구현 가능성 및 보안 평가|
|MVP 개발|⚠️ 진행 중|기본 UI 및 핵심 기능 구현|
|사용자 테스트|❌ 예정|실사용자 피드백 기반 개선|
|제품 최적화|❌ 예정|성능 개선 및 추가 기능|
|시장 출시|🚀 예정|내부 배포 및 사용자 교육|
|유지보수|❌ 예정|지속적 모니터링 및 기능 확장|

**우선순위**

1. MVP 기능 완성
2. 내부 테스트 및 사용자 피드백
3. 운영 환경 최적화
4. 장기 유지보수 및 기능 확장 계획
