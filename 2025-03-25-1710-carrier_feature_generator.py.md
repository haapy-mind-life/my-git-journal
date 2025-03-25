---
created: 2025-03-25T17:10:31+09:00
modified: 2025-03-25T17:11:05+09:00
---

# 2025-03-25-1710-carrier_feature_generator.py

아래는 **새로운 3단계 컨셉**(일반 라인 / 블록 라인 / 최종 병합)에 맞춰 **carrier_feature_generator.py**를 업데이트한 예시 코드입니다.  
- **`parse_nonblock_lines()`**, **`parse_block_lines()`**, **`finalize_merged_lines()`**는 **file_utils.py**에 구현되어 있다고 가정합니다.  
- NEW FORMAT 여부에 따라 업로드(UI) 흐름이 달라지고,  
- 마지막에 Feature 설정 및 CF 파일 생성 단계를 추가했습니다.

---

## carrier_feature_generator.py (최신 예시)

```python
def run(is_admin=False):
    import streamlit as st
    from modules.file_utils import (
        parse_nonblock_lines,
        parse_block_lines,
        finalize_merged_lines
    )
    from modules.json_utils import create_cf_file  # 예: 최종 CF JSON 생성
    
    st.title("Carrier Feature Generator (3단계 분리)")

    # ─────────────────────────────────────────────────────────
    # 1) NEW FORMAT + 파일 업로드
    # ─────────────────────────────────────────────────────────
    st.subheader("1. 파일 업로드 (NEW FORMAT 미사용 시)")
    new_format = st.checkbox("NEW FORMAT 사용", value=False)
    uploaded_file = None

    if not new_format:
        uploaded_file = st.file_uploader("업로드할 .h 파일", type=["h"])
        if uploaded_file:
            st.success("파일 업로드 완료! 아래 단계 버튼을 차례로 진행하세요.")
        else:
            st.info("파일(.h)을 업로드하세요.")
    else:
        st.info("NEW FORMAT 사용 시 파일 업로드가 불필요합니다.")

    st.markdown("---")

    # ─────────────────────────────────────────────────────────
    # 2) (STEP 1) 일반 라인 파싱
    # ─────────────────────────────────────────────────────────
    st.subheader("2. 일반 라인 파싱 (Step 1)")
    step1_executed = False
    if not new_format and uploaded_file:
        if st.button("1) 일반 라인 파싱"):
            parse_nonblock_lines(uploaded_file)
            step1_executed = True
    else:
        st.info("NEW FORMAT이거나 파일 업로드 전이므로 Step 1 생략 가능")

    st.markdown("---")

    # ─────────────────────────────────────────────────────────
    # 3) (STEP 2) 블록 파싱 & 사용자 선택
    # ─────────────────────────────────────────────────────────
    st.subheader("3. 블록 파싱 & 선택 (Step 2)")
    step2_executed = False
    if not new_format and uploaded_file:
        if st.button("2) 블록 선택"):
            parse_block_lines()
            step2_executed = True
    else:
        st.info("NEW FORMAT이거나 파일 업로드 전이므로 Step 2 생략 가능")

    st.markdown("---")

    # ─────────────────────────────────────────────────────────
    # 4) (STEP 3) 최종 병합
    # ─────────────────────────────────────────────────────────
    st.subheader("4. 최종 병합 (Step 3)")
    if not new_format and uploaded_file:
        if st.button("3) 일반 + 블록 병합"):
            finalize_merged_lines()
            st.success("일반 라인 + 블록 선택 라인 병합 완료 → parsed_list 저장")
    else:
        st.info("NEW FORMAT이거나 파일 업로드 전이므로 Step 3 생략 가능")

    # 확인
    if "parsed_list" in st.session_state and st.session_state["parsed_list"]:
        st.write("**parsed_list (최종 병합 라인 미리보기)**")
        st.code("\n".join(st.session_state["parsed_list"]))
    else:
        st.info("parsed_list가 아직 비어있습니다.")

    st.markdown("---")

    # ─────────────────────────────────────────────────────────
    # 5) Feature 설정 (NEW FORMAT vs 일반)
    # ─────────────────────────────────────────────────────────
    st.subheader("5. Feature 설정")
    # 7개 Feature
    features = ["NR_NSA", "NR_DSS", "NR_SA", "NR_SA_DSS", "NR_VONR", "NR_NSA_NRCA", "NR_SA_NRCA"]

    # session_state에 feature_settings
    if "feature_settings" not in st.session_state:
        st.session_state["feature_settings"] = {}

    for feat in features:
        if feat not in st.session_state["feature_settings"]:
            # 초기화
            st.session_state["feature_settings"][feat] = {
                "checked": False,
                "mode": None,
                "value": None
            }

        col1, col2, col3 = st.columns([1,1.3,1.2])
        with col1:
            checked = st.checkbox(f"{feat}", key=f"{feat}_check", value=st.session_state["feature_settings"][feat]["checked"])
        with col2:
            if checked:
                if new_format:
                    # ADD / REMOVE
                    mode_val = st.radio("Mode", ["ADD", "REMOVE"], horizontal=True, key=f"{feat}_mode")
                    val_opt = None  # NEW FORMAT 시 enable/disable 없음
                else:
                    # ALLOW_MODE / BLOCK_MODE
                    mode_val = st.radio("Mode", ["ALLOW_MODE", "BLOCK_MODE"], horizontal=True, key=f"{feat}_mode")
                    # col3 - enable/disable
                    with col3:
                        val_opt = st.radio("Value", ["ENABLE", "DISABLE"], horizontal=True, key=f"{feat}_val")
                st.session_state["feature_settings"][feat]["checked"] = True
                st.session_state["feature_settings"][feat]["mode"] = mode_val
                st.session_state["feature_settings"][feat]["value"] = val_opt
            else:
                # 체크 안됨
                st.session_state["feature_settings"][feat]["checked"] = False
                st.session_state["feature_settings"][feat]["mode"] = None
                st.session_state["feature_settings"][feat]["value"] = None
                mode_val = None
                val_opt = None
                with col3:
                    st.write("(비활성)")

    st.markdown("---")

    # ─────────────────────────────────────────────────────────
    # 6) CF 파일 생성
    # ─────────────────────────────────────────────────────────
    st.subheader("6. CF 파일 생성")
    omc_version = st.text_input("OMC VERSION (예: 91)")
    mcc_mnc = st.text_input("MCC_MNC 입력 (예: 123456)")

    if st.button("CF 파일 생성"):
        # 검증
        if not omc_version.strip():
            st.error("OMC VERSION이 비어있습니다.")
            return
        if not mcc_mnc.strip():
            st.error("MCC_MNC가 비어있습니다.")
            return

        # (예) feature_settings → 최종 DF
        from modules.file_utils import finalize_df
        final_df = finalize_df(new_format, st.session_state["feature_settings"])
        if final_df.empty:
            st.warning("설정된 Feature가 없습니다. 최소 1개 이상 체크?")
            return

        st.success("Feature 설정 DF 생성 완료!")

        # (예) CF JSON 생성
        from modules.json_utils import create_cf_file
        cf_data = create_cf_file(
            final_df=final_df,
            omc_version=omc_version,
            mcc_mnc=mcc_mnc
        )
        if not cf_data:
            st.error("CF 파일 생성 실패 (cf_data가 비어있음)")
            return

        st.success("CF 파일 생성 완료!")
        st.write("**최종 DataFrame 미리보기**")
        st.dataframe(final_df, use_container_width=True)

        import json
        cf_json_str = json.dumps(cf_data, ensure_ascii=False, indent=2)
        st.download_button(
            label="CF 파일 다운로드",
            data=cf_json_str,
            file_name=f"CF_{mcc_mnc}.json",
            mime="application/json"
        )

    # 관리자
    if is_admin:
        st.warning("(관리자 전용) 추가 기능 UI")
```

---

### 코드 개요

1. **파일 업로드 (NEW FORMAT 미사용 시)**  
   - `.h` 파일 업로드  
   - “1) 일반 라인 파싱” 버튼 → `parse_nonblock_lines(uploaded_file)` (file_utils.py)  
   - “2) 블록 선택” 버튼 → `parse_block_lines()`  
   - “3) 일반+블록 병합” → `finalize_merged_lines()`  
   - 최종 결과 → `st.session_state["parsed_list"]`

2. **Feature 설정**  
   - NEW FORMAT이면 (ADD/REMOVE), 아니면 (ALLOW/BLOCK + ENABLE/DISABLE)  
   - 체크가 해제된 Feature는 모드/값을 None, UI 비활성(간단히 표시)

3. **CF 파일 생성**  
   - OMC_VERSION, MCC_MNC 입력 (검증)  
   - **`finalize_df(new_format, feature_settings)`** → 최종 DataFrame  
   - **`create_cf_file(final_df, omc_version, mcc_mnc)`** → CF JSON → 다운로드

각 단계에 **오류/검증** 로직을 추가하여,  
- 비어있는 값 → `st.error(...)` → `return`  
등을 수행합니다.

---

## file_utils.py & json_utils.py (요약)

```python
# file_utils.py

def parse_nonblock_lines(uploaded_file):
    # 파일 라인 => normal_lines, block_candidates
    ...

def parse_block_lines():
    # block_candidates => A/B/Skip UI => block_lines
    ...

def finalize_merged_lines():
    # normal_lines + block_lines => parsed_list
    ...

def finalize_df(new_format, feature_settings):
    # feature_settings => final_df
    ...
```

```python
# json_utils.py

def create_cf_file(final_df, omc_version, mcc_mnc):
    # final_df → CF JSON (dict) → return
    ...
```

---

이로써 **3단계 라인 파싱**(일반/블록/병합)과 **NEW FORMAT** 여부에 따른 Feature 설정, **CF 파일 생성** 흐름을 **UI 단**에서 깔끔하게 정리할 수 있습니다.
