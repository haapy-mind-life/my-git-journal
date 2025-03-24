---
created: 2025-03-24T10:58:17+09:00
modified: 2025-03-24T10:58:32+09:00
---

# 2025-03-24-carrier_feature_generator.py#1

import streamlit as st
from modules.json_utils import create_cf_json  # 예: json_utils.py 안에 정의된 함수

def run(is_admin=False):
    """
    NEW FORMAT 전용 Carrier Feature Generator (예시)
    - MCC_MNC 입력
    - Feature (ADD / REMOVE) 체크
    - 'CF 파일 생성' 버튼 클릭 시 create_cf_json() 호출
    - 결과 JSON 미리보기 & 다운로드
    """
    st.subheader("Carrier Feature Generator (NEW FORMAT)")

    st.info("현재 화면은 NEW FORMAT 전용 예시입니다. ADD / REMOVE 체크 방식을 사용합니다.")
    
    # (1) MCC_MNC 입력
    mcc_mnc = st.text_input("MCC_MNC 입력", placeholder="예: 123456 또는 99999F")

    # (2) Feature 리스트
    features = ["NSA", "DSS", "SA", "SA_DSS", "NSA_NRCA", "SA_NRCA", "VONR"]

    st.markdown("#### Legacy Feature 설정 (ADD / REMOVE)")

    # 체크박스 형태로 ADD, REMOVE 동시 선택 가능 (실무 로직에 맞춰 조정)
    # 예: NSA_ADD, NSA_REMOVE
    feature_settings = {}
    for feat in features:
        with st.container():
            st.write(f"**{feat}**")
            add_key = f"{feat}_add"
            remove_key = f"{feat}_remove"
            add_val = st.checkbox("ADD", key=add_key)
            remove_val = st.checkbox("REMOVE", key=remove_key)
            feature_settings[feat] = {
                "ADD": add_val,
                "REMOVE": remove_val
            }
        st.markdown("---")

    # (3) CF 파일 생성 버튼
    if st.button("💾 CF 파일 생성"):
        # (3-1) create_cf_json 호출 (json_utils.py)
        #      MCC_MNC, feature_settings 등 사용자가 선택한 데이터를 넘겨주어 CF JSON 생성
        cf_data = create_cf_json(
            mcc_mnc=mcc_mnc,
            feature_config=feature_settings
        )

        # (3-2) 결과 표시
        st.success("CF 파일 생성 완료!")
        st.json(cf_data)

        # (3-3) 파일 다운로드
        st.download_button(
            label="📥 CF JSON 다운로드",
            data=str(cf_data),    # json.dumps(cf_data, ensure_ascii=False, indent=2) 로도 가능
            file_name="CF_file.json",
            mime="application/json"
        )

    # (옵션) 관리자 전용 영역
    if is_admin:
        st.warning("관리자 전용 옵션을 여기에 추가할 수 있습니다.")
