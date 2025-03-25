---
created: 2025-03-25T17:20:41+09:00
modified: 2025-03-25T17:21:12+09:00
---

# 2025-03-25-file_utils.py

아래는 **이전에 작성했던 `parse_h_minimal()`** 함수를 **두 부분**(**`parse_nonblock_lines()`**, **`parse_block_lines()`**)로 나눈 예시입니다.  

1. **`parse_nonblock_lines()`**: 업로드된 파일에서 일반 라인과 블록 후보 라인(= #if / #else / #endif 등)을 나누어 **`normal_lines`**와 **`block_candidates`**에 저장.  
2. **`parse_block_lines()`**: **`block_candidates`**를 분석하여 A/B/Skip 블록 선택 UI를 제공하고, 최종 결정된 라인들을 **`block_lines`**로 저장.

마지막에 **`finalize_merged_lines()`**에서 **`normal_lines + block_lines`** 합치는 구조는 기존과 동일하게 유지하시면 됩니다.

---

## file_utils.py (수정 예시)

```python
import streamlit as st
import pandas as pd

##############################################################
# parse_nonblock_lines()
##############################################################
def parse_nonblock_lines(uploaded_file, start_marker="BEGIN_FEATURE", end_marker="END_FEATURE"):
    """
    1) 업로드된 .h 파일을 메모리에서 읽어서
       start_marker ~ end_marker 구간을 추출(이전 parse_h_minimal의 capturing)
    2) 구간 내에서 #if/#else/#endif 처리를 위해 'block_candidates'로 분류,
       그 외는 'normal_lines'로 저장
    """

    st.info("parse_nonblock_lines() - 이전 parse_h_minimal() 일부 로직 사용")

    # 세션 스테이트 초기화
    if "normal_lines" not in st.session_state:
        st.session_state["normal_lines"] = []
    if "block_candidates" not in st.session_state:
        st.session_state["block_candidates"] = []
    if "parsed_once" not in st.session_state:
        st.session_state["parsed_once"] = False

    # (A) 파일 라인
    lines = uploaded_file.read().decode("utf-8", errors="replace").splitlines()

    # (B) start_marker / end_marker 구간 추출 (capturing)
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

    # 첫 실행 시
    if not st.session_state["parsed_once"]:
        st.session_state["normal_lines"].clear()
        st.session_state["block_candidates"].clear()

        # 이전 parse_h_minimal에서는 #if로 in_block, reading_a/b 등 처리했지만,
        # 여기서는 단순히 #if/#else/#endif 포함 라인을 block_candidates로,
        # 나머지는 normal_lines로 보낸다고 가정 (또는 원하는 로직 적용)
        for cl in captured_lines:
            s = cl.strip()
            if s.startswith("#if") or s.startswith("#else") or s.startswith("#endif"):
                # 블록 후보
                st.session_state["block_candidates"].append(cl)
            else:
                # 일반 라인
                st.session_state["normal_lines"].append(cl)

        st.session_state["parsed_once"] = True
        st.success(f"parse_nonblock_lines() 완료: normal_lines={len(st.session_state['normal_lines'])}, block_candidates={len(st.session_state['block_candidates'])}")
    else:
        st.info("이미 parse_nonblock_lines()를 실행했습니다. 재실행은 생략.")


##############################################################
# parse_block_lines()
##############################################################
def parse_block_lines():
    """
    1) block_candidates(이전 단계에서 추출) → A/B 블록 분석
    2) 사용자 A/B/Skip 라디오
    3) 최종 결정된 라인들을 block_lines에 저장
    """

    st.info("parse_block_lines() - 이전 parse_h_minimal() 나머지 로직 활용")

    if "block_candidates" not in st.session_state:
        st.warning("block_candidates가 없습니다. parse_nonblock_lines() 먼저 실행 필요")
        return

    if "block_lines" not in st.session_state:
        st.session_state["block_lines"] = []
    if "block_choices" not in st.session_state:
        st.session_state["block_choices"] = {}
    if "parsed_blocks" not in st.session_state:
        st.session_state["parsed_blocks"] = []
    if "blocks_parsed" not in st.session_state:
        st.session_state["blocks_parsed"] = False

    # 한 번도 안 했으면, A/B 블록 구성
    if not st.session_state["blocks_parsed"]:
        st.session_state["parsed_blocks"].clear()
        st.session_state["block_choices"].clear()
        st.session_state["block_lines"].clear()

        # 예시) block_candidates 전체를 반으로 나누어 A/B 블록 1개만 만든다
        # 실제로는 #if, #else, #endif 분석하여 여러 블록 만들 수 있음
        bc = st.session_state["block_candidates"]
        half_idx = len(bc)//2
        a_lines = bc[:half_idx]
        b_lines = bc[half_idx:]
        st.session_state["parsed_blocks"].append((a_lines, b_lines, 0))

        st.session_state["blocks_parsed"] = True
        st.success("parse_block_lines() - 블록 파싱 완료")

    # UI
    for (a_lines, b_lines, idx) in st.session_state["parsed_blocks"]:
        st.markdown(f"### Block #{idx+1}")
        with st.expander(f"A 블록(#{idx+1})"):
            st.code("\n".join(a_lines), language="c")
        with st.expander(f"B 블록(#{idx+1})"):
            st.code("\n".join(b_lines), language="c")

        old_choice = st.session_state["block_choices"].get(idx, "A")
        choice = st.radio(
            f"Block #{idx+1} 선택",
            ["A", "B", "Skip"],
            index=(0 if old_choice=="A" else (1 if old_choice=="B" else 2)),
            key=f"block_{idx}"
        )
        st.session_state["block_choices"][idx] = choice

    if st.button("블록 선택 확정"):
        # 최종 라인
        st.session_state["block_lines"].clear()
        for (a_lines, b_lines, idx) in st.session_state["parsed_blocks"]:
            user_choice = st.session_state["block_choices"].get(idx, "A")
            if user_choice == "A":
                st.session_state["block_lines"].extend(a_lines)
            elif user_choice == "B":
                st.session_state["block_lines"].extend(b_lines)
            else:
                pass  # skip
        st.success(f"블록 라인 {len(st.session_state['block_lines'])}개 선택 완료")
```

---

### 핵심 변경점 (이전 parse_h_minimal 대비)

1. **`parse_nonblock_lines()`**  
   - `start_marker ~ end_marker` 구간 캡처 (capturing) → 라인별로  
   - `#if/#else/#endif` 등은 **`block_candidates`**에, 나머지는 **`normal_lines`**에 저장.  
   - (`parsed_once` 이용해 중복 실행 방지)

2. **`parse_block_lines()`**  
   - **`block_candidates`**를 이용해 A/B 블록 구성(간단 예시)  
   - 사용자에게 A/B/Skip 라디오 UI → “블록 선택 확정” 버튼 클릭 시, **`block_lines`**에 최종 결정 라인 저장.

---

## finalize_merged_lines() (참고)

기존 예시와 동일하게, **normal_lines** + **block_lines**를 합쳐 **parsed_list**를 만들면 됩니다.

```python
def finalize_merged_lines():
    if "normal_lines" not in st.session_state or "block_lines" not in st.session_state:
        st.warning("normal_lines 혹은 block_lines가 없습니다.")
        return

    if "parsed_list" not in st.session_state:
        st.session_state["parsed_list"] = []

    merged = st.session_state["normal_lines"] + st.session_state["block_lines"]
    st.session_state["parsed_list"].clear()
    st.session_state["parsed_list"].extend(merged)

    st.success(f"최종 라인 {len(merged)}개 병합 완료 → parsed_list에 저장됨.")
```

---

### carrier_feature_generator.py (간단 흐름)

```python
def run(is_admin=False):
    import streamlit as st
    from modules.file_utils import parse_nonblock_lines, parse_block_lines, finalize_merged_lines

    st.title("Carrier Feature Generator (분리 버전)")

    new_format = st.checkbox("NEW FORMAT", value=False)
    uploaded_file = None
    if not new_format:
        uploaded_file = st.file_uploader(".h 파일 업로드", type=["h"])
        if uploaded_file:
            if st.button("1) 일반 라인 파싱"):
                parse_nonblock_lines(uploaded_file)
            if st.button("2) 블록 선택"):
                parse_block_lines()
            if st.button("3) 병합"):
                finalize_merged_lines()
    else:
        st.info("NEW FORMAT => 파일 업로드 불필요")
    
    if "parsed_list" in st.session_state and st.session_state["parsed_list"]:
        st.write("**parsed_list 미리보기**")
        st.code("\n".join(st.session_state["parsed_list"]))
```

---

## 요약

- **parse_nonblock_lines()**: 원래 `parse_h_minimal()`에서 **start_marker/end_marker** 구간 캡처 로직을 떼어내, **블록 후보** vs **일반 라인** 분리만 수행.  
- **parse_block_lines()**: 남은 코드(블록 A/B/Skip UI)를 떼어내, **block_candidates** 활용해 라인 구성, 최종 결과는 **block_lines**에 저장.  
- **finalize_merged_lines()**: **normal_lines + block_lines** 합쳐 **parsed_list**로 저장.

이렇게 분리하면, **이전 `parse_h_minimal()`** 로직을 **2개 함수**로 나누어,  
**일반 라인/블록 후보** → **A/B 선택** 과정을 명확히 구분할 수 있습니다.
