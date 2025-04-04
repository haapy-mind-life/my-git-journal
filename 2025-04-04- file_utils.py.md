---
created: 2025-04-04T17:22:43+09:00
modified: 2025-04-04T17:23:03+09:00
---

# 2025-04-04- file_utils.py

아래는 **최종 DataFrame**을 생성하는 과정을 별도의 함수로 분리하여 호출하는 예시입니다. 이 방식으로, 최종 라인 리스트(`final_raw_list`)를 다른 부분(예: UI 함수)에서 구성하고, **데이터 프레임 변환**은 전담 함수에서 처리할 수 있습니다.

---

## 1) file_utils.py (최종 예시)

```python
import streamlit as st
import pandas as pd
from modules.file_utils_parse import parse_h_file
from modules.file_utils_ui import user_select_blocks

def build_final_dataframe(final_raw_list):
    """
    최종 라인 리스트를 받아 DataFrame으로 만들어 반환.
    향후 추가 전처리/검증 로직도 이 함수에 넣을 수 있음.
    """
    df = pd.DataFrame(final_raw_list, columns=["Line"])
    # 필요 시 전처리/필터링 등 추가 가능
    return df

def process_legacy_file(upload_label="Legacy Allow List(.h) 업로드"):
    """
    1) .h 파일 업로드
    2) parse_h_file로 #if/else 블록 파싱
    3) 사용자 선택(user_select_blocks) → final_raw_list
    4) build_final_dataframe으로 최종 DF 생성
    성공 시 (DataFrame, None), 실패 시 (None, 오류)
    """
    uploaded_file = st.file_uploader(label=upload_label, type=["h"])
    if not uploaded_file:
        return None, None  # 파일 미선택

    try:
        file_name = uploaded_file.name
        lines = uploaded_file.read().decode("utf-8", errors="replace").splitlines()

        # 1) 파싱
        normal_lines, block_list = parse_h_file(file_name, lines)

        # 2) 사용자 블록 선택
        final_raw_list = user_select_blocks(normal_lines, block_list)

        # 3) 최종 DataFrame
        df = build_final_dataframe(final_raw_list)
        return df, None

    except Exception as e:
        return None, f"오류: {str(e)}"
```

---

## 2) legacy_allow_list.py

```python
import streamlit as st
from modules.file_utils import process_legacy_file

def run_legacy_allow_list():
    st.title("Legacy Allow List (최신 구조)")

    df, error = process_legacy_file("Legacy Allow List(.h) 업로드")
    if df is not None:
        st.success("최종 DataFrame 결과")
        st.dataframe(df, use_container_width=True)
        # 필요 시 st.session_state["legacy_df"] = df
    else:
        if error:
            st.error(f"오류: {error}")
        else:
            st.info("파일을 업로드하세요.")
```

---

## 3) 상세 설명

1. **`parse_h_file(file_name, lines)`**  
   - 파일명(`A.h`/`B.h`)에 따라 마커 필터  
   - `#if ~ #else ~ #endif` 구간 파싱 → `(normal_lines, block_list)`

2. **`user_select_blocks(normal_lines, block_list)`**  
   - 사용자에게 UI(checkbox 등)로 블록별 선택 여부 묻기  
   - 최종 선택 라인(`final_raw_list`) 반환

3. **`build_final_dataframe(final_raw_list)`**  
   - 라인 리스트를 **`pd.DataFrame`**으로 변환.  
   - 추가 전처리/필터 로직이 있다면 이 함수에서 처리

4. **`process_legacy_file(...)`**  
   - 위 3단계를 하나의 **파이프라인**으로 묶어, **(DataFrame, None)**를 최종적으로 리턴

5. **`legacy_allow_list.py`**  
   - `process_legacy_file(...)` 호출 후, 성공 시 `st.dataframe(df)`

---

## 4) 결론

- 이 구조로 **최종 DataFrame** 생성 로직을 **별도 함수**(`build_final_dataframe`)에 두면,  
- 불필요한 중복이나 **하드코딩**을 줄이고, **전처리**나 **후처리**를 손쉽게 추가 가능.
