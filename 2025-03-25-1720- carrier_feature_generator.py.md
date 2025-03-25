---
created: 2025-03-25T17:20:07+09:00
modified: 2025-03-25T17:20:26+09:00
---

# 2025-03-25-1720- carrier_feature_generator.py

아래는 **최신 요구사항**을 반영한 **`carrier_feature_generator.py`** 예시 코드입니다.  
- **NEW FORMAT** 체크 시: 파일 업로드 불필요, 블록 선택 단계도 생략  
- **NEW FORMAT** 미사용 시: `.h` 파일 업로드 후,  
  1. 일반 라인 파싱(**parse_nonblock_lines**)  
  2. 블록 후보가 있을 경우만 블록 선택(**parse_block_lines**)  
  3. 병합(**finalize_merged_lines**)  
- 마지막으로 **Feature 설정**(ALLOW_MODE/BLOCK_MODE or ADD/REMOVE 등) & **CF 파일 생성** 단계를 거칩니다.

```python
def run(is_admin=False):
    import streamlit as st
    import json

    # file_utils.py 함수들
    from modules.file_utils import (
        parse_nonblock_lines,
        parse_block_lines,
        finalize_merged_lines,
        finalize_df
    )
    # json_utils.py 함수
    from modules.json_utils import create_cf_file

    st.title("Carrier Feature Generator (최신)")

    # ─────────────────────────────────────────────────────────
    # 1) NEW FORMAT & 파일 업로드
    # ─────────────────────────────────────────────────────────
    st.subheader("1. 파일 업로드 (NEW FORMAT 아닌 경우만)")
    new_format = st.checkbox("NEW FORMAT 사용", value=False)
    uploaded_file = None

    if not new_format:
        uploaded_file = st.file_uploader("업로드할 .h 파일", type=["h"])
        if uploaded_file:
            st.success("파일 업로드 완료! 아래 단계를 순서대로 진행하세요.")
        else:
            st.info(".h 파일을 업로드하세요.")
    else:
        st.info("NEW FORMAT 사용 시 파일 업로드가 불필요합니다.")

    st.markdown("---")

    # ─────────────────────────────────────────────────────────
    # 2) 일반 라인 파싱
    # ─────────────────────────────────────────────────────────
    st.subheader("2. 일반 라인 파싱")
    if not new_format and uploaded_file:
        if st.button("1) 일반 라인 파싱"):
            parse_nonblock_lines(uploaded_file)
    else:
        st.info("NEW FORMAT 또는 파일 업로드 전이면 스킵")

    st.markdown("---")

    # ─────────────────────────────────────────────────────────
    # 3) 블록 선택 (있을 때만)
    # ─────────────────────────────────────────────────────────
    st.subheader("3. 블록 선택")
    if not new_format and uploaded_file:
        # block_candidates가 있는 경우에만 버튼 표시
        block_exists = (
            "block_candidates" in st.session_state and 
            st.session_state["block_candidates"] and 
            len(st.session_state["block_candidates"]) > 0
        )
        if block_exists:
            if st.button("2) 블록 파싱 & 선택"):
                parse_block_lines()
        else:
            st.info("블록 후보가 없으므로 이 단계를 생략해도 됩니다.")
    else:
        st.info("NEW FORMAT 또는 파일 업로드 전이면 스킵")

    st.markdown("---")

    # ─────────────────────────────────────────────────────────
    # 4) 병합
    # ─────────────────────────────────────────────────────────
    st.subheader("4. 병합 (일반 라인 + 블록 라인)")
    if not new_format and uploaded_file:
        if st.button("3) 병합"):
            finalize_merged_lines()
    else:
        st.info("NEW FORMAT이면 스킵")

    # 결과 미리보기
    if "parsed_list" in st.session_state and st.session_state["parsed_list"]:
        st.write("**parsed_list (최종 병합 라인 미리보기)**")
        st.code("\n".join(st.session_state["parsed_list"]))
    else:
        st.info("parsed_list가 아직 비어있습니다.")

    st.markdown("---")

    # ─────────────────────────────────────────────────────────
    # 5) Feature 설정
    # ─────────────────────────────────────────────────────────
    st.subheader("5. Feature 설정")

    # 7개 Feature
    features = ["NR_NSA", "NR_DSS", "NR_SA", "NR_SA_DSS", "NR_VONR", "NR_NSA_NRCA", "NR_SA_NRCA"]

    if "feature_settings" not in st.session_state:
        st.session_state["feature_settings"] = {}

    for feat in features:
        if feat not in st.session_state["feature_settings"]:
            st.session_state["feature_settings"][feat] = {
                "checked": False,
                "mode": None,
                "value": None
            }

        col1, col2, col3 = st.columns([1,1.5,1.5])
        with col1:
            checked = st.checkbox(f"{feat}", value=st.session_state["feature_settings"][feat]["checked"], key=f"{feat}_ck")
        with col2:
            if checked:
                if new_format:
                    mode_val = st.radio("Mode", ["ADD", "REMOVE"], horizontal=True, key=f"{feat}_md")
                    val_opt = None
                else:
                    mode_val = st.radio("Mode", ["ALLOW_MODE", "BLOCK_MODE"], horizontal=True, key=f"{feat}_md")
                    # col3 - ENABLE/DISABLE
                    with col3:
                        val_opt = st.radio("Value", ["ENABLE", "DISABLE"], horizontal=True, key=f"{feat}_val")
            else:
                mode_val = None
                val_opt = None
                with col2:
                    st.write("(모드 선택 불가)")
                with col3:
                    st.write("(비활성)")
        # 저장
        st.session_state["feature_settings"][feat]["checked"] = checked
        st.session_state["feature_settings"][feat]["mode"] = mode_val
        st.session_state["feature_settings"][feat]["value"] = val_opt

    st.markdown("---")

    # ─────────────────────────────────────────────────────────
    # 6) CF 파일 생성
    # ─────────────────────────────────────────────────────────
    st.subheader("6. CF 파일 생성")
    omc_version = st.text_input("OMC VERSION (예: 91)")
    mcc_mnc = st.text_input("MCC_MNC 입력 (예: 123456)")

    if st.button("CF 파일 생성"):
        # (a) 검증
        if not omc_version.strip():
            st.error("OMC VERSION을 입력하세요.")
            return
        if not mcc_mnc.strip():
            st.error("MCC_MNC를 입력하세요.")
            return

        # (b) finalize_df(new_format, feature_settings)
        final_df = finalize_df(new_format, st.session_state["feature_settings"])
        if final_df.empty:
            st.warning("Feature가 하나도 설정되지 않았습니다.")
            return
        st.success("Feature 설정 DF 생성 완료")

        # (c) create_cf_file(...)
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

    # 관리자 모드
    if is_admin:
        st.warning("(관리자 전용) 추가 기능 UI")
```

---

## 코드 흐름 요약

1. **(1) 파일 업로드**  
   - **NEW FORMAT=false** → `.h` 업로드  
   - **NEW FORMAT=true** → 파일 업로드 불필요

2. **(2) 일반 라인 파싱**  
   - “1) 일반 라인 파싱” 버튼 클릭 시 → **`parse_nonblock_lines(uploaded_file)`**  
   - **`normal_lines`** vs. **`block_candidates`** 구분

3. **(3) 블록 선택**  
   - “2) 블록 파싱 & 선택” → **`parse_block_lines()`**  
   - **`block_candidates`**가 있을 때만 버튼 표시

4. **(4) 병합**  
   - “3) 병합” → **`finalize_merged_lines()`**  
   - 최종 라인 → **`parsed_list`**

5. **(5) Feature 설정**  
   - **7개 Feature** 각각 체크/모드/value (ALLOW/BLOCK + ENABLE/DISABLE or ADD/REMOVE)

6. **(6) CF 파일 생성**  
   - **OMC VERSION, MCC_MNC** 검증  
   - **`finalize_df(new_format, feature_settings)`** → **final_df**  
   - **`create_cf_file(final_df, omc_version, mcc_mnc)`** → CF JSON → 다운로드

나머지 **파일 로직**(`parse_nonblock_lines`, `parse_block_lines`, `finalize_merged_lines`, `finalize_df`)과 **CF 로직**(`create_cf_file`)은 **file_utils** 및 **json_utils**에 구현하시면 됩니다.  
이로써 전체 UI(frontend) 흐름이 깔끔하게 정리되었습니다.
