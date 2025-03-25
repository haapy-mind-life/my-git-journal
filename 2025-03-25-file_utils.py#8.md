---
created: 2025-03-25T12:08:49+09:00
modified: 2025-03-25T12:09:09+09:00
---

# 2025-03-25-file_utils.py#8

아래 예시는 **`do_final_processing()`** 함수를 **간단한** 형태로 작성한 예시입니다.  
- **`raw_list`**(문자열 목록) 각 라인마다 **MCC**, **MNC**, **Feature**, **MODE**를 추출(파싱)  
- Feature가 여러 개 있을 수 있으므로(예: `"NR_NSA|NR_SA|NR_VONR"`), **split**하여 여러 행을 생성  
- 최종적으로 **DataFrame**(`["MCC_MNC", "Feature", "MODE"]`)을 만들어 **출력**하는 흐름을 보여줍니다.

> **가정**:  
> - **`raw_list`**의 각 원소(문자열)는 `","`로 구분된 4가지 구간을 갖습니다.  
>   1) MCC  
>   2) MNC  
>   3) Feature 문자열 (ex: `"NR_NSA|NR_SA|NR_VONR"`)  
>   4) MODE (`"ALLOW_LIST"` 또는 `"BLOCK_LIST"`)  
>   
>   예: `"450,05,NR_NSA|NR_VONR,ALLOW_LIST"`

---

```python
import streamlit as st
import pandas as pd

def do_final_processing():
    """
    - st.session_state['parsed_list'] 가 존재한다고 가정
    - 예: raw_list = [
        \"450,05,NR_NSA|NR_VONR,ALLOW_LIST\",
        \"123,999F,NR_SA,ALLOW_LIST\",
        ...
      ]
    - 각 라인을 ,(쉼표)로 나누어 (MCC, MNC, Feature문자열, MODE) 파싱
    - Feature문자열은 | 로 구분 → 여러 Feature 가능
    - df: [MCC_MNC, Feature, MODE]
    """

    if "parsed_list" not in st.session_state or not st.session_state["parsed_list"]:
        st.warning("parsed_list가 비어있습니다. 먼저 '최종 라인 생성'을 진행해주세요.")
        return

    raw_list = st.session_state["parsed_list"]
    rows = []

    for line in raw_list:
        line = line.strip()
        if not line:
            continue

        # 예) "450,05,NR_NSA|NR_VONR,ALLOW_LIST"
        parts = line.split(",")
        if len(parts) < 4:
            st.warning(f"형식이 올바르지 않은 라인: {line}")
            continue

        mcc = parts[0].strip()
        mnc = parts[1].strip()
        feature_str = parts[2].strip()  # 예: "NR_NSA|NR_VONR"
        mode_str = parts[3].strip()    # 예: "ALLOW_LIST" or "BLOCK_LIST"

        # MCC_MNC 결합
        mcc_mnc = mcc + mnc

        # Feature 문자열 분리( | )
        features = [f.strip() for f in feature_str.split("|") if f.strip()]

        # rows 에 추가
        for feat in features:
            rows.append({
                "MCC_MNC": mcc_mnc,
                "Feature": feat,
                "MODE": mode_str
            })

    if not rows:
        st.warning("데이터가 없습니다.")
        return

    df = pd.DataFrame(rows, columns=["MCC_MNC", "Feature", "MODE"])

    st.success("최종 변환 결과:")
    st.dataframe(df)

    # 필요 시 df 반환
    return df
```

---

### 코드 흐름

1. **`parsed_list`**(SessionState)에 저장된 문자열 목록을 순회.  
2. 각 라인을 **`,`** 기준으로 **MCC, MNC, Feature 문자열, MODE** 추출.  
3. **MCC + MNC** → `"MCC_MNC"` 합치기.  
4. Feature 문자열이 `"NR_NSA|NR_SA|NR_VONR"`처럼 **`|`**로 구분돼 있을 수 있으므로, **split** → 개별 Feature 항목.  
5. 각 Feature를 행으로 만들어 **`rows`**에 누적.  
6. 최종적으로 **pandas DataFrame**을 만들어 **화면 출력**.

---

### 사용 예시

```python
# carrier_feature_generator.py
def run(is_admin=False):
    import streamlit as st
    from modules.file_utils import parse_h_minimal, do_final_processing

    st.subheader("Carrier Feature Generator")

    start_marker = st.text_input("Start Marker", "BEGIN_FEATURE")
    end_marker = st.text_input("End Marker", "END_FEATURE")
    uploaded_file = st.file_uploader("업로드(.h)", type=["h"])

    if uploaded_file:
        # A) Marker 구간 + #if 파싱 + A/B/Skip 결정 → 최종 라인 parsed_list 에 저장
        parse_h_minimal(uploaded_file, start_marker, end_marker, max_blocks=10)

        # B) 최종 전처리
        if st.button("최종 DF 변환"):
            do_final_processing()
    else:
        st.info("파일(.h)을 업로드하세요.")
```

1. **`parse_h_minimal()`**: Start/End Marker 구간 추출, #if/#else/#endif 블록 파싱 & 선택,  
   최종 라인을 **`st.session_state["parsed_list"]`**에 저장(예: `"450,05,NR_NSA|NR_VONR,ALLOW_LIST"` 등).  
2. **`do_final_processing()`**: **`parsed_list`** 각 라인을 `(MCC, MNC, Feature(s), MODE)`로 파싱 → **DataFrame** 생성 및 출력.

이처럼 **각 라인**에 **MCC/MNC/Feature/Mode** 정보가 포함된 문자열을 가정하면,  
라인 수만큼 반복하여 원하는 **DataFrame**을 손쉽게 구성할 수 있습니다.
