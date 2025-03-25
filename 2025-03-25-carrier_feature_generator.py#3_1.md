---
created: 2025-03-25T14:51:31+09:00
modified: 2025-03-25T14:52:02+09:00
---

# 2025-03-25-carrier_feature_generator.py#3

아래는 **최신 버전**의 예시 코드로, 요구사항을 반영하여 **`carrier_feature_generator.py`** 와 **`file_utils.py`**를 간결하게 구성했습니다.

---

## **carrier_feature_generator.py** (최신 업데이트 예시)
```python
def run(is_admin=False):
    import streamlit as st
    import json

    # file_utils.py의 함수들 불러온다고 가정
    from modules.file_utils import parse_h_minimal, do_final_processing

    st.title("Carrier Feature Generator (최신)")

    # 1. Marker 설정
    start_marker = st.text_input("Start Marker", "BEGIN_FEATURE")
    end_marker = st.text_input("End Marker", "END_FEATURE")

    # 2. 파일 업로드 (.h)
    uploaded_file = st.file_uploader(".h 파일 업로드", type=["h"])

    # parse_h_minimal에서 A/B 블록 파싱 & 선택, 최종 라인을 session_state["parsed_list"]에 저장
    if uploaded_file:
        parse_h_minimal(
            uploaded_file=uploaded_file,
            start_marker=start_marker,
            end_marker=end_marker,
            max_blocks=10
        )
    else:
        st.info(".h 파일을 업로드하세요.")
        return

    st.markdown("---")
    
    # 3. "전처리 & DF 생성" 버튼
    if st.button("전처리 + DF 생성"):
        # do_final_processing() 내부에서
        # session_state["parsed_list"] → DF 생성 & session_state["final_df"] 저장
        do_final_processing()

        # 최종 DF 확인
        if "final_df" in st.session_state:
            df = st.session_state["final_df"]
            if df.empty:
                st.warning("최종 DataFrame이 비어있습니다.")
                return

            # 모드(1=ALLOW_LIST, 2=BLOCK_LIST) 가정
            st.subheader("[ALLOW_LIST] 미리보기")
            df_allow = df[df["MODE"] == 1].copy()
            st.dataframe(df_allow.head(5))  # 일부 미리보기
            st.write(f"ALLOW_LIST 총 {len(df_allow)}개 MCC_MNC 보유")

            st.subheader("ALLOW_LIST 전체 DataFrame")
            st.dataframe(df_allow)

            st.markdown("---")

            st.subheader("[BLOCK_LIST] 미리보기")
            df_block = df[df["MODE"] == 2].copy()
            st.dataframe(df_block.head(5))
            st.write(f"BLOCK_LIST 총 {len(df_block)}개 MCC_MNC 보유")

            st.subheader("BLOCK_LIST 전체 DataFrame")
            st.dataframe(df_block)
        else:
            st.warning("final_df가 생성되지 않았습니다.")
```

---

## **file_utils.py** (스켈레톤 코드)

```python
import streamlit as st
import pandas as pd

def parse_h_minimal(uploaded_file, start_marker, end_marker, max_blocks=10):
    """
    1) .h 파일 파싱 → Marker 구간 → #if~#else 블록 최대 10개 파싱
    2) 사용자에게 A/B/Skip 선택 UI 제공
    3) '최종 라인 생성' 버튼 누르면 session_state['parsed_list'] 에 저장 (라인별)
       - 예) ["450,05,NR_NSA|NR_SA,1", "123,999F,NR_VONR,2"] 등
    """
    if "parsed_list" not in st.session_state:
        st.session_state["parsed_list"] = []
    if "parsed_once" not in st.session_state:
        st.session_state["parsed_once"] = False
    # pblocks, normal_lines, block_choices 등 초기화
    # ...

    st.info("parse_h_minimal() 작동 중... #if 블록 파싱 & A/B/Skip 선택을 여기서 구현")

    # 예) 임시 데모 버튼
    if st.button("(데모) 파싱 완료 후 parsed_list 저장"):
        st.session_state["parsed_list"] = [
            "450,05,NR_NSA|NR_SA,1",      # mode=1(ALLOW_LIST)
            "123,999F,NR_VONR,2",        # mode=2(BLOCK_LIST)
            "999,111F,NR_DSS|NR_SA_NRCA,1"
        ]
        st.success("parsed_list 3줄 임시 저장 완료!")


def do_final_processing():
    """
    1) session_state['parsed_list'] → 각 라인 파싱
    2) DataFrame으로 변환 → session_state['final_df'] 저장
    3) (mode=1 => ALLOW_LIST, mode=2 => BLOCK_LIST)
    """
    if "parsed_list" not in st.session_state:
        st.warning("parsed_list가 없습니다.")
        return

    raw_list = st.session_state["parsed_list"]
    if not raw_list:
        st.warning("parsed_list가 비어있습니다.")
        return

    rows = []
    for line in raw_list:
        line = line.strip()
        if not line:
            continue
        parts = line.split(",")
        if len(parts) < 4:
            st.warning(f"형식이 맞지 않은 라인: {line}")
            continue

        mcc = parts[0].strip()
        mnc = parts[1].strip()
        feat_str = parts[2].strip()   # 예: "NR_NSA|NR_SA"
        mode_str = parts[3].strip()   # "1" or "2"

        mcc_mnc = mcc + mnc
        features = [f.strip() for f in feat_str.split("|") if f.strip()]

        try:
            mode_val = int(mode_str)  # 1 or 2
        except:
            mode_val = 0

        for feat in features:
            rows.append({
                "MCC_MNC": mcc_mnc,
                "Feature": feat,
                "MODE": mode_val
            })

    if not rows:
        st.warning("전처리 결과가 없습니다.")
        return

    df = pd.DataFrame(rows, columns=["MCC_MNC", "Feature", "MODE"])
    st.session_state["final_df"] = df
    st.success("final_df 생성 완료: st.session_state['final_df']")
```

---

## 동작 요약

1. **`carrier_feature_generator.py`**  
   - 파일 업로드 & Marker 설정.  
   - **`parse_h_minimal(...)`** 호출 → #if 블록 파싱 & A/B/Skip 선택, 최종적으로 **`st.session_state["parsed_list"]`**(문자열 목록) 생성.  
   - **"전처리 + DF 생성"** 버튼 클릭 → `do_final_processing()` → 결과를 `st.session_state["final_df"]`에 저장.  
   - **ALLOW_LIST (mode=1) / BLOCK_LIST (mode=2)** 별로 미리보기(상위 5행) + 통계 + 전체 DataFrame 표시.

2. **`file_utils.py`**  
   - **`parse_h_minimal(...)`**: **스켈레톤**으로, 내부에서 실제 구간 & #if 파싱 로직을 구현. **데모용**으로 `st.session_state["parsed_list"]` 에 간단한 예시 라인만 저장.  
   - **`do_final_processing()`**: `parsed_list`를 파싱 → **DataFrame**(`final_df`) 생성 & 저장.

이를 통해 **사용자**는 **한 번의 버튼 클릭**으로 최종 전처리와 DF 생성까지 완료하고, ALLOW_LIST/BLOCK_LIST 통계 및 전체 데이터를 확인할 수 있습니다.
