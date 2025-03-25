---
created: 2025-03-25T16:34:39+09:00
modified: 2025-03-25T16:35:14+09:00
---

# 2025-03-25-1634-carrier_feature_generator.py

아래 예시는 **`carrier_feature_generator.py`** 파일을 **UI(frontend)** 위주로 단순화하여 작성한 코드입니다.  
- 실제 **블록 파싱**, **파일 로직**은 **`file_utils.py`**에서,  
- **CF JSON 생성** 등은 **`json_utils.py`**에서 수행하도록 하며,  
- 이곳에서는 **UI 흐름**(NEW FORMAT 체크, 파일 업로드, Feature 선택, 최종 변환 및 다운로드)을 주로 담당합니다.

---

## carrier_feature_generator.py (최신 단순 예시)

```python
def run(is_admin=False):
    import streamlit as st
    import math

    # 가정: file_utils, json_utils 내 필요한 함수를 import
    from modules.file_utils import parse_block_selection, finalize_df
    from modules.json_utils import create_cf_file

    st.title("Carrier Feature Generator")

    # ─────────────────────────────────────────────────────────
    # 1. 파일 업로드 & NEW FORMAT 체크
    # ─────────────────────────────────────────────────────────
    st.subheader("1. 파일 업로드")
    new_format = st.checkbox("NEW FORMAT 사용하기", value=False)
    uploaded_file = None

    if not new_format:
        # NEW FORMAT이 아닐 경우에만 .h 업로드
        uploaded_file = st.file_uploader("업로드할 .h 파일 선택", type=["h"])
        if uploaded_file:
            st.success("파일 업로드 완료!")
            # (예) file_utils.parse_block_selection(...)에서
            # 블록 선택 UI (A/B/Skip) 등 진행
            parse_block_selection(uploaded_file)
        else:
            st.info(".h 파일을 업로드하세요.")
    else:
        st.info("NEW FORMAT 사용 시 파일 업로드가 불필요합니다.")

    # ─────────────────────────────────────────────────────────
    # 2. FEATURE MODE 설정
    # ─────────────────────────────────────────────────────────
    st.subheader("2. FEATURE MODE 설정")

    # 7개 Feature
    features = ["NR_NSA", "NR_DSS", "NR_SA", "NR_SA_DSS", "NR_VONR", "NR_NSA_NRCA", "NR_SA_NRCA"]
    # 예: ALLOW_MODE / BLOCK_MODE or ADD / REMOVE
    # 여기서는 "체크"를 통해 Feature를 활성화한 뒤, 해당 모드를 선택

    # 사용자 입력 저장용
    # 실제 로직은 session_state / dict를 혼합해 구성 가능
    if "feature_config" not in st.session_state:
        st.session_state["feature_config"] = {}

    # Feature 체크 + 모드 설정
    for feat in features:
        col1, col2 = st.columns([1,2])
        with col1:
            enabled = st.checkbox(f"{feat} 사용 여부", key=f"{feat}_enabled")
        with col2:
            if not enabled:
                # 비활성 시 음영 처리(쉬운 방법은 disabled=True 옵션)
                mode = st.radio(
                    label="모드 선택",
                    options=["(비활성)"],
                    disabled=True,
                    index=0,
                    key=f"{feat}_mode"
                )
            else:
                if new_format:
                    # NEW FORMAT => ADD/REMOVE
                    mode = st.radio(
                        label="모드 선택",
                        options=["ADD", "REMOVE"],
                        horizontal=True,
                        key=f"{feat}_mode"
                    )
                else:
                    # NOT NEW FORMAT => ALLOW_MODE / BLOCK_MODE
                    mode = st.radio(
                        label="모드 선택",
                        options=["ALLOW_MODE", "BLOCK_MODE"],
                        horizontal=True,
                        key=f"{feat}_mode"
                    )
        # 저장
        st.session_state["feature_config"][feat] = {
            "enabled": enabled,
            "mode": mode
        }

    st.markdown("---")

    # 간단 검증: 중복 체크 (ex: 사용자 요청 - "체크 설정이 중복"이라면?)
    # 여기서는 예시로 "어떤 모드가 2개 이상이면 에러" 등 간단한 검사 가능.
    # 실제 구현은 상황에 맞게.

    # ─────────────────────────────────────────────────────────
    # 3. 생성 및 다운로드
    # ─────────────────────────────────────────────────────────
    st.subheader("3. 생성 및 다운로드")

    # 3.1) OMC VERSION, MCC_MNC 입력
    omc_version = st.text_input("OMC VERSION 입력 (예: 91)")
    mcc_mnc = st.text_input("MCC_MNC 입력 (예: 123456, 99999F 등)")

    # 3.2) 최종 CF 파일 생성 버튼
    if st.button("CF 파일 생성"):
        # (예) file_utils.finalize_df(...) 등으로 최종 DF 생성
        #     session_state["final_df"] 등 저장
        final_df = finalize_df(new_format, st.session_state["feature_config"])
        
        # (예) json_utils.create_cf_file(...)에서 CF JSON or CF 구조 생성
        cf_file_data = create_cf_file(
            final_df=final_df,
            omc_version=omc_version,
            mcc_mnc=mcc_mnc
            # + 다른 필요한 데이터
        )

        # 결과 표시
        st.success("최종 변환 완료!")
        # 미리보기
        st.write("**최종 DataFrame 미리보기**")
        st.dataframe(final_df, use_container_width=True)

        # CF 파일 다운로드
        import json
        cf_json_str = json.dumps(cf_file_data, ensure_ascii=False, indent=2)
        st.download_button(
            label="CF 파일 다운로드",
            data=cf_json_str,
            file_name=f"CF_{mcc_mnc}.json",
            mime="application/json"
        )

    # 관리자
    if is_admin:
        st.warning("관리자 모드 활성화됨. 추가 관리자 기능을 여기에 구현할 수 있음.")
```

---

## 코드 흐름 설명

1. **파일 업로드**  
   - **NEW FORMAT**이 아닐 때만 **`.h` 파일**을 업로드.  
   - 업로드 완료 시 `"파일 업로드 완료!"` 메시지.  
   - 뒤에서 **`parse_block_selection(uploaded_file)`**(file_utils 내 함수) 호출하여 **Block 선택** 등 진행.

2. **FEATURE MODE 설정**  
   - 7개 Feature 각각에 대해 **Checkbox**(enable/disable) + **Radio**(ALLOW/BLOCK or ADD/REMOVE).  
   - NEW FORMAT이면 ADD/REMOVE, 아니면 ALLOW_MODE/BLOCK_MODE.  
   - 체크가 안 된 Feature는 `disabled=True` 등으로 음영 처리.

3. **생성 및 다운로드**  
   - **OMC VERSION**, **MCC_MNC** 입력.  
   - 버튼 클릭 시  
     - `file_utils.finalize_df(...)` 등으로 최종 DataFrame 생성 → (예시) `final_df`  
     - `json_utils.create_cf_file(...)` 등으로 CF JSON 생성 → 다운로드  
     - **가로 폭 최대**(`use_container_width=True`)로 최종 DF 미리보기

4. **관리자 전용**  
   - `if is_admin: st.warning("관리자...")`

---

## 외부 함수 예시 (간단 Skeleton)

**file_utils.py** (예시)

```python
import streamlit as st
import pandas as pd

def parse_block_selection(uploaded_file):
    st.info("여기서 #if ~ #else 블록 파싱 & A/B/Skip UI etc.")
    # block 선택 로직...
    # 최종 st.session_state["parsed_list"] 저장

def finalize_df(new_format, feature_config):
    """
    - new_format: bool
    - feature_config: { 'NR_NSA': {'enabled': True, 'mode': 'ALLOW_MODE'}, ... }
    - 예: ALLOW_MODE => mode=1, BLOCK_MODE => mode=2, ADD => mode=3, REMOVE => mode=4 ...
    - 최종 DF 생성, 예시:
      MCC_MNC, Feature, Mode
    """
    rows = []
    for feat, cfg in feature_config.items():
        if cfg["enabled"]:
            rows.append({
                "Feature": feat,
                "Mode": cfg["mode"]
            })
    df = pd.DataFrame(rows)
    st.session_state["final_df"] = df
    return df
```

**json_utils.py** (예시)

```python
def create_cf_file(final_df, omc_version, mcc_mnc):
    """
    - final_df: user-chosen features/modes
    - omc_version: (예: "91")
    - mcc_mnc: (예: "123456")
    - 원하는 CF 구조(JSON) 반환
    """
    # 예시:
    data = {
        "omc_version": omc_version,
        "mcc_mnc": mcc_mnc,
        "features": []
    }
    for _, row in final_df.iterrows():
        data["features"].append({
            "name": row["Feature"],
            "mode": row["Mode"]
        })
    return data
```

---

### 결론

이로써 **UI(frontend)**에 집중된 **`carrier_feature_generator.py`** 코드를 제시했습니다.  
- 파일 업로드(NEW FORMAT 비사용 시)  
- Block 선택 (file_utils.parse_block_selection)  
- Feature Mode 설정(ALLOW/BLOCK or ADD/REMOVE)  
- 최종 변환(OMC VERSION, MCC_MNC 입력) → CF 파일 다운로드  

**백엔드** 로직(`parse_block_selection`, `finalize_df`, `create_cf_file` 등)은 **`file_utils.py`, `json_utils.py`** 등에서 구현해 **재사용**하는 방식입니다.  
원하는 로직에 맞게 세부 코드를 수정해 활용하시면 됩니다.
