---
created: 2025-03-25T11:50:35+09:00
modified: 2025-03-25T11:51:04+09:00
---

# 2025-03-25_file_utils.py#6

아래 코드는 **`do_final_processing()`** 함수를 **간결화**하여,  
1) **이전 단계**(예: `parse_h_minimal`)에서 이미 “최종 라인” 또는 “중괄호 추출 리스트”가 **`st.session_state["parsed_list"]`** 같은 변수에 저장되어 있다고 가정,  
2) 그 **`parsed_list`**의 각 문자열을 파싱하여 **MCC_MNC**, **Feature(7가지 중 하나)**, **MODE(ALLOW_LIST, BLOCK_LIST)**를 해석,  
3) **MCC_MNC**를 오름차순 정렬하여 **ALLOW_LIST**와 **BLOCK_LIST**를 **각각** DataFrame으로 출력,  
4) Feature들은 **True/False** 컬럼으로 표현하는 예시입니다.

> **주의**:  
> - 실제 **`parsed_list`**에 어떤 형태의 문자열이 들어있는지(예: `"NR_NSA,\"450\",\"05\",ALLOW_LIST"`)에 따라 **split/정규표현식** 등을 조정해야 합니다.  
> - 여기서는 예시로 **`Feature,"AAA","BBB",MODE`** 형태로 가정합니다.  
> - 또, 여러 줄에 걸쳐 동일한 `MCC_MNC+MODE`가 여러 Feature를 가질 수도 있으므로, **중복 병합** 로직을 포함합니다.

---

## 예시 코드

```python
import streamlit as st
import pandas as pd
import re

def do_final_processing():
    """
    - st.session_state['parsed_list'] 안에 문자열들이 있다고 가정
    - 각 문자열 형식 예: "NR_NSA,\"450\",\"05\",ALLOW_LIST"
        1) Feature: "NR_NSA", "NR_DSS", ... (총 7가지 중 하나)
        2) MCC: "450" (숫자, 문자 F 가능)
        3) MNC: "05"  (숫자, 문자 F 가능)
        4) MODE: "ALLOW_LIST" or "BLOCK_LIST"
    - MCC + MNC -> 'MCC_MNC'로 합침
    - 7개 Feature 각각 True/False로 저장
    - 최종적으로 ALLOW_LIST / BLOCK_LIST 각각을 MCC_MNC 오름차순 정렬로 표시
    """

    # 1) parsed_list 가져오기
    if "parsed_list" not in st.session_state:
        st.error("parsed_list가 없습니다. 먼저 파싱 과정을 진행해주세요.")
        return

    parsed_list = st.session_state["parsed_list"]
    if not parsed_list:
        st.warning("parsed_list가 비어있습니다.")
        return

    # 2) 변환을 위한 준비
    # 7개 Feature 목록
    all_features = ["NR_NSA", "NR_DSS", "NR_SA", "NR_SA_DSS", "NR_VONR", "NR_NSA_NRCA", "NR_SA_NRCA"]

    # (MCC_MNC, mode) 별로 Feature 상태를 딕셔너리에 저장
    # 구조: data_map[(mcc_mnc, mode)] = {NR_NSA: bool, NR_DSS: bool, ...}
    data_map = {}

    # 3) 각 라인(문자열) 파싱
    # 예: line = "NR_NSA,\"450\",\"05\",ALLOW_LIST"
    for line in parsed_list:
        line = line.strip()
        if not line:
            continue

        # 간단 split 예시(쉼표 기준). 실제 형태에 맞게 조정.
        parts = line.split(",")
        # 기대: parts[0] = "NR_NSA"
        #       parts[1] = "\"450\""
        #       parts[2] = "\"05\""
        #       parts[3] = "ALLOW_LIST"  or "BLOCK_LIST"
        if len(parts) < 4:
            # 형식이 다르면 스킵 or 에러처리
            st.warning(f"형식이 올바르지 않은 라인: {line}")
            continue

        feature_raw = parts[0].strip()
        mcc_raw = parts[1].strip().strip('"')
        mnc_raw = parts[2].strip().strip('"')
        mode_raw = parts[3].strip()

        # MCC_MNC 결합
        mcc_mnc = mcc_raw + mnc_raw  # 예: "450" + "05" -> "45005"

        # (mcc_mnc, mode) 키 생성
        key = (mcc_mnc, mode_raw)

        # data_map에 없으면 초기화
        if key not in data_map:
            data_map[key] = {f: False for f in all_features}

        # feature_raw가 all_features 중 하나면 True로 설정
        if feature_raw in all_features:
            data_map[key][feature_raw] = True
        else:
            st.warning(f"알 수 없는 Feature: {feature_raw}")

    # 4) data_map -> DataFrame 변환
    #    컬럼: MCC_MNC, MODE, NR_NSA, NR_DSS, ...
    rows = []
    for (mcc_mnc, mode), feat_dict in data_map.items():
        row = {
            "MCC_MNC": mcc_mnc,
            "MODE": mode,
        }
        row.update(feat_dict)
        rows.append(row)

    df_all = pd.DataFrame(rows)
    if df_all.empty:
        st.warning("변환 결과가 없습니다.")
        return

    # 5) ALLOW_LIST, BLOCK_LIST 분리 후 정렬
    df_allow = df_all[df_all["MODE"] == "ALLOW_LIST"].copy()
    df_block = df_all[df_all["MODE"] == "BLOCK_LIST"].copy()

    # MCC_MNC 오름차순 정렬
    # MCC_MNC가 숫자+F 형태이므로 단순 문자 정렬 시 "45005" < "999F" 등 
    # 실제 로직에 맞게 정렬 필요(문자열로도 충분할 수 있음)
    df_allow.sort_values(by="MCC_MNC", inplace=True)
    df_block.sort_values(by="MCC_MNC", inplace=True)

    # 6) 결과 출력
    st.success("최종 변환 결과 (ALLOW_LIST / BLOCK_LIST)")
    st.markdown("**ALLOW_LIST**")
    st.dataframe(df_allow)

    st.markdown("**BLOCK_LIST**")
    st.dataframe(df_block)

    # 필요 시 df_allow, df_block 반환
    return (df_allow, df_block)
```

---

## 코드 흐름 설명

1. **`parsed_list`**:  
   - 이전 파싱 단계에서 중괄호 추출한 문자열들이 저장된 상태(예: `["NR_NSA,\"450\",\"05\",ALLOW_LIST", ...]`).

2. **라인 파싱**(쉼표 Split)  
   - 예: `parts[0] = "NR_NSA"`, `parts[1] = "\"450\""`, `parts[2] = "\"05\""`, `parts[3] = "ALLOW_LIST"`  
   - **MCC** + **MNC**를 합쳐 `MCC_MNC`로 구성 (예: `"450" + "05"` → `"45005"`).  
   - `feature_raw`가 7개 Feature 중 하나이면 True, 아니면 경고.

3. **`(MCC_MNC, MODE)`**(예: `("45005", "ALLOW_LIST")`)를 키로 사용하는 `data_map` 딕셔너리.  
   - 값: `{ "NR_NSA": True/False, "NR_DSS": True/False, ... }`

4. **DataFrame 변환**  
   - 열: `["MCC_MNC", "MODE", "NR_NSA", "NR_DSS", ..., "NR_SA_NRCA"]`

5. **ALLOW_LIST / BLOCK_LIST**로 분리 후 **MCC_MNC** 오름차순 정렬, 화면 표시.

---

## 최종 사용 예

```python
# carrier_feature_generator.py (발췌)
from modules.file_utils import parse_h_minimal
from modules.file_utils import do_final_processing

def run(is_admin=False):
    import streamlit as st

    st.subheader("Carrier Feature Generator")

    # 1) Marker 설정, 파일 업로드
    start_marker = st.text_input("Start Marker", "BEGIN_FEATURE")
    end_marker = st.text_input("End Marker", "END_FEATURE")
    uploaded_file = st.file_uploader("업로드(.h)", type=["h"])

    if uploaded_file:
        # (A) 구간 + #if 파싱 + A/B/Skip 선택
        parse_h_minimal(uploaded_file, start_marker, end_marker, max_blocks=10)

        # (B) '최종 전처리' 버튼 → do_final_processing
        if st.button("최종 전처리"):
            do_final_processing()

    else:
        st.info("파일(.h)을 업로드하세요.")
```

### 동작 요약

1. **`parse_h_minimal`**:  
   - Start/End Marker로 구간 필터,  
   - #if/#else/#endif로 최대 10개 블록 파싱,  
   - A/B/Skip 선택 UI 표시,  
   - **최종 라인 구성은 안 함**.

2. **사용자**가 **“최종 전처리”** 버튼 클릭 → **`do_final_processing()`**:  
   - 이미 세션에 저장된 `pblocks`, `block_choices` 등으로 최종 라인 구성,  
   - `{...}` 추출 결과가 **`st.session_state["parsed_list"]`** 또는 별도 변수에 있다면 사용,  
   - **MCC/MNC**/MODE/Feature bool 변환,  
   - **ALLOW_LIST**, **BLOCK_LIST** 정렬 후 표시.

---

이로써 **코드가 길어지거나 복잡해지는 부분**을 두 함수(`parse_h_minimal`, `do_final_processing`)로 나누고,  
최종 전처리(DF 변환, ALLOW/BLOCK 분리) 로직을 별도 함수로 **간결**하게 유지할 수 있습니다.  

프로젝트 요구사항(문자열 형식, Feature / MCC_MNC 규칙)에 맞춰 문자열 파싱을 조정해 보세요.  
**성공적인 개발**을 응원합니다!
