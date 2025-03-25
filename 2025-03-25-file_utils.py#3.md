---
created: 2025-03-25T10:55:48+09:00
modified: 2025-03-25T10:56:11+09:00
---

# 2025-03-25-file_utils.py#3

아래 예시는 **하나의 함수**에서 **`.h` 파일을 메모리상에서만 읽고**,  
- **Start Marker / End Marker**로 원하는 구간만 캡처,  
- 구간 안에서 최대 10개의 `#if ~ #else ~ #endif` 블록을 찾고,  
- 각 블록(A, B)을 **사용자에게 표시**하여 **A / B / Skip** 중 선택하도록 요청,  
- 마지막에 사용자가 결정한 블록들만 이어 붙여 **최종 라인**을 구성한 뒤 **DataFrame**으로 보여주는**(혹은 다른 용도)** 흐름을 구현한 **간단 예시**입니다.

> **주의**:  
> - 이 예시는 **중첩 구조, #elif, 파일 내 여러 Start/End** 등 복잡한 상황은 최소한으로 가정합니다.  
> - **Streamlit**은 매번 UI를 다시 렌더링하므로, **`st.session_state`**로 상태(사용자 결정)를 저장해야 합니다.  
> - **파일 내 원래 라인 순서**를 정확히 복원하려면 추가 로직이 필요합니다. 여기서는 **단순화**를 위해, 구간 밖의 라인은 무시하거나, 혹은 한꺼번에 붙이는 식으로 작성합니다.

---

## 1) 통합 함수 예시

```python
import streamlit as st
import pandas as pd

def parse_h_with_markers_and_conditions(uploaded_file, start_marker, end_marker):
    """
    하나의 함수 안에서:
    1) 업로드된 .h 파일을 메모리에서만 라인 분할
    2) start_marker 라인이 나오면 '캡처' 시작
    3) end_marker 라인이 나오면 '캡처' 종료
    4) 캡처 구간 안에서 최대 10개의 #if ~ #else ~ #endif 블록을 찾음
    5) 각 블록에 대해 A/B 블록 내용 표시 → st.radio로 A/B/Skip 결정
    6) 최종 '전처리 완료' 버튼 클릭 시, 결정된 블록 라인을 합쳐 DataFrame 출력
    """

    # 세션 상태: 블록별 선택 결과
    if "block_choices" not in st.session_state:
        st.session_state["block_choices"] = {}  # 예: { block_id: 'A', 'B', or 'S' }

    # 세션 상태: 파싱 완료된 블록들(사용자에게 표시할 A/B 내용)
    if "parsed_blocks" not in st.session_state:
        st.session_state["parsed_blocks"] = []  # [(a_lines, b_lines, idx), ...]

    # 세션 상태: 이미 파싱 완료되었는지 여부
    if "parsed_once" not in st.session_state:
        st.session_state["parsed_once"] = False

    # 만약 이미 파일 파싱이 끝났고, 다시 업로드 파일 바뀌면 초기화
    # (간단히 파일 이름 체크 등으로 구분 가능)
    # 여기서는 생략

    # 1) 파일 메모리 읽기
    lines = uploaded_file.read().decode("utf-8", errors="replace").splitlines()
    
    # 2) Start / End marker에 따라 캡처 구간 추출
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

    # 이제 captured_lines 안에서 #if ~ #else ~ #endif 블록을 파싱
    if not st.session_state["parsed_once"]:
        st.session_state["parsed_blocks"].clear()
        st.session_state["block_choices"].clear()

        block_count = 0
        in_block = False
        reading_a = False
        reading_b = False

        current_block_a = []
        current_block_b = []

        normal_captured = []  # 블록 밖의 일반 라인(캡처 구간 내지만, #if / #else / #endif 바깥)

        for line in captured_lines:
            if block_count >= 10:
                # 10개 초과는 그냥 normal_captured에 저장
                normal_captured.append(line)
                continue

            stripped = line.strip()
            if stripped.startswith("#if") and not in_block:
                in_block = True
                reading_a = True
                reading_b = False
                current_block_a = []
                current_block_b = []
                continue
            if stripped.startswith("#else") and in_block and reading_a:
                reading_a = False
                reading_b = True
                continue
            if stripped.startswith("#endif") and in_block:
                # 블록 확정
                st.session_state["parsed_blocks"].append((current_block_a, current_block_b, block_count))
                block_count += 1
                in_block = False
                reading_a = False
                reading_b = False
                continue

            if in_block:
                if reading_a:
                    current_block_a.append(line)
                elif reading_b:
                    current_block_b.append(line)
            else:
                normal_captured.append(line)

        # normal_captured도 세션에 저장(간단 예시)
        st.session_state["parsed_blocks"].append((normal_captured, None, -1))  # -1: normal

        st.session_state["parsed_once"] = True
        st.info("파싱을 완료했습니다. 아래에서 블록별 선택을 진행하세요.")
    else:
        st.info("이미 파싱 완료된 파일이 있습니다. 아래에서 블록 선택을 수정할 수 있습니다.")

    # ---- 블록별 사용자 선택 UI ----
    final_lines_preview = []
    for (a_lines, b_lines, block_idx) in st.session_state["parsed_blocks"]:
        if block_idx == -1:
            # normal_captured
            final_lines_preview += a_lines
            continue

        # 라디오 UI
        st.markdown(f"### Block #{block_idx + 1}")
        # A 블록 내용 표시
        with st.expander("A 블록 내용 보기"):
            st.code("\n".join(a_lines), language="c")
        # B 블록 내용 표시
        with st.expander("B 블록 내용 보기"):
            st.code("\n".join(b_lines), language="c")

        # 이전 선택값
        prev_choice = st.session_state["block_choices"].get(block_idx, "A")
        choice = st.radio(
            f"Block #{block_idx+1} 선택",
            ["A", "B", "Skip"],
            index=(0 if prev_choice == "A" else (1 if prev_choice == "B" else 2)),
            key=f"block_{block_idx}"
        )
        st.session_state["block_choices"][block_idx] = choice

    # '최종 라인 구성' 버튼
    if st.button("최종 전처리 완료"):
        # 최종 라인
        final_lines = []
        for (a_lines, b_lines, block_idx) in st.session_state["parsed_blocks"]:
            if block_idx == -1:
                # normal_captured
                final_lines.extend(a_lines)
            else:
                user_choice = st.session_state["block_choices"].get(block_idx, "A")
                if user_choice == "A":
                    final_lines.extend(a_lines)
                elif user_choice == "B" and b_lines is not None:
                    final_lines.extend(b_lines)
                else:
                    # Skip
                    pass

        df = pd.DataFrame(final_lines, columns=["content"])
        st.success("최종 전처리 결과:")
        st.dataframe(df)

        # 필요 시 df 반환, 혹은 session_state에 저장 가능
        # st.download_button 등 후속 작업 수행 가능
```

---

### 2) 동작 개요

1. **파일에서 라인 분할**(메모리만 사용, 임시파일 없음).
2. **`start_marker` / `end_marker`**를 통해 **필요 구간**만 **`captured_lines`**에 저장.
3. **`captured_lines`** 안에서 최대 10개의 `#if~#else~#endif` 블록을 파싱:  
   - `#if` 만나면 A 블록 수집,  
   - `#else` 만나면 B 블록 수집,  
   - `#endif` 만나면 하나의 블록 완성 → `parsed_blocks` 리스트에 저장.  
   - 그 외 라인은 **normal_captured**(블록 바깥 라인)으로 저장.  
   - 10개 초과 블록은 그냥 normal_captured로 처리(단순 예시).
4. **`parsed_blocks`**를 **`st.session_state`**에 저장하여 **UI 재실행** 시에도 유지.
5. 각 블록에 대해 **A / B 블록 내용**을 **`st.expander`**로 표시 → **`st.radio`("A", "B", "Skip")**  
   - Skip은 두 블록 다 무시.
6. **“최종 전처리 완료”** 버튼 클릭 → 사용자 결정값에 따라 A/B/Skip 선택.  
   - 결정된 라인을 **최종 DataFrame**으로 구성 후 표시.

---

### 3) 사용 예시 (carrier_feature_generator.py)

```python
# carrier_feature_generator.py

def run(is_admin=False):
    import streamlit as st
    from modules.file_utils import parse_h_with_markers_and_conditions

    st.subheader("Carrier Feature Generator")
    # Marker 입력
    start_marker = st.text_input("Start Marker", "BEGIN_FEATURE")
    end_marker = st.text_input("End Marker", "END_FEATURE")

    uploaded_file = st.file_uploader("지원 형식: .h", type=["h"])
    if uploaded_file:
        parse_h_with_markers_and_conditions(uploaded_file, start_marker, end_marker)
    else:
        st.info("파일 업로드 후 진행하세요.")
    
    # 기타 Legacy Feature 설정, CF 생성 로직 등 추가 가능
    # ...
```

이제 `.h` 파일을 업로드하면,  
**(1)** `BEGIN_FEATURE`부터 `END_FEATURE` 사이 라인만 대상으로,  
**(2)** 최대 10개의 `#if ~ #else ~ #endif` 블록을 찾아 **A/B/Skip** 결정,  
**(3)** 최종 라인을 DataFrame으로 보여주는 구조가 됩니다.

---

### 4) 주의/보완점

1. **파일 내 순서 보존**:  
   - 현재 예시에서는 **normal_captured**를 맨 뒤에 붙이는 등 단순 구현이므로, 실제 파일 순서대로 라인을 재조합하려면, **정확한 위치 정보**를 추적해야 합니다(예: block 시작 전 normal 라인, block 후 normal 라인 등).

2. **중첩 #if** 구조, **#elif**, **다중 #else**:  
   - 이 예시는 간단한 1단계 **#if / #else / #endif**만 처리합니다. 복잡한 중첩 로직은 별도 구현 필요.

3. **Marker 위치**:  
   - `start_marker`와 `end_marker`를 여러 번 만날 경우 등도 고려해야 합니다. 여기서는 1회 한정.

4. **UI/UX**:  
   - `st.expander`를 사용해 A/B 블록 내용을 펼쳐볼 수 있게 했습니다.  
   - 라디오에서 Skip이나 A/B 선택 시 **re-run**이 일어나므로, 선택 상태가 유지되도록 **session_state**를 사용합니다.

---

이상으로 **스타트/엔드 마커로 구간 지정** → **그 구간 내에서 `#if~#else~#endif` 최대 10개** → **사용자 의사결정(A/B/Skip)** → **최종 라인 재조합**이라는 과정을 **단일 함수** 안에 구현한 예시였습니다.  
**프로젝트 요구**에 맞게 세부 로직(정규표현식, 중첩 처리, 라인 수정 등)을 추가해보시기 바랍니다.
