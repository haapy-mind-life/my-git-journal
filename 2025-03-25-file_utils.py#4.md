---
created: 2025-03-25T11:05:24+09:00
modified: 2025-03-25T11:06:15+09:00
---

# 2025-03-25-file_utils.py#4

아래 예시는 **A/B 블록**의 내용을 표시할 때, **해당 블록에 속하는 `#if`, `#else`, `#endif` 줄**도 함께 포함해서 출력하도록 수정한 코드 예시입니다.  
즉, 사용자가 **조건 지시문**까지 모두 확인한 뒤 A/B 결정이 가능하도록 했습니다.

---

## 1) 통합 함수 예시 (수정)

```python
import streamlit as st
import pandas as pd

def parse_h_with_markers_and_conditions(uploaded_file, start_marker, end_marker):
    """
    1) 업로드된 .h 파일을 메모리에서 읽기
    2) start_marker / end_marker로 특정 구간만 추출
    3) 구간 내 최대 10개의 #if ~ #else ~ #endif 블록 파싱
       - A 블록: #if 포함 ~ #else 직전까지
       - B 블록: #else 포함 ~ #endif까지
    4) A/B 블록 출력 시, #if, #else, #endif 라인도 포함
    5) 사용자 라디오로 A/B/Skip 결정
    """

    # 세션 스테이트(초기화)
    if "block_choices" not in st.session_state:
        st.session_state["block_choices"] = {}
    if "parsed_blocks" not in st.session_state:
        st.session_state["parsed_blocks"] = []
    if "parsed_once" not in st.session_state:
        st.session_state["parsed_once"] = False

    # 파일 라인 분할
    lines = uploaded_file.read().decode("utf-8", errors="replace").splitlines()

    # 1) Marker 구간 필터
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

    if not st.session_state["parsed_once"]:
        # 초기화
        st.session_state["parsed_blocks"].clear()
        st.session_state["block_choices"].clear()

        block_count = 0
        in_block = False
        reading_a = False
        reading_b = False

        current_block_a = []
        current_block_b = []

        normal_captured = []  # 블록 바깥(구간 내) 라인
        lines_for_a = []      # A 블록 라인( #if ~ #else )
        lines_for_b = []      # B 블록 라인( #else ~ #endif )

        for line in captured_lines:
            stripped = line.strip()
            
            # 최대 10개 블록만 처리
            if block_count >= 10:
                normal_captured.append(line)
                continue
            
            if stripped.startswith("#if") and not in_block:
                # 새 블록 시작
                in_block = True
                reading_a = True
                reading_b = False
                current_block_a = []
                current_block_b = []
                # #if 줄도 A 블록에 포함
                current_block_a.append(line)
                continue
            
            if stripped.startswith("#else") and in_block and reading_a:
                # #else 줄을 A 블록에 마지막으로 포함 → B 블록 시작
                current_block_a.append(line)
                reading_a = False
                reading_b = True
                continue
            
            if stripped.startswith("#endif") and in_block:
                if reading_a:
                    # #endif 줄을 A 블록에 포함
                    current_block_a.append(line)
                elif reading_b:
                    # #endif 줄을 B 블록에 포함
                    current_block_b.append(line)
                
                # 블록 하나 완성
                st.session_state["parsed_blocks"].append((current_block_a, current_block_b, block_count))
                
                in_block = False
                reading_a = False
                reading_b = False
                current_block_a = []
                current_block_b = []
                block_count += 1
                continue
            
            # 블록 내부
            if in_block:
                if reading_a:
                    current_block_a.append(line)
                elif reading_b:
                    current_block_b.append(line)
            else:
                normal_captured.append(line)

        # 블록 밖(구간 내)에 해당하는 라인은 -1로 저장
        st.session_state["parsed_blocks"].append((normal_captured, None, -1))

        st.session_state["parsed_once"] = True
        st.info("파싱 완료. 아래에서 블록별 A/B 선택 가능.")
    else:
        st.info("이미 파싱된 상태입니다. 블록 선택을 수정할 수 있습니다.")

    # 블록별 UI (A/B/Skip)
    for (a_lines, b_lines, idx) in st.session_state["parsed_blocks"]:
        if idx == -1:
            # normal_captured
            continue  # 별도 처리 생략(원한다면 표시 가능)
        
        st.markdown(f"### Block #{idx+1}")
        # A 블록 내용 표시(#if ~ #else 전까지)
        with st.expander("A 블록 보기 (#if ~ #else)"):
            st.code("\n".join(a_lines), language="c")
        # B 블록 내용 표시(#else ~ #endif)
        with st.expander("B 블록 보기 (#else ~ #endif)"):
            st.code("\n".join(b_lines), language="c")

        prev_choice = st.session_state["block_choices"].get(idx, "A")
        choice = st.radio(
            f"Block #{idx+1} 선택",
            ["A", "B", "Skip"],
            index=(0 if prev_choice == "A" else (1 if prev_choice=="B" else 2)),
            key=f"block_{idx}"
        )
        st.session_state["block_choices"][idx] = choice

    # 최종 전처리 버튼
    if st.button("최종 라인 구성"):
        final_lines = []
        # normal_captured 먼저 찾기
        # blocks 안에 -1 인덱스로 normal_captured가 있다
        # (단, 이 단순 방식은 정확한 라인 순서 복원에는 한계가 있음)
        for (a_lines, b_lines, idx) in st.session_state["parsed_blocks"]:
            if idx == -1:
                # normal_captured
                final_lines.extend(a_lines)

        # 블록들
        for (a_lines, b_lines, idx) in st.session_state["parsed_blocks"]:
            if idx == -1:
                continue
            user_choice = st.session_state["block_choices"].get(idx, "A")
            if user_choice == "A":
                final_lines.extend(a_lines)
            elif user_choice == "B" and b_lines is not None:
                final_lines.extend(b_lines)
            else:
                pass  # Skip

        df = pd.DataFrame(final_lines, columns=["content"])
        st.success("최종 전처리 결과:")
        st.dataframe(df)
```

---

### 2) 주요 변경점

1. **#if / #else / #endif 라인도 A/B 블록에 포함**  
   - `#if` 줄은 A 블록에 자동 포함,  
   - `#else` 줄도 A 블록 끝에 포함 후 B 블록 시작,  
   - `#endif` 줄은 A/B 블록 중 현재 읽고 있는 블록에 포함.

2. **사용자에게 표시**  
   - `st.expander("A 블록 보기...")`와 `st.expander("B 블록 보기...")` 안에서 각 블록 전체 코드를 **`st.code(..., language=\"c\")`**로 표시.  
   - 사용자는 실제 지시문(`#if`, `#else`, `#endif`) 포함된 전체 라인을 보고 선택할 수 있음.

3. **최종 라인 구성**  
   - 사용자 결정값이 `"A"`, `"B"`, `"Skip"`에 따라 최종 라인을 합쳐 DataFrame 생성.  
   - **주의**: 파일 내 정확한 순서(블록 전/후 normal 라인) 복원을 위해서는 더 세밀한 로직이 필요.  
     여기서는 간단히 `normal_captured` → block loop 순서로 붙여서 예시를 보여줌.

---

### 3) 사용 예시

```python
# carrier_feature_generator.py (일부)
def run(is_admin=False):
    import streamlit as st
    from modules.file_utils import parse_h_with_markers_and_conditions

    # 사용자 입력
    start_marker = st.text_input("Start Marker", "BEGIN_FEATURE")
    end_marker = st.text_input("End Marker", "END_FEATURE")

    uploaded_file = st.file_uploader("지원 형식: .h", type=["h"])
    if uploaded_file:
        parse_h_with_markers_and_conditions(uploaded_file, start_marker, end_marker)
    else:
        st.info("파일 업로드 후 진행하세요.")
```

업로드된 `.h` 파일 중 `BEGIN_FEATURE` ~ `END_FEATURE` 구간을 추출,  
그 안에서 최대 10개의 `#if~#else~#endif` 블록을 찾아 사용자에게 A/B 블록을 **전체 라인**(지시문 포함)으로 보여줍니다.  
결정 후 **최종 라인**을 DataFrame으로 확인.

---

### 4) 주의 / 확장

- **중첩 #if** 구조, **#elif** 등은 고려 대상 아님(추가 구현 필요).  
- **파일 전체 라인 순서**를 100% 복원하려면, normal_captured 라인을 **블록 사이**에 삽입해야 합니다. (간단 예시에서는 한꺼번에 붙임.)  
- 여러 Start/End Marker가 있을 경우 → 반복해서 parse → 합치는 로직 필요.

이렇게 지시문까지 포함하여 **A/B 블록**을 **expander** 내에서 보여주면,  
사용자가 더 쉽게 **#if / #else / #endif** 구문과 그 내부 코드를 파악한 뒤 결정할 수 있습니다.  
프로젝트 요구에 맞춰 UI/로직을 세밀하게 조정해 보세요!
