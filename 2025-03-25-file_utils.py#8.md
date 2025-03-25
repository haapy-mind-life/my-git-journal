---
created: 2025-03-25T12:08:49+09:00
modified: 2025-03-25T15:36:44+09:00
---

# 2025-03-25-file_utils.py#8

아래는 **최신 버전**의 `file_utils.py` 예시 코드입니다.  
- **`parse_h_minimal()`**:  
  1) 업로드된 `.h` 파일을 메모리에서 **start_marker ~ end_marker** 구간만 추출  
  2) 구간 내 최대 10개의 `#if ~ #else ~ #endif` 블록 파싱  
  3) 사용자에게 블록별로 **A/B/Skip**을 선택할 수 있는 UI 제공  
  4) “최종 라인 생성” 버튼 클릭 시, 결정된 라인을 하나로 합쳐 **`st.session_state["parsed_list"]`** 에 저장  
- **`do_final_processing()`** (스켈레톤):  
  - `st.session_state["parsed_list"]` 를 파싱해 최종 **DataFrame** (`final_df`) 을 생성·저장하는 공간

각 프로젝트 요구에 맞게 상세 로직을 보강해 사용하시면 됩니다.

```python
# file_utils.py (최신 업데이트 예시)

import streamlit as st
import pandas as pd

########################################################
# parse_h_minimal()
########################################################
def parse_h_minimal(uploaded_file, start_marker, end_marker, max_blocks=10):
    """
    1) 업로드된 .h 파일을 메모리에서 읽어서,
       start_marker ~ end_marker 구간만 추출
    2) 구간 내 최대 max_blocks개의 #if ~ #else ~ #endif 블록 파싱 (A/B/Skip)
    3) 사용자가 각 블록에 대해 A/B/Skip을 선택
    4) '최종 라인 생성' 버튼으로 결정된 라인을 합쳐
       session_state["parsed_list"]에 저장
       (예: ["450,05,NR_NSA|NR_SA,1", "123,999F,NR_VONR,2", ...])
    """

    # 세션 상태 준비
    if "parsed_list" not in st.session_state:
        st.session_state["parsed_list"] = []
    if "pblocks" not in st.session_state:
        st.session_state["pblocks"] = []  # [(a_lines, b_lines, block_idx), ...]
    if "normal_lines" not in st.session_state:
        st.session_state["normal_lines"] = []
    if "block_choices" not in st.session_state:
        st.session_state["block_choices"] = {}  # { block_idx: "A"/"B"/"Skip" }
    if "parsed_once" not in st.session_state:
        st.session_state["parsed_once"] = False

    # (A) .h 파일 메모리 읽기
    lines = uploaded_file.read().decode("utf-8", errors="replace").splitlines()

    # (B) start_marker / end_marker 구간 추출
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

    # (C) 최초 파싱(once)
    if not st.session_state["parsed_once"]:
        # 초기화
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

        # 최대 max_blocks개의 #if 블록 파싱
        for line in captured_lines:
            if block_count >= max_blocks:
                # 초과 시 normal_captured에 저장
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
        st.info("구간 및 블록 파싱 완료. 아래에서 Block 선택 진행.")
    else:
        st.info("이미 파싱된 상태. Block 선택을 수정할 수 있습니다.")

    # (D) 블록별 A/B/Skip 선택 UI
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

    st.markdown("---")

    # (E) 최종 라인 생성 버튼
    if st.button("최종 라인 생성"):
        final_lines = []
        # normal_lines 먼저
        final_lines.extend(st.session_state["normal_lines"])
        # 블록들
        for (a_lines, b_lines, idx) in st.session_state["pblocks"]:
            user_choice = st.session_state["block_choices"].get(idx, "A")
            if user_choice == "A":
                final_lines.extend(a_lines)
            elif user_choice == "B":
                final_lines.extend(b_lines)
            else:
                pass  # Skip

        # 여기서 각 라인을 쉼표구분 문자열 등으로 변경해 저장 가능
        # 간단 예시: final_lines 그대로 session_state['parsed_list'] 에 저장
        st.session_state["parsed_list"].clear()
        for ln in final_lines:
            if ln.strip():
                st.session_state["parsed_list"].append(ln.strip())

        st.success("Block 선택을 반영한 최종 라인이 parsed_list에 저장되었습니다!")

########################################################
# do_final_processing() (Skeleton)
########################################################
def do_final_processing():
    """
    1) st.session_state['parsed_list'] 각 라인 파싱
    2) 최종 DataFrame 생성 → st.session_state['final_df'] 에 저장
    """
    st.info("이 함수는 스켈레톤입니다. 실제 로직은 프로젝트 요건에 맞춰 구현")
    if "parsed_list" not in st.session_state:
        st.warning("parsed_list가 비어있습니다.")
        return

    raw_list = st.session_state["parsed_list"]
    if not raw_list:
        st.warning("parsed_list가 비어있습니다.")
        return

    # 예: 각 라인을 'MCC,MNC,FeatureStr,MODE'로 split → DF
    # 아래는 단순 예시
    rows = []
    for line in raw_list:
        # ... 파싱 로직 (split, etc.)
        # rows.append({ ... })
        pass

    # df = pd.DataFrame(rows)
    # st.session_state['final_df'] = df
    # st.success("final_df 생성 완료!")

    st.info("do_final_processing() 로직을 구현해 DF 완성 & 저장하세요.")
```

---

### 사용 흐름

1. **`parse_h_minimal()`**  
   - 업로드된 `.h` 파일을 **start_marker ~ end_marker** 구간으로 제한  
   - **#if ~ #else ~ #endif** 블록을 최대 10개 파싱  
   - 사용자에게 **A/B/Skip** UI 제공  
   - **“최종 라인 생성”** 버튼 클릭 시, 선택된 라인(및 구간 바깥 라인)을 합쳐서 **`st.session_state["parsed_list"]`**에 저장

2. **`do_final_processing()`** (스켈레톤)  
   - **`st.session_state["parsed_list"]`**를 **split/정규표현식** 등으로 가공 → **DataFrame** 생성  
   - **`st.session_state["final_df"]`**에 저장, 필요 시 메시지 표시

이 구조를 바탕으로 **사용자 UI**와 **후속 로직**(예: DF 변환, ALLOW/BLOCK 리스트 분리, 중복 검사 등)을 자유롭게 확장하여 프로젝트에 적용하시면 됩니다.
