---
created: 2025-04-01T15:18:57+09:00
modified: 2025-04-01T15:19:19+09:00
---

# 2025-03-31-5G Feature Manager 프로젝트 PRD

아래는 지금까지의 **최신 구현 사항**과 **메뉴 구성**, **파일 업로드 정책** 등을 반영한 **최종 PRD 문서**입니다.  
(이전 문서를 기반으로 수정/추가된 사항을 모두 포함.)

---

# **5G Feature Manager 프로젝트 PRD (최종 업데이트)**

## **1. 개요**

### 1.1 프로젝트 개요

- 기존 **로컬 기반**의 5G Feature 관리 도구를 **Django + Streamlit 웹 애플리케이션** 형태로 전환  
- **IP 기반 사용자 인증**(Django) + **사용자별 독립 Streamlit 앱**(포트 매핑) → 보안과 접근성 강화  
- **Legacy Format** vs **New Format**에 맞춰 **파일 업로드/피처 설정** 로직을 유연하게 제공

### 1.2 목표

- **보안성**: IP 인증 + 내부 프로세스 분리로 안전한 운영  
- **유연성**: Legacy vs New Format 분기, 파일 업로드 필요 여부  
- **데이터 무결성**: 파일은 서버에 저장하지 않고, 사용자 PC나 세션 상태에서만 관리  
- **확장성**: CI/CD, 추가 기능(파일 비교, 시각화 등) 손쉽게 확장

---

## **2. 주요 기능**

| 기능                                | 설명                                                               |
|------------------------------------|--------------------------------------------------------------------|
| **Home**                           | 프로젝트 소개, 사용 방법 안내, 풍선 애니메이션(선택)                |
| **Legacy Allow List 업로드**       | Legacy Allow List 파일(.txt/.h) 업로드/파싱. DF 표시 및 추가 처리   |
| **Carrier Feature Generator**       | - **New Format**: ALLOW/BLOCK + ADD/REMOVE<br>- **Legacy Format**: 파일 업로드 필수, ALLOW/BLOCK + ENABLE/DISABLE |
| **파일 비교**                      | 5G 프로토콜 Feature 지원 여부 비교 (추후 확장)                      |
| **데이터 시각화**                  | Pandas/Chart로 시각화 (추후 확장)                                   |

---

## **3. 폴더 구조 (최종)**

```
5G_feature_manager/
├── src/                            # Streamlit 앱
│   ├── main.py                     # 메뉴 구성 및 실행
│   ├── views/
│   │   ├── home.py                 # 홈 (사용 방법 안내)
│   │   ├── legacy_allow_list.py    # Legacy Allow List 업로드
│   │   ├── carrier_feature_generator.py  # CF 생성기
│   │   ├── file_comparison.py      # 파일 비교
│   │   └── data_visualization.py   # 데이터 시각화
│   ├── modules/
│   │   ├── config_loader.py
│   │   ├── security.py
│   │   ├── visitor_log.py
│   │   ├── json_utils.py
│   │   ├── file_utils.py
│   │   └── config.yaml             # 메뉴 설정, 관리자 IP 등
│   └── tests/
│       ├── test_json_utils.py
│       ├── test_file_utils.py
│       ├── test_visualization.py
│       └── test_security.py
├── django_server/                   # Django 서버
│   ├── manage.py
│   ├── requirements.txt
│   ├── django_server/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── templates/
│   │       ├── unauthorized.html
│   │       └── admin_home.html
│   └── frontend/
│       ├── models.py
│       ├── admin.py
│       ├── middleware.py
│       └── templates/
│           ├── access_statistics.html
│           └── server_status.html
├── .github/workflows/
│   └── ci.yml                      # CI/CD 설정
└── README.md
```

---

## **4. 메뉴 구성 & 동작 흐름 (Streamlit)**

**Side Menu** (config.yaml):
1) **Home** (Home 화면)
2) **Legacy Allow List 업로드** (파일 업로드 .txt/.h)
3) **Carrier Feature Generator** (NEW vs LEGACY)
4) **파일 비교**
5) **데이터 시각화**

사용자는 **메뉴**를 통해 각 기능 페이지로 이동.

---

## **5. Carrier Feature Generator 상세**

- **NEW FORMAT**  
  - 파일 업로드 **불필요**  
  - **MODE**: ALLOW LIST / BLOCK LIST  
  - **VALUE**: ADD / REMOVE

- **LEGACY FORMAT**  
  - 파일 업로드 **필수**  
  - 파일 미업로드 시 **오류** 및 안내 팝업  
  - **MODE**: ALLOW LIST / BLOCK LIST  
  - **VALUE**: ENABLE / DISABLE

- **OMC VERSION**: 입력  
- **MCC_MNC**: 입력  
- **피처 설정**: checkbox 활성 → selectbox(모드/값)  
- **CF JSON 생성**: `create_cf_json()` → 다운로드

---

## **6. Legacy Allow List 업로드**

- **파일 업로드 & 파싱**  
  - `.txt` / `.h` 등 확장자 지원  
  - 업로드 성공 시 `DataFrame` 표시  
  - 필요 시 `session_state` 저장 또는 DB 저장  
- **Carrier Feature Generator**에서 필요 시 session_state로 연계 가능

---

## **7. 파일 업로드 로직 통합 (file_utils.py)**

- **`upload_and_parse_file()`**:  
  - `file_uploader` + 파싱 → DataFrame 반환  
  - 실패 시 오류 메시지 반환  
- 각 기능 모듈(`carrier_feature_generator.py`, `legacy_allow_list.py`)에서 이를 호출

---

## **8. Django 서버 (보안 및 접근)**

- **IP 기반**:  
  - `settings.py` → `STREAMLIT_PORTS` 딕셔너리  
  - `middleware.py` → 사용자 IP 확인  
    - 등록된 IP 아니면 **unauthorized.html** 표시  
    - 등록된 IP면 Streamlit 포트로 **리다이렉트**  
- **관리자**: `secure-admin/` 페이지(장고 관리자)로 접속, `admin_home.html` 등 추가 기능

---

## **9. 실행 방법**

1. **Django 서버**  
   ```bash
   cd django_server
   python manage.py makemigrations
   python manage.py migrate
   python manage.py runserver 0.0.0.0:8000
   ```
   - 브라우저 → `http://[서버IP]:8000` → IP 인증 후 Streamlit 포트 리다이렉트

2. **Streamlit**  
   ```bash
   cd ../src
   streamlit run main.py --server.port=8501
   ```
   - 여러 사용자 IP별 포트를 할당할 경우, Django에서 라우팅 가능

---

## **10. 보안 및 권장 사항**

- **SSL/TLS** 적용 (HTTPS)  
- Windows 방화벽으로 외부에서 Streamlit 포트 직접 접근 차단 (Django 통해서만 접근)  
- 관리자 페이지 보호 (강력한 비밀번호, IP 제한)  
- session_state는 사용자별 브라우저 세션에 종속 → 영구 저장은 DB 등 별도 방안 고려

---

## **11. 향후 일정**

| 단계             | 상태        | 내용                                                    |
|------------------|------------|---------------------------------------------------------|
| POC 평가         | ✅ 완료     | 보안성 및 기능 검토                                      |
| MVP 개발         | ⚠️ 진행 중  | 새 메뉴(Allow List) + CF 생성기 NEW/LEGACY 분기 구현 중  |
| 사용자 테스트    | ❌ 예정     | 실제 사용자 피드백 및 개선                                |
| 제품 최적화      | ❌ 예정     | UI/UX 다듬기, 성능 최적화, 보안 강화                      |
| 내부 배포        | 🚀 예정     | Windows 서버에 상시 실행, 담당자 교육                    |
| 유지보수         | ❌ 예정     | 지속적 모니터링 및 기능 확장 (파일 비교 개선 등)         |

---

# **결론**

- **Django**: IP 인증 + 관리자 페이지  
- **Streamlit**: 메뉴(5개 항목) 및 Legacy/New Format 분기, 파일 업로드 로직 통합  
- **Legacy Allow List 업로드**:  
  1) 파일 업로드 & 파싱  
  2) Carrier Feature Generator에서 사용할 수 있음  
- **NEW FORMAT**: 파일 없이 ALLOW/BLOCK + ADD/REMOVE  
- **LEGACY FORMAT**: 파일 업로드 필수 + ALLOW/BLOCK + ENABLE/DISABLE  

이 **최종 PRD**를 참고하여, 해당 구조를 토대로 **보안성이 높고 유지보수하기 편리한** 5G Feature Manager 서비스를 운영할 수 있습니다.
