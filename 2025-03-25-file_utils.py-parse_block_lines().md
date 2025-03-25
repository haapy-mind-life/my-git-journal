---
created: 2025-03-26T03:00:21+09:00
modified: 2025-03-26T03:00:56+09:00
---

# 2025-03-25-file_utils.py-parse_block_lines()

아래는 **“블록 선택"**을 체크박스(체크리스트) 방식으로 구현한 **`parse_block_lines()`** 함수의 최신 예시입니다.  
- 사용자가 여러 블록 중 원하는 블록을 골라 한 번에 **Confirm** 할 수 있습니다.  
- 각 블록 내 최대 20줄까지만 미리보기 표시(`st.text()`).  
- 최종 선택된 라인을 **`block_lines`**에 저장.  
- **`merged()`**(또는 `finalize_merged_lines()`)는 스켈레톤 코드로 남겨두어, 내부 로직은 사용자가 자유롭게 대체한다는 가정입니다.

---

## parse_block_lines() (최신)

```python
def parse_block_lines():
    import streamlit as st

    """
    st.session_state["block_candidates"] 가 다음과 같은 형태라고 가정:
      [
        [lineA1, lineA2, ...],  # Block 1
        [lineB1, lineB2, ...],  # Block 2
        ...
      ]
    이 함수에서는 각 블록을 체크박스로 선택하여 사용자에게 Confirm 처리.
    선택된 블록 라인을 합쳐 block_lines에 저장.
    """

    if "block_candidates" not in st.session_state:
        st.warning("block_candidates가 없습니다. 이전 단계에서 parse_nonblock_lines() 등을 먼저 실행하세요.")
        return

    blocks = st.session_state["block_candidates"]
    if not blocks:
        st.info("블록 후보가 비어 있습니다. 스킵 가능.")
        return

    # 선택 여부 배열
    if "block_selection" not in st.session_state:
        st.session_state["block_selection"] = [False] * len(blocks)

    # 최종 블록 라인
    if "block_lines" not in st.session_state:
        st.session_state["block_lines"] = []

    st.info("아래 블록 목록 중 원하는 블록을 체크하고, Confirm 버튼을 누르세요.")

    for i, block in enumerate(blocks):
        st.write(f"### Block {i+1} (총 {len(block)}줄)")
        # 최대 20줄까지만 미리보기
        sample_count = min(20, len(block))
        for j, line in enumerate(block[:sample_count]):
            st.text(f"{j+1:2d} | {line}")
        if len(block) > 20:
            st.write(f"... (추가 {len(block)-20}줄)")

        # 체크박스
        ck_key = f"block_checkbox_{i}"
        st.session_state["block_selection"][i] = st.checkbox(
            f"Select Block {i+1}",
            value=st.session_state["block_selection"][i],
            key=ck_key
        )

        st.markdown("---")

    # Confirm 버튼
    if st.button("Confirm block selection"):
        st.session_state["block_lines"].clear()
        selected_count = 0
        for i, block in enumerate(blocks):
            if st.session_state["block_selection"][i]:
                st.session_state["block_lines"].extend(block)
                selected_count += 1

        st.success(f"{selected_count}개 블록 선택 완료 → block_lines에 {len(st.session_state['block_lines'])}줄 저장됨.")
```

---

## merged() (스켈레톤 예시)

```python
def merged():
    """
    block_lines + normal_lines를 합치는 등의 최종 로직은
    사용자가 직접 구현한다는 스켈레톤 함수
    """
    import streamlit as st
    
    if "block_lines" not in st.session_state or "normal_lines" not in st.session_state:
        st.warning("block_lines 혹은 normal_lines가 없습니다.")
        return

    # 예: parsed_list = normal_lines + block_lines (또는 그 반대)
    # etc. 로직은 자유롭게 구성
    st.info("merged() 스켈레톤: 필요한 로직을 직접 작성하세요.")
```

---

### 설명

1. **parse_block_lines()**  
   - **block_candidates**: 이미 전 단계(parse_nonblock_lines 등)에서 구해둔, 각 블록의 라인 리스트.  
   - 블록마다 **체크박스**(`st.checkbox`)로 “Select Block X” 표시.  
   - **최대 20줄**만 `st.text()`로 미리보기를 제공(라인이 많아도 앱이 느려지지 않도록).  
   - “Confirm block selection” 버튼 클릭 시, 체크된 블록을 하나로 합쳐 **`block_lines`**에 저장.  

2. **merged()** (스켈레톤)  
   - 최종적으로 **`normal_lines + block_lines`**를 합치는 로직을 담을 수 있지만,  
   - 사용자가 별도 로직으로 대체할 수 있도록 함수 내용은 비워둠.

---

이렇게 **체크박스 기반** 블록 선택과 **미리보기**(20줄) 제한을 통해, UI 성능 향상과 사용 편의 둘 다 만족시킬 수 있습니다.
