---
created: 2025-03-25T10:15:01+09:00
modified: 2025-03-25T10:15:22+09:00
---

# 2025-03-25-carrier_feature_generator.py#3

아래는 **`file_utils.py`**에서 **`.h` 파일을 전처리하여 DataFrame`**으로 만드는 과정을 두 가지 방식으로 예시한 코드입니다:

1. **직접 메모리에서 읽고 수정** (간단한 라인 단위 수정 등에 적합)  
2. **임시 폴더에 복사 후 수정** (파일을 직접 열고 쓰며, 구조를 크게 바꾸는 등 상대적으로 복잡한 수정이 필요한 경우)

실제 프로젝트 환경에 맞춰, 두 방법 중 하나(또는 혼합)를 선택해 사용하면 됩니다.

---

## 파일 예시: `file_utils.py`

```python
import streamlit as st
import pandas as pd
import tempfile
import os

def parse_h_file_in_memory(uploaded_file):
    """
    1) 업로드된 .h 파일을 메모리에서 바로 읽어,
    간단한 수정(라인 필터링, 텍스트 치환 등)을 거쳐 DataFrame으로 반환.
    """
    # (1) 파일을 바이트로 읽고, UTF-8로 디코딩
    content = uploaded_file.read().decode("utf-8", errors="replace")
    
    # (2) 원하는 방식으로 라인 단위 접근
    lines = content.splitlines()

    # (2-1) 예: 특정 키워드(#define 등)만 골라내기
    #    여기서는 간단히 전체 줄을 DataFrame에 저장하는 예시
    #    필요 시 정규표현식 등을 사용해 필터링 가능
    # lines = [line for line in lines if line.startswith('#define')]

    # (2-2) 라인 수정(치환, 삭제 등) 가능
    # lines = [line.replace('OLD', 'NEW') for line in lines]

    # (3) DataFrame 생성
    df = pd.DataFrame(lines, columns=["content"])
    return df


def parse_h_file_with_temp(uploaded_file):
    """
    2) 업로드된 .h 파일을 임시폴더에 저장하고,
    파일을 직접 수정(추가, 치환 등)을 한 후,
    최종 결과를 DataFrame으로 만드는 예시.
    """
    # (1) 임시 폴더/파일 생성
    with tempfile.NamedTemporaryFile(mode='w+b', delete=False, suffix=".h") as tmp_file:
        temp_filename = tmp_file.name
        # (2) 업로드된 파일 내용을 tmp_file에 기록
        content = uploaded_file.read()
        tmp_file.write(content)
    
    # (3) 파일을 직접 열어 필요 작업(수정, 치환 등)을 수행
    # 예: readlines() 후 특정 줄 치환, 삭제, 추가 등
    # 아래는 간단히 한 번 더 열어 전체 라인 읽은 뒤, DataFrame에 담는 예시
    try:
        with open(temp_filename, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        # (3-1) 원하는 수정 로직 적용 (예: 특정 키워드 라인만 남기기)
        # lines = [line for line in lines if line.strip().startswith('#define')]

        # (3-2) 수정 후 DataFrame으로 변환
        df = pd.DataFrame([line.strip('\n') for line in lines], columns=["content"])
    finally:
        # (4) 임시 파일 정리(필요 시)
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

    return df


def parse_header_file(uploaded_file, use_temp=False):
    """
    최종적으로 carrier_feature_generator.py 등에서 호출하는 함수.
    use_temp=True 면 임시폴더로 복사 후 수정,
    False 면 메모리에서 바로 처리.
    """
    if use_temp:
        return parse_h_file_with_temp(uploaded_file)
    else:
        return parse_h_file_in_memory(uploaded_file)
```

---

### 코드 설명

1. **`parse_h_file_in_memory(uploaded_file)`**  
   - **직접 메모리에서** `.read()`로 파일 내용을 읽고,  
   - UTF-8로 디코딩 후 **한 줄씩 split**하여 간단한 **수정/필터링**을 거쳐 **DataFrame**으로 만듭니다.  
   - 적은 용량의 파일, 단순 전처리에 적합.

2. **`parse_h_file_with_temp(uploaded_file)`**  
   - 임시폴더(`tempfile.NamedTemporaryFile`)에 **이진 쓰기**(`'w+b'`)로 `.h` 파일을 저장.  
   - 그 후 **파일 시스템 접근**을 통해 **실제 파일**을 열고, 라인 수정 / 치환 등 복잡한 작업을 수행할 수 있음.  
   - 최종적으로 **DataFrame**으로 변환 후 임시 파일을 삭제.

3. **`parse_header_file(uploaded_file, use_temp=False)`**  
   - 외부에서 공용으로 불리는 함수.  
   - `use_temp=True` 파라미터에 따라 **메모리 방식** or **임시 파일 방식**을 선택.

---

### carrier_feature_generator.py 수정 예시

만약 특정 상황에서만 임시폴더 로직을 쓰고 싶다면, 예: NEW FORMAT이 아닐 때 `use_temp=True`를 쓰는 식으로:

```python
# carrier_feature_generator.py (발췌)

from modules.file_utils import parse_header_file

# ...
if not new_format:
    uploaded_file = st.file_uploader("지원 형식: .h", type=["h"])
    if uploaded_file:
        # 예: 임시폴더 로직 사용
        df = parse_header_file(uploaded_file, use_temp=True)
        st.dataframe(df)
else:
    ...
```

---

## 정리

- **Streamlit**에서 업로드된 파일(`uploaded_file`)은 메모리상의 파일 객체로, **단순 읽기** 접근은 가능하지만, **직접 수정**(부분 쓰기)은 지원하지 않습니다.  
- 따라서 **in-memory** 방식에서 가능한 수정은 **텍스트 전체를 문자열로 읽어서** → **문자열 치환** → **DataFrame 생성** 정도입니다.  
- **파일 자체에 물리적으로 쓰기**(임의 위치 수정, 특정 줄 추가/삭제 등)가 필요하다면, **임시폴더에 저장** 후 OS 파일 접근으로 처리하는 것이 일반적입니다.  

위 코드를 참고하여, 프로젝트 요구사항(라인 치환, define 매핑, 키워드 추출 등)에 맞춰 전처리 로직을 추가/수정해 보세요.  
프로젝트 진행을 응원합니다!
