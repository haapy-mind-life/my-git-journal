---
created: 2025-03-25T11:15:37+09:00
modified: 2025-03-25T11:15:55+09:00
---

# 2025-03-25-file_utils.py#5

아래는 **단일 통합 함수** 예시로, **업로드된 `.h` 파일을 메모리에서 읽어** 다음 과정을 수행합니다:

1. **Start/End Marker** 사이 라인만 추출  
2. **최대 10개** `#if ~ #else ~ #endif` 구문을 파싱 (각각 A/B 블록)  
3. 사용자에게 **A/B/Skip** 결정을 받으며, **#if / #else / #endif** 줄도 포함된 전체 블록을 표시  
4. **최종 결정** 후 최종 라인들을 합친 뒤, 각 라인에서 **`{ ... }`** 사이의 문자열을 추출해 **리스트** 형태로 저장  
5. (추가) 추출된 문자열 리스트는 **나중에 다른 함수**에서 DataFrame 전처리에 사용할 수 있음

> **주의사항**  
> - 본 예시는 **중첩 #if, #elif, 다중 marker** 등 복잡한 케이스를 최소화했습니다.  
> - **Streamlit** 특성상, UI 갱신 시 **`st.session_state`**를 사용해 파싱 결과와 사용자 선택을 저장해야 합니다.  
> - 파일 내 정확한 라인 순서 복원, 중첩 구조 등은 추가 로직이 필요할 수 있습니다.

---

## `file_utils.py` 예시

```python
import streamlit as st
import pandas as pd
import re

def parse_h_all_in_one(
    uploaded_file,
    start_marker,
    end_marker,
    max_blocks=10
):
    """
    1) 업로드된 .h 파일을 메모리에서 읽음
    2) start_marker ~ end_marker 구간만 추출
    3) 해당 구간 내에서 #if ~ #else ~ #endif 구문을 최대 max_blocks(기본 10)까지 파싱
       - A 블록(#if ~ #else 직전까지), B 블록(#else ~ #endif)
       - #if/#else/#endif 라인도 블록에 포함
    4) 사용자에게 각 블록에 대해 A/B/Skip 결정 (라디오 + expander로 코드 표시)
    5) 최종 결정 시 선택된 라인만 합쳐 'final_lines' 생성
    6) 'final_lines' 각 라인에서 '{...}' 구간을 추출 → 리스트로 저장
    7) 결과(최종 라인 + '{...}' 추출 리스트)를 화면에 표시 or 반환
    """

    # 세션 상태 초기화
    if "pblocks" not in st.session_state:
        st.session_state["pblocks"] = []   # [(a_lines, b_lines, idx), ...]
    if "block_choices" not in st.session_state:
        st.session_state["block_choices"] = {}
    if "parsed_once" not in st.session_state:
        st.session_state["parsed_once"] = False
    if "normal_lines" not in st.session_state:
        st.session_state["normal_lines"] = []
    
    # 1) 파일 라인 분할
    lines = uploaded_file.read().decode("utf-8", errors="replace").splitlines()

    # 2) start_marker ~ end_marker 구간 추출
    capturing = False
    captured = []
    for line in lines:
        if start_marker in line:
            capturing = True
            continue
        if end_marker in line:
            capturing = False
            continue
        if capturing:
            captured.append(line)
    
    # 첫 파싱인지 확인
    if not st.session_state["parsed_once"]:
        # 초기화
        st.session_state["pblocks"].clear()
        st.session_state["block_choices"].clear()
        st.session_state["normal_lines"].clear()

        block_count = 0
        in_block = False
        reading_a = False
        reading_b = False
        current_a = []
        current_b = []
        normal_captured = []

        # 3) #if ~ #else ~ #endif 파싱
        for line in captured:
            if block_count >= max_blocks:
                normal_captured.append(line)
                continue

            s = line.strip()
            if s.startswith("#if") and not in_block:
                # 새 블록 시작
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
                # #endif 줄을 현재 블록(A or B)에 포함
                if reading_a:
                    current_a.append(line)
                else:
                    current_b.append(line)
                
                # 블록 완성
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
                # 블록 외부
                normal_captured.append(line)
        
        # 블록 바깥(normal) 라인 저장
        st.session_state["normal_lines"] = normal_captured

        st.session_state["parsed_once"] = True
        st.info("파싱이 완료되었습니다. 아래에서 블록 선택을 진행하세요.")
    else:
        st.info("이미 파싱 상태가 있습니다. 블록 선택을 수정할 수 있습니다.")

    # 4) 사용자 결정 UI (각 블록 A/B/Skip)
    final_lines_preview = []
    for (a_lines, b_lines, idx) in st.session_state["pblocks"]:
        st.markdown(f"### Block #{idx+1}")
        # A 블록 표시
        with st.expander(f"A 블록 (#{idx+1})"):
            st.code("\n".join(a_lines), language="c")
        # B 블록 표시
        with st.expander(f"B 블록 (#{idx+1})"):
            st.code("\n".join(b_lines), language="c")

        prev_choice = st.session_state["block_choices"].get(idx, "A")
        choice = st.radio(
            f"Block #{idx+1} 선택",
            ["A", "B", "Skip"],
            index=(0 if prev_choice=="A" else (1 if prev_choice=="B" else 2)),
            key=f"block_{idx}"
        )
        st.session_state["block_choices"][idx] = choice

    # 최종 결정 버튼
    if st.button("최종 전처리 실행"):
        # 5) 선택된 라인 합치기
        final_lines = []
        # normal_lines 먼저
        final_lines.extend(st.session_state["normal_lines"])
        # 블록
        for (a_lines, b_lines, idx) in st.session_state["pblocks"]:
            user_choice = st.session_state["block_choices"].get(idx, "A")
            if user_choice == "A":
                final_lines.extend(a_lines)
            elif user_choice == "B":
                final_lines.extend(b_lines)
            else:
                pass  # Skip
        
        # 6) 각 라인에서 '{...}' 문자열 추출
        curly_pattern = re.compile(r'\{([^}]*)\}')
        parsed_list = []
        for line in final_lines:
            matches = curly_pattern.findall(line)
            for m in matches:
                parsed_list.append(m.strip())

        # 7) 결과 표시
        st.success("최종 라인 & 중괄호 추출 리스트:")
        
        # (a) 최종 라인 미리보기
        with st.expander("최종 라인 (코드)"):
            st.code("\n".join(final_lines), language="c")

        # (b) 중괄호 내 문자열 리스트
        st.write("**{...} 내 문자열**:", parsed_list)

        # 필요 시, parsed_list → DF 변환
        # df = pd.DataFrame(parsed_list, columns=["curly_content"])
        # st.dataframe(df)

        # 이후, df 또는 parsed_list 반환하거나 별도 사용 가능
```

---

## 2) 사용 방법

```python
# carrier_feature_generator.py
from modules.file_utils import parse_h_all_in_one

def run(is_admin=False):
    import streamlit as st
    
    st.subheader("Carrier Feature Generator - 통합 파싱")

    start_marker = st.text_input("Start Marker", "BEGIN_FEATURE")
    end_marker = st.text_input("End Marker", "END_FEATURE")
    
    uploaded_file = st.file_uploader("업로드 (.h)", type=["h"])
    if uploaded_file:
        parse_h_all_in_one(
            uploaded_file=uploaded_file,
            start_marker=start_marker,
            end_marker=end_marker,
            max_blocks=10
        )
    else:
        st.info("파일(.h)을 업로드해주세요.")
```

1. **사용자**: `start_marker` / `end_marker` 입력 후, `.h` 파일을 업로드.  
2. **함수**:  
   - 지정된 구간만 추출 → #if 블록 파싱(최대 10개) → A/B 블록 내용 표시(#if, #else, #endif 포함).  
3. 각 블록에 대해 “A”, “B”, “Skip” 선택.  
4. “최종 전처리 실행” 버튼 →  
   - 블록 합친 최종 라인(`final_lines`) 구성,  
   - 각 라인에서 `{...}` 추출 → `parsed_list`,  
   - 두 결과를 화면에 표시.

---

### 3) 핵심 포인트

1. **구간 필터**(start_marker, end_marker) → **단일 capturing 구간**만 다룸(여러 구간 필요 시 추가 구현).  
2. **간단한 #if ~ #else ~ #endif**(최대 10개)만 처리. 중첩/elif 등은 고려 X.  
3. 블록 표시 시 #if, #else, #endif 라인도 함께 **A/B**에 포함.  
4. **User UI**: 
   - A/B 블록 코드를 **`st.expander`**로 표시,  
   - **`st.radio`**로 A/B/Skip 결정.  
   - **`st.session_state`**에 결정 저장.  
5. **최종 라인**을 합친 뒤, **정규표현식**(`r'\{([^}]*)\}'`)으로 `{...}` 구간 추출.  
6. **추출된 문자열 리스트**는 `parsed_list`로 관리, 추후 DataFrame 변환 등 가능.

---

이로써 **Marker 구간** + **#if 블록 선택** + **중괄호 `{...}`** 추출을 **하나의 함수**에서 처리하는 **통합 예시**를 구성했습니다.  
추가적으로,  
- **중첩 블록**(if 안에 if 등) 처리,  
- **파일 전체 라인 순서** 정확한 복원,  
- **여러 구간**(start_marker ~ end_marker 반복)  
등은 필요 시 로직 확장이 가능합니다.  

**프로젝트 맞춤**으로 수정하여 활용해보시길 바랍니다!
