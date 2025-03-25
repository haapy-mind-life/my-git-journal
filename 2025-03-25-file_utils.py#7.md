---
created: 2025-03-25T12:00:13+09:00
modified: 2025-03-25T12:00:33+09:00
---

# 2025-03-25-file_utils.py#7

아래 예시는 **`parse_h_minimal()`** 함수에서 최종 결과(사용자가 A/B/Skip 결정한 라인들)를 **`st.session_state["parsed_list"]`**에 저장해두고,  
**`do_final_processing()`** 함수가 그 **`parsed_list`**를 활용해 **DataFrame**을 생성하는 흐름을 구현한 예시입니다.

---

## 1) `parse_h_minimal()` 수정

```python
import streamlit as st

def parse_h_minimal(uploaded_file, start_marker, end_marker, max_blocks=10):
    """
    1) 파일을 메모리에서 읽어 start_marker ~ end_marker 구간 추출
    2) 구간 내 최대 max_blocks개의 #if ~ #else ~ #endif 블록 파싱
       - A 블록, B 블록, Skip
    3) 블록별로 A/B 코드 표시 + 사용자가 라디오로 선택
    4) 이 함수 내에서 '최종 라인'을 구성하여 st.session_state['parsed_list']에 저장
       - 여기서는 예시로 '123', '456', 'NR_NSA | NR_SA, ALLOW_LIST' 등 문자열을 담는다.
    """

    # 세션 상태 준비
    if "pblocks" not in st.session_state:
        st.session_state["pblocks"] = []
    if "normal_lines" not in st.session_state:
        st.session_state["normal_lines"] = []
    if "block_choices" not in st.session_state:
        st.session_state["block_choices"] = {}
    if "parsed_once" not in st.session_state:
        st.session_state["parsed_once"] = False
    # 최종 결과 리스트
    if "parsed_list" not in st.session_state:
        st.session_state["parsed_list"] = []

    # 파일 라인 분할
    lines = uploaded_file.read().decode("utf-8", errors="replace").splitlines()

    # start_marker/end_marker 구간 추출
    capturing = False
    captured_lines = []
    for line in lines:
        if start_marker in line:
            capturing = True
            continue
        if end_marker in line:
            capturing = False
            continue
        if capturing:
            captured_lines.append(line)

    # 최초 파싱만 수행
    if not st.session_state["parsed_once"]:
        st.session_state["pblocks"].clear()
        st.session_state["normal_lines"].clear()
        st.session_state["block_choices"].clear()
        st.session_state["parsed_list"].clear()

        block_count = 0
        in_block = False
        reading_a = False
        reading_b = False
        current_a = []
        current_b = []
        normal_captured = []

        for line in captured_lines:
            if block_count >= max_blocks:
                normal_captured.append(line)
                continue

            s = line.strip()
            if s.startswith("#if") and not in_block:
                in_block = True
                reading_a = True
                reading_b = False
                current_a = [line]  # #if 포함
                current_b = []
                continue
            if s.startswith("#else") and in_block and reading_a:
                current_a.append(line)
                reading_a = False
                reading_b = True
                continue
            if s.startswith("#endif") and in_block:
                if reading_a:
                    current_a.append(line)
                else:
                    current_b.append(line)
                st.session_state["pblocks"].append((current_a, current_b, block_count))
                block_count += 1
                in_block = False
                reading_a = False
                reading_b = False
                current_a = []
                current_b = []
                continue

            if in_block:
                if reading_a:
                    current_a.append(line)
                elif reading_b:
                    current_b.append(line)
            else:
                normal_captured.append(line)

        st.session_state["normal_lines"] = normal_captured
        st.session_state["parsed_once"] = True
        st.info("파싱 완료. 블록 선택 후 '최종 라인 생성' 버튼을 클릭하세요.")
    else:
        st.info("이미 파싱된 상태입니다. 블록 선택을 수정할 수 있습니다.")

    # 블록별 UI
    for (a_lines, b_lines, idx) in st.session_state["pblocks"]:
        st.markdown(f"### Block #{idx+1}")
        with st.expander(f"A 블록(#{idx+1})"):
            st.code("\n".join(a_lines), language="c")
        with st.expander(f"B 블록(#{idx+1})"):
            st.code("\n".join(b_lines), language="c")

        prev_choice = st.session_state["block_choices"].get(idx, "A")
        choice = st.radio(
            f"Block #{idx+1} 선택",
            ["A", "B", "Skip"],
            index=(0 if prev_choice=="A" else (1 if prev_choice=="B" else 2)),
            key=f"block_{idx}"
        )
        st.session_state["block_choices"][idx] = choice

    # 최종 라인 생성 버튼
    if st.button("최종 라인 생성"):
        final_lines = []
        # normal 먼저
        final_lines.extend(st.session_state["normal_lines"])
        # 블록들
        for (a_lines, b_lines, idx) in st.session_state["pblocks"]:
            user_choice = st.session_state["block_choices"].get(idx, "A")
            if user_choice == "A":
                final_lines.extend(a_lines)
            elif user_choice == "B":
                final_lines.extend(b_lines)
            else:
                # Skip
                pass

        # 여기서는 예시로,
        # final_lines의 첫 2개 라인을 "123", "456"이라 가정 (MCC, MNC)
        # 그다음 "NR_NSA | NR_SA | NR_VONR, ALLOW_LIST" 같은 문자열이 있을 수 있음
        # 실제 로직에 맞게 변환(여기선 단순 저장만)
        st.session_state["parsed_list"].clear()

        # 간단 예시: final_lines를 st.session_state["parsed_list"]에 그대로 저장
        # 실제로는 라인별 필터링/치환/추출 로직을 추가 가능
        for ln in final_lines:
            if ln.strip():
                st.session_state["parsed_list"].append(ln.strip())

        st.success("최종 라인을 parsed_list에 저장했습니다. 이제 do_final_processing()에서 DF로 변환 가능.")
```

### 주요 변경점

- **최종 라인 생성** 버튼을 클릭하면, **사용자 결정(A/B/Skip)**에 따른 라인들을 하나로 합쳐서 **`st.session_state["parsed_list"]`**에 저장.  
- 여기서는 **단순히 `final_lines`를 그대로 저장**하지만, 실제 상황에 맞춰 라인을 가공/치환하여 **`["123", "456", "NR_NSA | NR_SA | ..."]`**와 같은 형식으로 만들면 됩니다.

---

## 2) `do_final_processing()` 함수

```python
import streamlit as st
import pandas as pd

def do_final_processing():
    """
    이전 단계(parse_h_minimal)에서 st.session_state['parsed_list']에
    예: ["123", "456", "NR_NSA | NR_SA | NR_VONR, ALLOW_LIST", ...] 형태로 저장되었다고 가정.
    
    - 앞 2개 라인(예: index 0,1)은 MCC, MNC
    - 그 다음 라인(예: index 2)은 'Feature들, MODE'
      ex) \"NR_NSA | NR_SA | NR_VONR, ALLOW_LIST\"
    - 실제 로직은 프로젝트 상황에 맞춰 확장
    """

    if "parsed_list" not in st.session_state or not st.session_state["parsed_list"]:
        st.warning("parsed_list가 비어있습니다. 먼저 '최종 라인 생성'을 진행해주세요.")
        return
    
    raw_list = st.session_state["parsed_list"]

    # 예시: raw_list = ["123", "456", "NR_NSA | NR_SA | NR_VONR, ALLOW_LIST"]
    if len(raw_list) < 3:
        st.error("데이터가 부족합니다. (MCC, MNC, Feature/MODE 라인이 필요)")
        return

    # (1) MCC = raw_list[0], MNC = raw_list[1]
    mcc = raw_list[0].strip()
    mnc = raw_list[1].strip()
    mcc_mnc = mcc + mnc  # e.g. "123456"

    # (2) Feature / Mode 파싱
    #    raw_list[2] 예: \"NR_NSA | NR_SA | NR_VONR, ALLOW_LIST\"
    #    -> split(',') -> [\"NR_NSA | NR_SA | NR_VONR\", \"ALLOW_LIST\"]
    #    -> feature_part, mode_part
    feature_line = raw_list[2].strip()
    parts = feature_line.split(",")
    if len(parts) < 2:
        st.error("Feature/MODE 라인 파싱 실패.")
        return

    feature_part = parts[0].strip()
    mode_part = parts[1].strip()

    # feature_part 예: \"NR_NSA | NR_SA | NR_VONR\"
    features = [f.strip() for f in feature_part.split("|")]
    # e.g. features = [\"NR_NSA\", \"NR_SA\", \"NR_VONR\"]

    # (3) DataFrame 변환 예시
    #    컬럼: [MCC_MNC, Feature, MODE]
    rows = []
    for feat in features:
        rows.append({
            "MCC_MNC": mcc_mnc,
            "Feature": feat,
            "MODE": mode_part
        })

    df = pd.DataFrame(rows, columns=["MCC_MNC", "Feature", "MODE"])

    # (4) 출력
    st.success("최종 변환 결과")
    st.dataframe(df)
```

### 설명

- **`parsed_list`**에서 MCC, MNC, Feature/MODE 라인을 예시로 추출.  
- `"NR_NSA | NR_SA | NR_VONR, ALLOW_LIST"`를 `split(",")` → `("NR_NSA | NR_SA | NR_VONR", "ALLOW_LIST")` → Feature는 `split("|")`로 나눔.  
- **DataFrame**에 `[MCC_MNC, Feature, MODE]` 형태로 저장.  
- 실제 로직에 따라, **더 많은 라인**을 분석하거나, **오류 처리**, **Feature 7개를 bool 형식**으로 변환하는 등 확장 가능.

---

## 3) 최종 사용 예 (carrier_feature_generator.py)

```python
def run(is_admin=False):
    import streamlit as st
    from modules.file_utils import parse_h_minimal, do_final_processing

    st.subheader("Carrier Feature Generator")

    start_marker = st.text_input("Start Marker", "BEGIN_FEATURE")
    end_marker = st.text_input("End Marker", "END_FEATURE")
    uploaded_file = st.file_uploader("업로드(.h)", type=["h"])

    if uploaded_file:
        parse_h_minimal(uploaded_file, start_marker, end_marker, max_blocks=10)

        st.markdown("---")
        if st.button("최종 전처리 (DF 변환)"):
            do_final_processing()
    else:
        st.info("파일(.h)을 업로드하세요.")
```

---

## 요약

1. **`parse_h_minimal()`**  
   - Marker 구간 → #if 블록 파싱 → A/B/Skip 선택 → 최종 라인 합치기  
   - **결과**를 **`st.session_state["parsed_list"]`**에 저장 (예: `["123", "456", "NR_NSA | NR_SA | NR_VONR, ALLOW_LIST"]`).

2. **`do_final_processing()`**  
   - **`parsed_list`**의 내용을 파싱하여 **DataFrame** 생성,  
   - **MCC/MNC** 결합, Feature 분해, MODE 파악, etc.

이를 통해 **코드를 두 부분**(파싱 vs 최종 변환)으로 나누면서 **단순**화하고,  
사용자는 **“최종 라인 생성”** 후 **“최종 전처리(DF 변환)”** 버튼을 눌러 원하는 결과를 얻을 수 있습니다.
