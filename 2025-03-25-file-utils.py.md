---
created: 2025-03-25T10:25:37+09:00
modified: 2025-03-25T10:26:02+09:00
---

# 2025-03-25-file-utils.py

아래는 **`file_utils.py`**에서 **라인 단위로 `.h` 파일을 읽고**, 특정 **START** 및 **END** 조건에 따라 **문자열 추출**을 시작/중지한 후, 추출된 라인들을 **`pandas.DataFrame`**으로 만드는 예시 코드입니다.  
(추후 실제 프로젝트 환경에 맞게 START/END 마커 문자열, 전처리 로직 등을 조정하시면 됩니다.)

```python
import pandas as pd

def parse_h_file_with_markers(uploaded_file, start_marker, end_marker):
    """
    업로드된 파일(.h)을 라인 단위로 읽고,
    특정 라인에 start_marker가 포함되면 추출을 시작,
    end_marker가 포함되면 추출을 종료.
    추출된 라인들을 DataFrame으로 반환하는 예시.
    """
    # 1) 파일 내용을 라인 단위로 분할
    lines = uploaded_file.read().decode("utf-8", errors="replace").splitlines()
    
    capturing = False
    captured_lines = []
    
    # 2) 라인 단위 순회
    for line in lines:
        # START 조건: start_marker가 라인에 포함되면 추출 시작
        if start_marker in line:
            capturing = True
            # 필요 시 line 자체를 제외(또는 포함)할지 결정
            continue
        
        # END 조건: end_marker가 라인에 포함되면 추출 종료
        if end_marker in line:
            capturing = False
            # 필요 시 line 자체를 제외(또는 포함)할지 결정
            continue
        
        # capturing이 True인 동안 라인을 저장
        if capturing:
            captured_lines.append(line)
    
    # 3) 추출된 라인을 DataFrame으로 생성
    df = pd.DataFrame(captured_lines, columns=["content"])
    
    # 추가 전처리(필요 시)
    # 예) 정규표현식을 사용해 특정 키워드만 추출/필터링 등
    # ...

    return df
```

---

### 사용 방법

1. **업로드된 `.h` 파일**을 `file_uploader`로 받아 `uploaded_file` 변수에 저장.
2. 원하는 **start_marker**, **end_marker**(예: `#ifdef BEGIN_FEATURE`, `#endif`)를 지정.
3. `parse_h_file_with_markers(uploaded_file, start_marker, end_marker)`를 호출 → **추출된 라인**들이 **DataFrame**으로 반환.

```python
# 예: carrier_feature_generator.py

from modules.file_utils import parse_h_file_with_markers

uploaded_file = st.file_uploader("지원 형식: .h", type=["h"])
if uploaded_file:
    df = parse_h_file_with_markers(uploaded_file, start_marker="BEGIN_FEATURE", end_marker="END_FEATURE")
    st.write("추출된 라인:")
    st.dataframe(df)
```

이렇게 하면, **`BEGIN_FEATURE`** 문자열이 등장하는 라인부터 **`END_FEATURE`**를 만나기 전까지 라인들을 추출하여 DataFrame으로 확인할 수 있습니다.

---

### 확장 아이디어

- **여러 구간**에 대해 추출해야 한다면, start/end 마커를 여러 쌍으로 나누거나, 구간별로 저장할 수도 있습니다.  
- **정규표현식**(re 모듈)을 사용해 라인별 패턴 매칭을 추가로 수행할 수 있습니다.  
- 추출한 라인을 다시 가공해(예: split, strip 등) DataFrame의 여러 열에 나누어 담을 수도 있습니다.  

이 코드 예시는 **가장 기본적인 형태**이므로, **프로젝트 요구**에 맞춰 세부 로직을 수정해보세요.
