---
created: 2025-03-25T16:50:21+09:00
modified: 2025-03-25T16:50:33+09:00
---

# 2025-03-25-1650-carrier_feature_generator.py

아래는 **최신** 요구사항을 반영한 **`carrier_feature_generator.py`** 코드 예시입니다.  
- **Step 2**가 **“Feature 설정”** 으로 변경.  
  - **NEW FORMAT** 미사용 시: “Feature 체크 → (ALLOW_MODE/BLOCK_MODE) → (ENABLE/DISABLE)”  
  - **NEW FORMAT** 사용 시: “Feature 체크 → (ADD/REMOVE)” (ENABLE/DISABLE은 없음)  
- **CF 파일 생성** 시 입력값(예: OMC VERSION, MCC_MNC) 검증 후 **잘못된 경우 오류 처리**를 추가했습니다.  
- **나머지** 로직(파일 업로드 + Block 선택, DF 생성, CF 파일 생성) 구조는 그대로 유지합니다.  
- **file_utils**, **json_utils** 등에서 실제 로직을 구현해 **재사용**하도록 가정하고, 이 파일은 **UI(frontend)** 중심으로만 작성했습니다.

---

## carrier_feature_generator.py (업데이트 예시)

```python
def run(is_admin=False):
    import streamlit as st
    import math
    import json

    # 예: file_utils, json_utils 내부 함수 (실제 구현은 프로젝트 상황에 맞춰)
    from modules.file_utils import parse_block_selection, finalize_df
    from modules.json_utils import create_cf_file

    st.title("Carrier Feature Generator (최신)")

    # ─────────────────────────────────────────────────────────
    # 1. 파일 업로드 & NEW FORMAT 여부
    # ─────────────────────────────────────────────────────────
    st.subheader("1. 파일 업로드")
    new_format = st.checkbox("NEW FORMAT 사용", value=False)
    uploaded_file = None

    if not new_format:
        uploaded_file = st.file_uploader("업로드할 .h 파일 선택", type=["h"])
        if uploaded_file:
            st.success("파일 업로드 완료!")
            # Block 선택 UI (A/B/Skip 등)
            parse_block_selection(uploaded_file)
        else:
            st.info(".h 파일을 업로드하세요.")
    else:
        st.info("NEW FORMAT 사용 시 파일 업로드가 불필요합니다.")

    st.markdown("---")

    # ─────────────────────────────────────────────────────────
    # 2. Feature 설정
    # ─────────────────────────────────────────────────────────
    st.subheader("2. Feature 설정")

    # 7개 Feature 목록
    features = ["NR_NSA", "NR_DSS", "NR_SA", "NR_SA_DSS", "NR_VONR", "NR_NSA_NRCA", "NR_SA_NRCA"]

    # session_state에 feature_settings 딕셔너리 저장 (없으면 초기화)
    if "feature_settings" not in st.session_state:
        st.session_state["feature_settings"] = {}  # { feat: {checked, mode, value} ... }

    # Feature UI
    for feat in features:
        if feat not in st.session_state["feature_settings"]:
            # 초기값
            st.session_state["feature_settings"][feat] = {
                "checked": False,   # Feature 체크
                "mode": None,       # ALLOW_MODE/BLOCK_MODE or ADD/REMOVE
                "value": None       # ENABLE/DISABLE (if not new_format)
            }

        col1, col2, col3 = st.columns([1, 1.3, 1.2])
        with col1:
            checked = st.checkbox(f"{feat}", key=f"{feat}_check", value=st.session_state["feature_settings"][feat]["checked"])
        with col2:
            if new_format:
                # NEW FORMAT => ADD/REMOVE
                if checked:
                    mode_val = st.radio("Mode", ["ADD", "REMOVE"], horizontal=True, key=f"{feat}_mode")
                else:
                    mode_val = None
            else:
                # Not NEW FORMAT => ALLOW_MODE/BLOCK_MODE
                if checked:
                    mode_val = st.radio("Mode", ["ALLOW_MODE", "BLOCK_MODE"], horizontal=True, key=f"{feat}_mode")
                else:
                    mode_val = None

        with col3:
            # NEW FORMAT 미사용 시 => ENABLE/DISABLE
            if not new_format:
                if checked and mode_val is not None:
                    # ENABLE/DISABLE
                    val_opt = st.radio("값 설정", ["ENABLE", "DISABLE"], horizontal=True, key=f"{feat}_val")
                else:
                    # 비활성
                    val_opt = None
            else:
                # NEW FORMAT이면 없음
                val_opt = None

        # 저장
        st.session_state["feature_settings"][feat]["checked"] = checked
        st.session_state["feature_settings"][feat]["mode"] = mode_val
        st.session_state["feature_settings"][feat]["value"] = val_opt

    # 검증 (체크가 되었는데 mode가 None이면 오류, etc.)
    # 아래는 단순 예시:
    next_possible = True
    for feat in features:
        cfg = st.session_state["feature_settings"][feat]
        if cfg["checked"] and cfg["mode"] is None:
            st.error(f"{feat}: 모드를 선택해야 합니다.")
            next_possible = False

    st.markdown("---")

    # ─────────────────────────────────────────────────────────
    # 3. CF 파일 생성
    # ─────────────────────────────────────────────────────────
    st.subheader("3. CF 파일 생성")

    omc_version = st.text_input("OMC VERSION (예: 91)")
    mcc_mnc = st.text_input("MCC_MNC 입력 (예: 123456, 99999F)")

    if st.button("CF 파일 생성하기"):
        # (a) 입력값 검증
        if not omc_version.strip():
            st.error("OMC VERSION을 입력하세요.")
            return
        if not mcc_mnc.strip():
            st.error("MCC_MNC를 입력하세요.")
            return
        if not next_possible:
            st.error("Feature 설정에 오류가 있습니다. 위 항목을 수정해주세요.")
            return

        # (b) finalize_df()로 DataFrame 생성
        final_df = finalize_df(new_format, st.session_state["feature_settings"])
        if final_df is None or final_df.empty:
            st.error("최종 변환할 데이터가 없습니다.")
            return

        # (c) create_cf_file()로 CF JSON 생성
        cf_data = create_cf_file(
            final_df=final_df,
            omc_version=omc_version,
            mcc_mnc=mcc_mnc
        )
        if not cf_data:
            st.error("CF 파일 생성 실패 (cf_data가 비어있음)")
            return

        st.success("최종 변환 완료!")
        # 미리보기
        st.write("**최종 DataFrame 미리보기**")
        st.dataframe(final_df, use_container_width=True)

        # 다운로드
        import json
        cf_json_str = json.dumps(cf_data, ensure_ascii=False, indent=2)
        st.download_button(
            label="CF 파일 다운로드",
            data=cf_json_str,
            file_name=f"CF_{mcc_mnc}.json",
            mime="application/json"
        )

    # 관리자 표시
    if is_admin:
        st.warning("관리자 모드 활성화중.")
```

---

## 설명

1. **파일 업로드**  
   - **NEW FORMAT** 체크가 **False**일 때 `.h` 파일 업로드 → 업로드 성공 시 **"파일 업로드 완료"** 표시  
   - 이후 **`parse_block_selection(uploaded_file)`**(예시 함수 in `file_utils.py`)를 통해 Block 선택  
   - **NEW FORMAT**이 **True**라면 업로드 불필요  

2. **Feature 설정**  
   - 7개 Feature 각각에 대해 **3열** UI  
     1) **Feature 체크** (col1)  
     2) **모드 선택** (col2)  
        - NEW FORMAT이면 **ADD/REMOVE**  
        - 아니면 **ALLOW_MODE/BLOCK_MODE**  
     3) **값 설정**(ENABLE/DISABLE) (col3, **NEW FORMAT이 아닐 때만** 표시)  
   - 체크 안 된 Feature는 모드/값을 **None**으로 두어 비활성 처리  
   - 단순 검증(**next_possible**): 체크되었는데 모드가 None이면 에러 표시

3. **CF 파일 생성**  
   - **OMC VERSION**, **MCC_MNC** 입력 (검증 후, 없으면 오류)  
   - **`finalize_df(new_format, st.session_state["feature_settings"])`** 호출 → Feature 설정들로 DataFrame 생성  
   - **`create_cf_file(...)`** → JSON 생성  
   - 결과를 미리보고, **다운로드** 버튼으로 `.json` 파일 제공  

4. **오류 처리**  
   - OMC_VERSION, MCC_MNC 비어 있으면 `st.error(...)` 후 return  
   - Feature 설정 오류도 `st.error(...)`  
   - final_df 비어있으면 오류 등

---

## file_utils.py (간단 스켈레톤 예시)

```python
def parse_block_selection(uploaded_file):
    import streamlit as st
    st.info("파일에서 #if ~ #else ~ #endif 블록을 파싱해 A/B/Skip 선택하는 예시")
    # 이후, 최종 라인 session_state["parsed_list"] 등에 저장하는 로직

def finalize_df(new_format, feature_settings):
    import pandas as pd
    rows = []
    for feat, cfg in feature_settings.items():
        if cfg["checked"]:
            rows.append({
                "Feature": feat,
                "Mode": cfg["mode"] or "",
                "Value": cfg["value"] or ""
            })
    if not rows:
        return pd.DataFrame()  # 빈 DF
    return pd.DataFrame(rows, columns=["Feature", "Mode", "Value"])
```

---

## json_utils.py (간단 스켈레톤 예시)

```python
def create_cf_file(final_df, omc_version, mcc_mnc):
    import json
    if final_df is None or final_df.empty:
        return {}
    data = {
        "omc_version": omc_version,
        "mcc_mnc": mcc_mnc,
        "features": []
    }
    for _, row in final_df.iterrows():
        data["features"].append({
            "name": row["Feature"],
            "mode": row["Mode"],
            "value": row["Value"]
        })
    return data
```

---

### 결론

이렇게 **UI 코드(`carrier_feature_generator.py`)**를 **단순화**하고,  
- **NEW FORMAT** 여부  
- **파일 업로드 / Block 파싱**  
- **Feature 설정** (체크 + 모드 + ENABLE/DISABLE or ADD/REMOVE)  
- **CF 파일 생성** (오류 시 `st.error` 후 `return`)

등을 하나의 흐름으로 구현했습니다.  
**file_utils**, **json_utils** 안에서 **실제 로직**을 구현하고, 이곳에서는 UI 이벤트와 입력값 검증을 담당하도록 구분했습니다.

프로젝트 요구사항에 맞춰 세부 코드를 조정하여 사용하세요!
