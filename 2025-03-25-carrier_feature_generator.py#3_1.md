---
created: 2025-03-25T14:51:31+09:00
modified: 2025-03-25T15:36:16+09:00
---

# 2025-03-25-carrier_feature_generator.py#3

아래는 **최신 버전**의 `carrier_feature_generator.py` 예시 코드입니다.  
- **NEW FORMAT** 체크 여부에 따라 `.h` 파일 업로드 메뉴 표시  
- 업로드 완료 시 **"파일 업로드 완료!"** 메시지  
- **Block 선택** 단계에서 **`parse_h_minimal()`** 호출  
- **최종 라인 생성**은 `parse_h_minimal` 내부 버튼으로 진행 (사용자가 A/B/Skip 결정 후)  
- **최종 변환 완료** 버튼 클릭 시 **`do_final_processing()`** → `final_df` 생성 후 미리보기 (가로폭 최대)

```python
def run(is_admin=False):
    import streamlit as st
    import math
    import json

    from modules.file_utils import parse_h_minimal, do_final_processing
    # parse_h_minimal() → 구간 및 블록(A/B/Skip) 파싱
    # do_final_processing() → parsed_list → final_df

    st.title("Carrier Feature Generator (최신)")

    # 1) NEW FORMAT 체크 및 파일 업로드
    st.subheader("1. 파일 업로드")
    new_format = st.checkbox("NEW FORMAT 사용", value=False)
    uploaded_file = None
    if not new_format:
        # NEW FORMAT이 아닌 경우에만 .h 업로드
        uploaded_file = st.file_uploader("지원 형식: .h", type=["h"])
        if uploaded_file:
            st.success("파일 업로드 완료!")
    else:
        st.info("NEW FORMAT 사용: 파일 업로드 불필요")

    # 2) Block 선택 (parse_h_minimal)
    st.subheader("2. Block 선택")
    # 파일이 있거나 NEW FORMAT이면 parse_h_minimal 수행
    if uploaded_file or new_format:
        parse_h_minimal(
            uploaded_file=uploaded_file if not new_format else None,
            start_marker="BEGIN_FEATURE",
            end_marker="END_FEATURE",
            max_blocks=10
        )
    else:
        st.info("파일(.h)을 업로드하거나 NEW FORMAT을 체크하세요.")
        return

    st.markdown("---")

    # 3) Legacy Feature 설정 (예시)
    st.subheader("3. Legacy Feature 설정 (예시)")
    st.info("여기서 7개 Feature + CHECKBOX 로직 등을 구현 가능")
    # (실제 Legacy Feature 설정 UI는 별도로 구현 가능)

    st.markdown("---")

    # 4) 최종 라인 생성 여부 확인
    # parse_h_minimal 내부 '최종 라인 생성' 버튼 클릭 시, st.session_state["parsed_list"]에 저장
    if "parsed_list" in st.session_state and st.session_state["parsed_list"]:
        st.success("Block 선택 완료 (parsed_list에 최종 라인 저장됨)")
    else:
        st.info("아직 최종 라인 생성 전이거나 parsed_list가 비어있습니다.")

    # 5) 최종 변환 (DF 생성 등)
    st.subheader("4. 최종 변환")
    if st.button("최종 변환 완료"):
        # do_final_processing() → st.session_state['final_df'] 생성
        do_final_processing()

        if "final_df" in st.session_state:
            df = st.session_state["final_df"]
            if df.empty:
                st.warning("최종 DataFrame이 비어있습니다.")
                return

            st.success("최종 변환 완료!")
            st.write("**전처리 결과 (DataFrame) - 가로 폭 최대**")
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("final_df가 생성되지 않았습니다.")

    # 관리자 전용
    if is_admin:
        st.warning("관리자 전용 기능 영역입니다.")
```

---

## 코드 해설

1. **NEW FORMAT** 체크  
   - 체크 해제 시 `.h` 파일 업로드, 체크 시 업로드 불필요.  
   - 업로드 되면 `"파일 업로드 완료!"` 표시.

2. **Block 선택**  
   - **`parse_h_minimal(...)`** 호출.  
   - 마커: `"BEGIN_FEATURE" ~ "END_FEATURE"`  
   - 최대 블록: `max_blocks=10`  
   - 내부에서 A/B/Skip 결정 + "최종 라인 생성" 버튼 → **`st.session_state["parsed_list"]`** 에 결과 라인 저장.

3. **Legacy Feature 설정**(예시)  
   - 필요한 UI만 표시. (실제 로직은 프로젝트별 구현)

4. **최종 라인 생성** 여부 확인  
   - `st.session_state["parsed_list"]`가 비어있으면 아직 라인 생성 전.

5. **최종 변환 완료**  
   - **`do_final_processing()`** → `final_df` 생성 후 저장.  
   - `df.empty` 검사 → 미리보기 시 `st.dataframe(df, use_container_width=True)`로 가로 폭 최대화.  

6. **관리자 전용**  
   - `if is_admin: st.warning("관리자 전용...")`

이 코드 구조대로라면, 사용자는  
1) `.h` 업로드(또는 NEW FORMAT 체크)  
2) **Block 선택**(A/B/Skip) + `"최종 라인 생성"` → `parsed_list`  
3) **"최종 변환 완료"** 버튼 → `final_df` → **데이터프레임 미리보기**

원하는 시나리오를 모두 충족할 수 있습니다.  

프로젝트 요구사항에 맞추어 **중첩 #if**, **다중 marker**, **Legacy Feature UI** 등을 확장하시면 됩니다.
