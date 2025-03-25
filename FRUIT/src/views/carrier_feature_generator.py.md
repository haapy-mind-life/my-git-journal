---
created: 2025-03-26T03:22:08+09:00
modified: 2025-03-26T03:22:19+09:00
---

# carrier_feature_generator.py

아래는 현재까지의 논의를 모두 반영한 **최신 버전의** `carrier_feature_generator.py` 코드입니다.  

- UI 흐름 간결화  
- 파일 업로드, NEW FORMAT 여부 체크, 피쳐 설정 간 명확한 구분  
- 최종 파일(JSON) 생성 및 다운로드

---

### **`carrier_feature_generator.py` (최신 업데이트)**

```python
import streamlit as st
import pandas as pd
from modules.file_utils import parse_nonblock_lines, parse_block_lines, merged
from modules.json_utils import create_cf_json

def run(is_admin=False):
    st.title("🚀 Carrier Feature Generator")

    # 1. 파일 업로드 섹션
    st.subheader("1️⃣ 파일 업로드")
    new_format = st.checkbox("NEW FORMAT 사용")
    
    uploaded_file = None
    if not new_format:
        uploaded_file = st.file_uploader("파일 업로드 (.h)", type=["h"])
        if uploaded_file:
            st.success("✅ 파일 업로드 완료")
            parse_nonblock_lines(uploaded_file)
            parse_block_lines()
            
            if st.button("📌 블록 선택 완료"):
                merged()
                st.success("✅ 블록 선택이 완료되었습니다.")
                if "final_df" in st.session_state:
                    st.subheader("📋 전처리 결과 미리보기")
                    st.dataframe(st.session_state["final_df"], use_container_width=True)
    else:
        st.info("NEW FORMAT 사용 중: 파일 업로드가 필요 없습니다.")

    st.markdown("---")

    # 2. Feature 설정 섹션
    st.subheader("2️⃣ Feature 설정")
    
    features = ["NR_NSA", "NR_DSS", "NR_SA", "NR_SA_DSS", "NR_NSA_NRCA", "NR_SA_NRCA", "NR_VONR"]
    feature_settings = {}

    for feat in features:
        st.markdown(f"**{feat} 설정**")
        cols = st.columns([1, 2, 2])

        with cols[0]:
            use_feature = st.checkbox(f"{feat} 사용", key=f"{feat}_use")

        if use_feature:
            with cols[1]:
                if new_format:
                    mode = st.radio(f"{feat} 모드", ["ADD", "REMOVE"], key=f"{feat}_mode")
                else:
                    mode = st.radio(f"{feat} 모드", ["ALLOW_MODE", "BLOCK_MODE"], key=f"{feat}_mode")
            with cols[2]:
                if new_format:
                    status = st.selectbox(f"{feat} 상태", ["ENABLE", "DISABLE"], key=f"{feat}_status")
                else:
                    status = st.selectbox(f"{feat} 상태", ["ENABLE", "DISABLE"], key=f"{feat}_status")
            feature_settings[feat] = {"mode": mode, "status": status}
        else:
            feature_settings[feat] = None

        st.markdown("---")

    # 3. JSON 파일 생성 섹션
    st.subheader("3️⃣ CF JSON 생성")

    omc_version = st.text_input("OMC VERSION 입력 (예: 91)", placeholder="91")
    mcc_mnc = st.text_input("MCC_MNC 입력 (예: 123456 또는 99999F)", placeholder="123456")

    if st.button("💾 CF 파일 생성", use_container_width=True):
        if not omc_version.strip() or not mcc_mnc.strip():
            st.error("⚠️ OMC VERSION과 MCC_MNC를 정확히 입력해주세요.")
        else:
            # 파일 정보 요약
            file_info = "NEW FORMAT" if new_format else "Legacy FORMAT"
            if uploaded_file:
                file_info += f" ({uploaded_file.name})"

            # JSON 생성
            cf_json = create_cf_json(
                new_format=new_format,
                omc_version=omc_version.strip(),
                mcc_mnc=mcc_mnc.strip(),
                feature_config=feature_settings,
                file_info=file_info,
                parsed_df=st.session_state.get("final_df")
            )

            # JSON 직렬화
            import json
            json_str = json.dumps(cf_json, ensure_ascii=False, indent=2)

            st.success("✅ CF JSON 파일 생성 완료")
            st.download_button(
                label="📥 JSON 다운로드",
                data=json_str,
                file_name=f"CF_{omc_version}_{mcc_mnc}.json",
                mime="application/json"
            )

    if is_admin:
        st.subheader("🔑 관리자 전용 기능")
        st.info("관리자 전용 추가 기능이 여기에 표시됩니다. (추후 구현 예정)")
```

---

### **구조 및 기능 설명**

- **1. 파일 업로드 섹션**  
  - NEW FORMAT 체크 여부에 따라 업로드 메뉴 표시  
  - 파일 업로드 시 바로 전처리 진행(parse_nonblock_lines → parse_block_lines → merged)  
  - 전처리 결과(DataFrame) 미리보기 제공  

- **2. Feature 설정 섹션**  
  - 각 Feature별 사용 여부 체크박스  
  - 사용 선택된 Feature만 모드(ADD/REMOVE 또는 ALLOW/BLOCK) 및 상태(ENABLE/DISABLE) 설정 가능  
  - 사용하지 않는 Feature는 음영 처리 및 설정 비활성화  

- **3. CF JSON 생성 섹션**  
  - 필수 정보 입력: OMC VERSION, MCC_MNC  
  - JSON 생성 버튼 클릭 시 입력값 유효성 체크 후 JSON 파일 생성 및 다운로드  

- **관리자 기능**  
  - 추후 필요 시 관리자 전용 기능 추가 공간 확보  

---

이 구조는 UI의 직관성을 유지하며, 각 설정 단계가 명확히 구분되고, 파일 처리 로직도 모듈화되어 유지보수에 용이합니다. 추가적인 요구 사항 있으면 알려주세요!
