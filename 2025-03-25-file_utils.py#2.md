---
created: 2025-03-25T10:45:19+09:00
modified: 2025-03-25T10:46:18+09:00
---

# 2025-03-25-file_utils.py#2

아래 예시는 **`.h` 파일을 라인 단위로 읽은 뒤**,  
- **`#if ~ #else ~ #endif`** 구조를 찾아  
- **사용자에게 A/ B 블록 중 어떤 것을 선택할지** 결정받는 과정을 최대 10회까지 지원하는 **간단한 예시**입니다.  
- 사용자 결정 후, **선택된 블록들만** 모아서 최종 텍스트(또는 DataFrame)로 만드는 방식을 보여줍니다.

> **주의사항**:  
> - Streamlit은 페이지를 다시 렌더링(re-run)하는 구조여서,  
>   각 결정 시점을 잘 관리하려면 **`st.session_state`** 등을 활용해야 합니다.  
> - 여기서는 **단일 함수** 내에서 예시로 작성했지만, 실제 프로젝트에서는 **여러 단계**(파일 전체 파싱 → #if 구조 인식 → 사용자 결정 → 최종 라인 조합)를 분리하는 것이 좋습니다.  
> - **복잡한 중첩 구조(예: #if 안에 #if)**나 **다중 #elseif** 등은 추가 로직이 필요합니다.

---

## 1) 예시: `file_utils.py`

```python
import streamlit as st
import pandas as pd

def parse_h_file_with_conditions(uploaded_file):
    """
    예시 로직:
    1) 업로드된 .h 파일을 라인 단위로 읽음
    2) #if ~ #else ~ #endif 구조를 최대 10개까지 파싱
    3) 사용자에게 A 블록(#if~#else) 또는 B 블록(#else~#endif) 중 하나 선택 요청
    4) 최종적으로 선택된 라인을 모아 DataFrame 생성
    5) 중첩 #if/#else, #elif, 다중 #else 등은 간단히 가정해서 생략
    """

    # 이미 n번 결정했다면, session_state에서 그 결정 정보를 재사용
    # 없으면 초기화
    if "block_choices" not in st.session_state:
        st.session_state["block_choices"] = {}  # 예: {block_index: "A" or "B"}

    # 1) 라인 분할
    lines = uploaded_file.read().decode("utf-8", errors="replace").splitlines()

    # 2) #if ~ #else ~ #endif 블록 검출
    blocks = []
    normal_lines = []  # 블록 외부의 일반 라인들을 저장
    block_count = 0

    in_block = False
    current_block_a = []
    current_block_b = []
    reading_a = False
    reading_b = False

    for line in lines:
        # 최대 10개 블록만 처리
        if block_count >= 10:
            # 10개 초과는 그냥 normal_lines로
            normal_lines.append(line)
            continue

        # #if 발견 -> 블록 A 시작
        if line.strip().startswith("#if") and not in_block:
            in_block = True
            reading_a = True
            reading_b = False
            current_block_a = []
            current_block_b = []
            continue

        # #else 발견 -> 블록 B 시작
        if line.strip().startswith("#else") and in_block and reading_a:
            reading_a = False
            reading_b = True
            continue

        # #endif 발견 -> 블록 끝
        if line.strip().startswith("#endif") and in_block:
            # 블록 하나 완성
            blocks.append((current_block_a, current_block_b, block_count))
            block_count += 1
            in_block = False
            reading_a = False
            reading_b = False
            continue

        # 블록 내부 라인 저장
        if in_block:
            if reading_a:
                current_block_a.append(line)
            elif reading_b:
                current_block_b.append(line)
        else:
            # 블록 바깥의 일반 라인
            normal_lines.append(line)

    # 3) 사용자에게 각 블록에 대해 A/B 중 어떤 것 선택할지 결정받기
    final_lines = []
    # 일단 normal_lines를 미리 추가
    # (블록이 파일 내에서 인터리빙될 수 있으므로, 더 정확한 위치 반영하려면 별도 로직 필요)
    # 여기서는 단순화된 예시로, 모든 블록 이후에 normal_lines를 붙임
    # 실제 구현에선 위치정보를 저장해야 함
    # final_lines.extend(normal_lines)

    for block_a, block_b, idx in blocks:
        st.markdown(f"### 블록 #{idx+1} 에 대한 선택")
        # 이전 선택이 있으면 가져옴
        prev_choice = st.session_state["block_choices"].get(idx, "A")  # 기본값 A
        
        choice = st.radio(
            f"#if ~ #else ~ #endif 구조 #{idx+1}",
            options=["A (if)", "B (else)", "Skip (둘다 무시)"],
            index=(0 if prev_choice == "A" else (1 if prev_choice=="B" else 2)),
            key=f"block_{idx}"
        )
        # 선택 상태를 session_state에 저장
        if choice.startswith("A"):
            st.session_state["block_choices"][idx] = "A"
        elif choice.startswith("B"):
            st.session_state["block_choices"][idx] = "B"
        else:
            st.session_state["block_choices"][idx] = "S"

    # 4) 최종 결정 후 '최종 전처리 실행' 버튼
    if st.button("최종 전처리 실행"):
        final_lines = []
        # 블록 바깥 normal_lines를 제대로 위치에 맞춰 넣으려면 추가 로직 필요
        # 여기서는 예시로 blocks를 만나기 전까지 normal_lines를 넣고, block 처리, 그 후 normal_lines? 
        # 단순히 block 결과 후에 normal_lines를 붙이는 구조로 작성 (간단화)
        
        # 블록은 파일 내 순서대로 존재하지만, 
        # 실제로 normal_lines, block, normal_lines, block 순서가 필요할 수 있음
        # -> 더 정교한 로직 필요. 여기서는 시연용 간단 예시
        # 이 예시는 normal_lines 전부 최상단에 붙여버리고, 그 후 block들 붙임.
        
        final_lines.extend(normal_lines)
        for block_a, block_b, idx in blocks:
            user_choice = st.session_state["block_choices"].get(idx, "A")
            if user_choice == "A":
                final_lines.extend(block_a)
            elif user_choice == "B":
                final_lines.extend(block_b)
            else:
                # Skip
                pass
        
        # 5) DataFrame으로 변환
        df = pd.DataFrame(final_lines, columns=["content"])
        st.success("최종 전처리 완료!")
        st.dataframe(df)

        # 추가 후속 로직: df를 반환하거나, JSON화, 다운로드 등
        # ...

```

---

### 코드 설명

1. **파싱 과정**  
   - `.read().decode(...).splitlines()`로 라인 분할  
   - `#if`를 만나면 **Block A** 수집 시작, `#else`를 만나면 **Block B** 수집, `#endif`를 만나면 하나의 블록 완성  
   - 최대 10개 블록까지만 처리(그 이상은 normal_lines에 그냥 추가)

2. **사용자 결정**  
   - 각 블록에 대해 **`st.radio`**로 **“A (if)”**, **“B (else)”**, **“Skip”**(둘 다 무시) 중 하나를 선택  
   - `st.session_state["block_choices"][idx]`에 사용자 결정 값을 저장/로드

3. **최종 전처리 실행**  
   - “최종 전처리 실행” 버튼을 눌렀을 때,  
   - `normal_lines` + (user_choice에 따라 A or B or Skip) 전부 합쳐서 `final_lines` 생성  
   - `pandas.DataFrame`으로 표시

4. **중첩 구조나 복잡한 상황**  
   - 이 예시는 **가장 단순한 #if ~ #else ~ #endif**만 처리합니다.  
   - 다중 **`#elif`**나 **중첩 #if**가 있으면 더 정교한 로직이 필요합니다.  
   - 또한 **파일 내 순서**(블록 전, 중간, 후의 normal_lines) 반영도 간단히 처리했습니다.

---

## 2) 사용 예시 (carrier_feature_generator.py 등)

```python
# carrier_feature_generator.py (발췌)
from modules.file_utils import parse_h_file_with_conditions

uploaded_file = st.file_uploader("지원 형식: .h", type=["h"])
if uploaded_file:
    # 라인 단위로 읽고 #if/#else/#endif 구문을 찾아
    # 사용자 결정(최대 10회) 받는 인터페이스
    parse_h_file_with_conditions(uploaded_file)

# 이후, 최종 전처리 실행 버튼 클릭 시,
# DataFrame이 표시됨.
```

사용자는 사이드바의 checkbox 등으로 NEW FORMAT을 체크할 수도 있고,  
만약 NEW FORMAT이 아니라면 `.h` 파일을 업로드해서 parse 과정을 진행할 수 있습니다.

---

### 결론

- 이 예시는 **여러 번(#if~#else~#endif 블록 최대 10개) 발생할 수 있는 조건 분기**에 대해 사용자에게 **A/B 선택**을 물어보고,  
- 최종 라인을 재구성한 뒤 **DataFrame**으로 제공하는 **기본 개념 시연**입니다.  
- 실제 구현에서는 **파일 내 순서**를 좀 더 정확히 반영하거나, **중첩**을 처리하는 로직 등이 필요할 수 있습니다.  
- **Streamlit**의 특성상, 라디오 선택 시마다 앱이 재실행되므로, **`st.session_state`**를 사용해 사용자 결정을 기억합니다.  
- “최종 전처리 실행” 버튼을 눌렀을 때 한 번에 최종 결과를 만드는 구조입니다.

이 로직을 토대로, 프로젝트 요구에 따라 상세 로직(예: #elif, 중첩)이나 UI를 보강해보시기 바랍니다.  
프로젝트 개발에 도움이 되길 바랍니다.
