---
created: 2025-04-04T16:40:40+09:00
modified: 2025-04-04T16:41:17+09:00
---

# 2025-04-10-h-file-parsing.md

```markdown
# 2025-04-10-h-file-parsing.md

## Git Journal 업데이트: H 파일 업로드 → 파싱 → 블록 선택 → 최종 DataFrame

이 문서는 .h 파일을 업로드한 뒤, **`parse_h_file()`**로 **normal_lines**, **block_list**를 구성하고, **`user_select_blocks()`** 함수를 통해 사용자에게 #if/#else 블록 적용 여부를 묻는 코드를 종합한 예시입니다.

---

## 1) file_utils.py (간결화된 예시)

```python
import pandas as pd

def parse_h_file(file_name, lines):
    """
    file_name: 업로드된 파일명 (예: A.h, B.h 등)
    lines: 파일 전체를 라인 단위로 split한 리스트
    
    1) (필요한 경우) file_name에 따라 start_marker / end_marker 등 필터 적용 가능
    2) #if / #else / #endif 블록을 구분
       - normal_lines: 블록 밖 라인
       - block_list: 여러 블록 정보를 담은 리스트
    """
    # (예: start/end marker) - 간단화. 확장 시 추가
    start_marker = None
    end_marker = None
    if file_name.endswith("A.h"):
        start_marker = "START_A"
        end_marker = "END_A"
    elif file_name.endswith("B.h"):
        start_marker = "START_B"
        end_marker = "END_B"

    in_range = True if not start_marker else False
    marker_filtered = []
    # 1) marker 구간 필터
    for raw_line in lines:
        line = raw_line.strip()
        if start_marker and line.startswith(start_marker):
            in_range = True
            continue
        if end_marker and line.startswith(end_marker):
            in_range = False
            continue

        if in_range:
            marker_filtered.append(line)

    normal_lines = []
    block_list = []

    # 2) #if / #else / #endif 파싱
    inside_if = False
    inside_else = False
    block_type = None  # "if_only" or "if_else"
    temp_if_lines = []
    temp_else_lines = []

    for line in marker_filtered:
        if line.startswith("#if"):
            inside_if = True
            block_type = "if_only"
            temp_if_lines = [line]
        elif line.startswith("#else"):
            if block_type == "if_only":
                block_type = "if_else"
            inside_else = True
            temp_else_lines = [line]
        elif line.startswith("#endif"):
            if inside_if:
                if inside_else:
                    # #if ~ #else ~ #endif
                    temp_else_lines.append(line)
                    block_list.append({
                        "type": block_type,  # "if_else"
                        "if_lines": temp_if_lines,
                        "else_lines": temp_else_lines
                    })
                    inside_else = False
                    temp_else_lines = []
                else:
                    # #if ~ #endif
                    temp_if_lines.append(line)
                    block_list.append({
                        "type": block_type,  # "if_only"
                        "if_lines": temp_if_lines,
                        "else_lines": []
                    })
                inside_if = False
                block_type = None
                temp_if_lines = []
            else:
                # endif without if? skip or handle error
                pass
        else:
            # 일반 라인
            if inside_if:
                if inside_else:
                    temp_else_lines.append(line)
                else:
                    temp_if_lines.append(line)
            else:
                normal_lines.append(line)

    return normal_lines, block_list
```

---

## 2) user_select_blocks() (UI로 블록 선택)

```python
import streamlit as st

def user_select_blocks(normal_lines, block_list):
    """
    사용자에게 #if/#else/#endif 블록 UI를 제공하여,
    최종 라인 리스트(final_raw_list)를 구성.
    """
    final_raw_list = list(normal_lines)

    if len(block_list) == 0:
        st.info("선택할 #if/#else 블록이 없습니다.")
        return final_raw_list

    st.markdown("### #if/#else 블록 선택")

    for i, block in enumerate(block_list):
        btype = block["type"]
        st.markdown(f"**블록 {i+1}** (타입: `{btype}`)")

        if btype == "if_only":
            if_lines = block["if_lines"]
            st.code("\n".join(if_lines), language="text")
            use_block = st.checkbox(f"블록 {i+1} 적용", key=f"use_if_only_{i}")
            if use_block:
                final_raw_list.extend(if_lines)

        elif btype == "if_else":
            if_lines = block["if_lines"]
            else_lines = block["else_lines"]

            st.write("**#if 부분**")
            st.code("\n".join(if_lines), language="text")
            use_if = st.checkbox(f"블록 {i+1}의 #if 부분 적용", key=f"use_if_{i}")

            st.write("**#else 부분**")
            st.code("\n".join(else_lines), language="text")
            use_else = st.checkbox(f"블록 {i+1}의 #else 부분 적용", key=f"use_else_{i}")

            if use_if:
                final_raw_list.extend(if_lines)
            if use_else:
                final_raw_list.extend(else_lines)
        else:
            st.warning(f"알 수 없는 블록 타입: {btype}")

        st.markdown("---")

    return final_raw_list
```

---

## 3) 예시 사용 코드 (run_upload_parse)

```python
import streamlit as st
import pandas as pd
from modules.file_utils import parse_h_file
from modules.some_ui import user_select_blocks  # user_select_blocks() 함수가 들어있는 파일

def run_upload_parse():
    st.title("Upload & Parse .h File")

    uploaded_file = st.file_uploader("파일 업로드 (.h)", type=["h"])
    if not uploaded_file:
        st.info("파일을 업로드하세요.")
        return

    file_name = uploaded_file.name
    content = uploaded_file.read().decode("utf-8", errors="replace").splitlines()

    # 1) 파싱 (normal_lines, block_list)
    normal_lines, block_list = parse_h_file(file_name, content)

    # 2) 사용자에게 블록 선택 UI
    final_raw_list = user_select_blocks(normal_lines, block_list)

    # 최종 미리보기
    if st.button("최종 라인 보기"):
        st.markdown("### 최종 선택 라인들")
        df = pd.DataFrame(final_raw_list, columns=["Line"])
        st.dataframe(df, use_container_width=True)
        # 추후 st.session_state["legacy_df"] = df 등 처리
```

---

## 결론

1. **사용자 .h 업로드** → `parse_h_file()`로 **일반 라인 + 블록** 추출  
2. **UI**: `user_select_blocks()`가 각 블록을 checkbox로 선택하도록 제공  
3. **최종 라인**(`final_raw_list`)을 DataFrame 등으로 활용  

이로써 **파일 업로드** → **조건부 블록 파싱** → **사용자 선택** → **결과 확인**이라는 일련의 작업이 가능해집니다.
