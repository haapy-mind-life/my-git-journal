---
created: 2025-03-26T03:18:58+09:00
modified: 2025-03-26T03:19:15+09:00
---

# home.py

다음은 **최신 버전의 `home.py`** 파일 코드입니다.

이 페이지는 프로젝트의 주요 정보(README, PRD, GitHub 링크 등)를 제공하여 사용자가 프로젝트 개요 및 관련 문서를 쉽게 접근할 수 있도록 합니다.

---

## home.py (최신 업데이트)

```python
import streamlit as st

def run(is_admin=False):
    st.title("🏠 5G Feature Manager")

    st.markdown("""
    **환영합니다!**  
    이 애플리케이션은 기존 로컬 기반의 5G Feature 관리 도구를  
    웹 기반으로 전환한 통합 관리 솔루션입니다.
    """)

    st.markdown("---")

    # 프로젝트 정보 섹션
    st.subheader("📌 프로젝트 정보")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 📖 README")
        st.markdown("[프로젝트 README](https://github.com/yourusername/5G_feature_manager#readme)", unsafe_allow_html=True)

    with col2:
        st.markdown("### 📚 PRD 문서")
        st.markdown("[프로젝트 요구사항 정의서(PRD)](https://yourlink_to_prd_document.com)", unsafe_allow_html=True)

    with col3:
        st.markdown("### 💻 GitHub Repo")
        st.markdown("[GitHub 저장소](https://github.com/yourusername/5G_feature_manager)", unsafe_allow_html=True)

    st.markdown("---")

    # 프로젝트 목표
    st.subheader("🎯 프로젝트 목표")
    st.markdown("""
    - 기존 로컬 툴의 웹 기반 전환
    - 사용자 데이터 파일 보안성 강화 (사용자 PC에 직접 저장)
    - CI/CD를 통한 코드 품질 관리
    - 사용하기 쉽고 직관적인 UI 제공
    """)

    # 향후 계획
    st.markdown("---")
    st.subheader("📅 향후 계획")

    st.markdown("""
    | 단계             | 상태        | 내용                                   |
    |------------------|-------------|----------------------------------------|
    | POC 평가         | ✅ 완료     | 프로젝트 가능성 평가 및 보안성 검토     |
    | MVP 개발         | ⚠️ 진행 중  | 주요 기능 구현 및 테스트               |
    | 사용자 테스트    | ❌ 예정     | 사용자 피드백 수렴 및 UX 개선           |
    | 제품 최적화      | ❌ 예정     | 추가 기능 확장 및 성능 최적화          |
    | 시장 출시        | 🚀 예정     | 내부 배포 및 사용자 교육               |
    | 유지보수         | ❌ 예정     | 지속적인 기능 확장 및 개선             |
    """)

    st.markdown("---")

    # 관리자 전용 기능 (옵션)
    if is_admin:
        st.subheader("🔑 관리자 전용")
        st.info("관리자 전용 기능이 여기에 표시됩니다. (추후 구현 예정)")
```

---

## 설명

- **프로젝트 정보**:  
  3개의 컬럼으로 구분하여 주요 문서와 GitHub 링크를 직관적으로 제공합니다.

- **프로젝트 목표**:  
  프로젝트가 지향하는 목표를 명확히 기술하여 사용자에게 전달합니다.

- **향후 계획**:  
  현재 상태 및 향후 추진할 계획을 간략한 표로 제공하여 프로젝트 진행 상황을 쉽게 이해할 수 있도록 합니다.

- **관리자 전용**:  
  관리자 로그인 시(관리자 IP 접속 시)에만 추가 기능이나 관리 기능을 추후 표시할 수 있는 공간을 제공합니다.

---

이 형태로 관리하면 프로젝트 정보 제공이 직관적이고 명확하며, 향후 추가 확장도 용이합니다. 추가 사항 있으면 알려주세요!
