---
created: 2025-03-25T11:34:40+09:00
modified: 2025-03-25T11:34:56+09:00
---

# 2025-03-25-file_utils.py#5

아래 예시는 **`file_utils.py`**를 **단순화**하여,  
1) **Marker 구간**과 **#if / #else / #endif** 구문을 파싱하고,  
2) 사용자에게 A/B/Skip 선택 UI를 제공(블록별 표시)한 뒤,  
**최종 라인을 구성**하는 **실질적인 전처리(DF 변환 등)는 다른 함수**에서 진행하도록 분리한 예시입니다.

---

## 1) `file_utils.py` (단순화)

```python
import streamlit as st

def parse_h_minimal(uploaded_file, start_marker, end_marker, max_blocks=10):
    """
    파일을 메모리에서 읽어:
      1) start_marker ~ end_marker 구간만 추출
      2) 구간 내 최대 max_blocks개의 #if ~ #else ~ #endif 블록 파싱
         - A 블록(#if ~ #else 직전까지), B 블록(#else ~ #endif)
         - #if/#else/#endif 줄도 함께 저장
      3) 세션 상태에 파싱 결과 저장 (pblocks, normal_lines)
      4) 각 블록의 A/B 내용 표시 + radio로 사용자가 A/B/Skip 선택
         (단, 최종 라인 합치기와 DataFrame 변환은 하지 않음!)
    """

    if "pblocks" not in st.session_state:
        st.session_state["pblocks"] = []   # [(a_lines, b_lines, block_idx), ...]
    if "normal_lines" not in st.session_state:
        st.session_state["normal_lines"] = []
    if "block_choices" not in st.session_state:
        st.session_state["block_choices"] = {}
    if "parsed_once" not in st.session_state:
        st.session_state["parsed_once"] = False

    # 파일 라인 분할 (메모리)
    lines = uploaded_file.read().decode("utf-8", errors="replace").splitlines()

    # (1) Start/End 구간 추출
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

    # 이미 파싱하지 않았다면, 블록 파싱
    if not st.session_state["parsed_once"]:
        st.session_state["pblocks"].clear()
        st.session_state["normal_lines"].clear()
        st.session_state["block_choices"].clear()

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
                current_a = [line]  # #if 줄 포함
                current_b = []
                continue
            if s.startswith("#else") and in_block and reading_a:
                # #else 줄도 A 블록에 포함
                current_a.append(line)
                reading_a = False
                reading_b = True
                continue
            if s.startswith("#endif") and in_block:
                # #endif 줄을 현재 읽고 있는 블록(A/B)에 포함
                if reading_a:
                    current_a.append(line)
                else:
                    current_b.append(line)
                # 블록 하나 완성
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
        st.info("파싱 완료. 아래 블록별로 A/B 선택 가능합니다.")
    else:
        st.info("이미 파싱된 상태입니다. 블록 선택을 수정할 수 있습니다.")

    # (2) 블록별 A/B/Skip 선택 UI 표시 (단, 최종 처리는 이 함수에서 하지 않음)
    for (a_lines, b_lines, block_idx) in st.session_state["pblocks"]:
        st.markdown(f"### Block #{block_idx+1}")
        with st.expander(f"A 블록 (#{block_idx+1})"):
            st.code("\n".join(a_lines), language="c")
        with st.expander(f"B 블록 (#{block_idx+1})"):
            st.code("\n".join(b_lines), language="c")

        old_choice = st.session_state["block_choices"].get(block_idx, "A")
        choice = st.radio(
            f"Block #{block_idx+1} 선택",
            ["A", "B", "Skip"],
            index=(0 if old_choice == "A" else (1 if old_choice=="B" else 2)),
            key=f"block_{block_idx}"
        )
        st.session_state["block_choices"][block_idx] = choice

    st.markdown("---")
    st.write("※ 이 함수는 여기까지 수행하고, 최종 라인 구성 및 DF 변환은 별도의 함수에서 처리.")
```

이렇게 하면 **파일 파싱 + 블록별 A/B 선택 UI**까지만 담당하고,  
최종 라인 합치기, `{...}` 추출, DataFrame 변환 등은 하지 않아 코드가 한결 간결해집니다.

---

## 2) 최종 전처리 함수 (별도 작성)

이제 **사용자**가 “최종 전처리” 버튼을 누르면,  
아래 함수(예시)를 호출하여 **블록 선택**에 따른 **최종 라인**을 구성하고,  
각 라인에서 **`{ ... }`** 추출 후 DataFrame으로 보여주도록 합니다.

```python
import re
import pandas as pd
import streamlit as st

def do_final_processing():
    """
    session_state에 저장된 pblocks, normal_lines, block_choices를 사용해
    1) 최종 라인 구성 (A/B/Skip)
    2) 각 라인에서 '{...}' 추출
    3) DataFrame 생성 및 반환 (또는 화면 표시)
    """
    if "pblocks" not in st.session_state or "block_choices" not in st.session_state:
        st.error("먼저 파일을 파싱해주세요.")
        return

    final_lines = []
    # normal_lines 먼저 추가
    normal_lines = st.session_state.get("normal_lines", [])
    final_lines.extend(normal_lines)

    # 블록 A/B/Skip
    for (a_lines, b_lines, idx) in st.session_state["pblocks"]:
        user_choice = st.session_state["block_choices"].get(idx, "A")
        if user_choice == "A":
            final_lines.extend(a_lines)
        elif user_choice == "B":
            final_lines.extend(b_lines)
        else:
            # Skip
            pass

    # 중괄호 추출
    curly_pattern = re.compile(r'\{([^}]*)\}')
    parsed_list = []
    for line in final_lines:
        matches = curly_pattern.findall(line)
        for m in matches:
            parsed_list.append(m.strip())

    # DataFrame 변환
    df = pd.DataFrame(parsed_list, columns=["curly_content"])

    # 사용자에게 표시
    st.success("최종 전처리 결과")
    st.dataframe(df)

    # 필요 시 df 반환 가능
    return df
```

위 함수는  
- `pblocks`, `normal_lines`, `block_choices`(파일 파싱 결과 및 사용자 결정)를 불러오고,  
- 최종 라인을 구성한 다음, `{...}` 부분을 정규표현식으로 추출,  
- **DataFrame** 생성 및 표시.

---

## 3) 사용하는 예시 (carrier_feature_generator.py)

```python
# carrier_feature_generator.py
import streamlit as st
from modules.file_utils import parse_h_minimal
from modules.file_utils import do_final_processing  # or define in another file

def run(is_admin=False):
    st.subheader("Carrier Feature Generator - 간단 구조")

    start_marker = st.text_input("Start Marker", "BEGIN_FEATURE")
    end_marker = st.text_input("End Marker", "END_FEATURE")
    uploaded_file = st.file_uploader("업로드 (.h)", type=["h"])

    if uploaded_file:
        # (A) 파일 파싱 + 블록 A/B 선택
        parse_h_minimal(
            uploaded_file=uploaded_file,
            start_marker=start_marker,
            end_marker=end_marker,
            max_blocks=10
        )

        # (B) 최종 전처리 실행 버튼
        if st.button("최종 전처리 → DF 변환"):
            do_final_processing()
    else:
        st.info("파일(.h)을 업로드해 주세요.")
```

1. 사용자가 **Start/End Marker**와 **.h 파일** 업로드 → `parse_h_minimal` 호출  
   - 이 함수가 **블록 파싱** & **A/B/Skip** UI 표시 (단, 최종 처리 X)  
2. 사용자 선택 후 **“최종 전처리 → DF 변환”** 버튼 클릭 → `do_final_processing()`  
   - **최종 라인** 구성 + **`{...}`** 추출 → **DataFrame** 표시

---

## 요약

- **`file_utils.py`**:  
  1) `parse_h_minimal(...)`: **구간 + #if 블록** 파싱, 세션 상태에 저장, 블록별 A/B 선택 UI 표시. **최종 결과 DF 변환은 안 함**  
  2) `do_final_processing()`: **사용자 결정**(A/B/Skip)에 따른 최종 라인 합치기, **`{...}`** 추출, **DataFrame** 출력  
- **`carrier_feature_generator.py`**:  
  - 업로드 파일 & Marker 입력 → `parse_h_minimal` → 최종 전처리 버튼 → `do_final_processing`

이렇게 구조를 두 함수로 **분리**함으로써, **파일 파싱 & UI**와 **최종 전처리(DF 변환)**를 구분해 **코드가 간단**해집니다.  
추가적으로 **중첩 구조** 등은 요구사항에 맞게 확장하면 됩니다.
