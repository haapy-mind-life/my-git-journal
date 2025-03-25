---
created: 2025-03-26T03:01:56+09:00
modified: 2025-03-26T03:02:43+09:00
---

# 2025-03-25-carrier_feature_generator.py-parse_nonblock_lines()

아래는 **`parse_nonblock_lines()`** 함수가 **`#if`**를 만나면 **`#endif`**까지 라인을 전부 하나의 블록으로 묶어 **`block_candidates`**에 저장하도록 구현한 예시입니다.  
- **최대 10개** 블록까지만 파싱(초과되는 블록은 무시하거나, 필요하다면 추가 처리).  
- 블록 밖 라인은 **`normal_lines`**에 저장.

---

## parse_nonblock_lines() (수정 예시)

```python
def parse_nonblock_lines(uploaded_file, start_marker="BEGIN_FEATURE", end_marker="END_FEATURE"):
    import streamlit as st

    """
    1) .h 파일 라인을 start_marker ~ end_marker 구간만 추출
    2) 그 구간에서:
       - #if ... ~ #endif 까지 하나의 블록(block_temp)로 수집
       - 블록 파싱은 최대 10개까지만 허용
       - 블록 밖 라인은 normal_lines에 저장
    3) block_candidates에는 각 블록(리스트 형태)을 저장
    """

    st.info("parse_nonblock_lines(): #if ~ #endif 하나의 블록, 최대 10개")

    if "normal_lines" not in st.session_state:
        st.session_state["normal_lines"] = []
    if "block_candidates" not in st.session_state:
        st.session_state["block_candidates"] = []
    if "parsed_once" not in st.session_state:
        st.session_state["parsed_once"] = False

    if st.session_state["parsed_once"]:
        st.info("이미 parse_nonblock_lines() 실행됨.")
        return

    # 초기화
    st.session_state["normal_lines"].clear()
    st.session_state["block_candidates"].clear()

    # 1) 파일 라인 읽기
    lines = uploaded_file.read().decode("utf-8", errors="replace").splitlines()

    # 2) start_marker/end_marker 구간 필터
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

    # 3) #if ~ #endif 파싱
    block_count = 0
    in_block = False
    block_temp = []
    for cl in captured_lines:
        s = cl.strip()
        if block_count >= 10:
            # 최대 10개만 허용
            # 나머지는 normal_lines에 저장하거나 무시
            st.session_state["normal_lines"].append(cl)
            continue

        if s.startswith("#if") and not in_block:
            # 새 블록 시작
            in_block = True
            block_temp = [cl]  # #if 줄 포함
            continue

        if in_block:
            # 블록 안
            block_temp.append(cl)
            if s.startswith("#endif"):
                # 블록 끝
                st.session_state["block_candidates"].append(block_temp)
                block_count += 1
                in_block = False
                block_temp = []
        else:
            # 블록 밖 라인
            st.session_state["normal_lines"].append(cl)

    # 혹시 블록이 끝나지 않고 끝났다면? (예: #if ~ #endif 누락)
    # block_temp가 남아있으면 normal_lines로 보내거나 필요 처리
    if in_block and block_temp:
        # 여기서는 그냥 normal_lines로 처리
        st.session_state["normal_lines"].extend(block_temp)

    # 상태 갱신
    st.session_state["parsed_once"] = True
    st.success(
        f"parse_nonblock_lines() 완료: block_candidates={len(st.session_state['block_candidates'])}개, "
        f"normal_lines={len(st.session_state['normal_lines'])}"
    )
```

---

## 코드 흐름

1. **파일 라인**: `.read().decode(...).splitlines()`로 분할  
2. **start_marker/end_marker**: **captured_lines** 생성  
3. **블록 파싱**:  
   - **`#if`** 발견 시 `in_block=True`, 새 **block_temp** 시작  
   - 그 다음 라인들 **block_temp**에 추가  
   - **`#endif`** 만나면 block_temp를 **block_candidates**에 저장, `block_count++`, `in_block=False`  
   - **최대 10개** 블록만 허용, 초과는 **normal_lines**로 처리  
   - 블록 밖 라인은 **normal_lines**에 저장  
4. **블록이 #endif로 제대로 닫히지 않은 상태**(파일 끝까지 도달)인 경우, 남은 **block_temp**를 **normal_lines**로 이동

이렇게 하면 **각 `#if ~ #endif`**가 **`block_candidates`**의 한 원소(리스트)로 저장됩니다.  
이후 **`parse_block_lines()`**에서 **block_candidates**를 한 블록씩 펼쳐보며 A/B/Skip을 결정할 수도 있고,  
(만약 #else가 중간에 있다면, 그건 block_temp 안에 섞여있는 상태입니다 – 실제로 #if~#else~#endif를 A/B로 나누려면 다음 단계에서 더 파싱이 필요.)

원하시는 구조( A: `#if->#else`, B: `#else->#endif` )를 **`parse_block_lines()`**에서 다시 처리하시면 됩니다.
