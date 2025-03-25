---
created: 2025-03-25T09:55:17+09:00
modified: 2025-03-25T09:55:49+09:00
---

# 2025-03-25-carrier_fature_generator.py#3

아래는 **`carrier_feature_generator.py`**와 **`file_utils.py`**에 대한 예시 코드입니다.  
- **파일 업로드** 지원 형식을 `.h`로 변경  
- 업로드된 `.h` 파일을 **`file_utils.py`**의 새 함수에서 전처리하여 **pandas DataFrame** 형태로 반환  

---

## 1) `carrier_feature_generator.py` 예시

```python
def run(is_admin=False):
    import streamlit as st
    import json, math
    import pandas as pd

    from modules.json_utils import create_cf_json  # 예시: json_utils 내 함수
    from modules.file_utils import parse_header_file  # 새로 작성한 함수

    # 1. 파일 업로드 섹션 (".h" 파일만 업로드 가능)
    st.subheader("1. 파일 업로드")
    new_format = st.checkbox("NEW FORMAT 사용")
    uploaded_file = None

    if not new_format:
        uploaded_file = st.file_uploader("지원 형식: .h", type=["h"])
        if uploaded_file is not None:
            st.success("'.h' 파일이 업로드되었습니다.")
            # 업로드된 파일을 file_utils.py 의 함수로 전처리 → pandas DataFrame
            df = parse_header_file(uploaded_file)
            st.write("업로드된 .h 파일을 전처리한 결과(DataFrame 미리보기):")
            st.dataframe(df)
    else:
        st.info("NEW FORMAT 사용: 파일 업로드 불필요")

    st.markdown("---")
    
    # 2. 기본 설정 섹션
    st.subheader("2. 기본 설정")
    solution = "SLSI" if new_format else "MTK"  # 자동 결정
    st.write(f"SOLUTION: {solution} (자동 결정)")
    mcc_mnc = st.text_input("MCC_MNC 입력", placeholder="예: 123456 또는 99999F")
    
    st.markdown("---")
    
    # 3. Legacy Feature 설정 (4열×2행)
    st.subheader("3. Legacy Feature 설정")

    features = ["NSA", "DSS", "SA", "SA_DSS", "NSA_NRCA", "SA_NRCA", "VONR"]
    feature_modes = {}
    num_cols = 4
    num_rows = math.ceil(len(features) / num_cols)

    for r in range(num_rows):
        cols = st.columns(num_cols)
        for c in range(num_cols):
            i = r * num_cols + c
            if i < len(features):
                feat = features[i]
                with cols[c]:
                    st.write(f"**{feat}**")
                    if new_format:
                        add_checked = st.checkbox("ADD", key=f"{feat}_add")
                        remove_checked = st.checkbox("REMOVE", key=f"{feat}_remove")
                        # 둘 다 체크 가능 → 생성 버튼 누를 때 검증
                        feature_modes[feat] = {"ADD": add_checked, "REMOVE": remove_checked}
                    else:
                        allow_checked = st.checkbox("ALLOW_MODE", key=f"{feat}_allow")
                        block_checked = st.checkbox("BLOCK_MODE", key=f"{feat}_block")
                        # 둘 다 체크 가능 → 생성 버튼 누를 때 검증
                        feature_modes[feat] = {"ALLOW_MODE": allow_checked, "BLOCK_MODE": block_checked}

    st.markdown("---")

    # 4. 생성 및 다운로드 섹션
    st.subheader("4. 생성 및 다운로드")
    if st.button("💾 CF 파일 생성", use_container_width=True):
        # (검증) 둘 다 체크된 경우 에러 처리
        for feat, mode_dict in feature_modes.items():
            if sum(mode_dict.values()) > 1:
                st.error(f"Feature '{feat}' 에서는 두 항목을 동시에 선택할 수 없습니다. 다시 설정해주세요.")
                return

        # 파일 정보
        if uploaded_file:
            file_bytes = uploaded_file.read()
            file_info = f"파일 크기: {len(file_bytes)} bytes"
        else:
            file_info = "파일 업로드 없음"

        # JSON 생성
        cf_result = create_cf_json(
            new_format=new_format,
            solution=solution,
            mcc_mnc=mcc_mnc,
            feature_config=feature_modes,
            file_info=file_info
        )

        # 직렬화
        json_str = json.dumps(cf_result, ensure_ascii=False, indent=2)

        st.success("✅ CF 파일 생성 완료!")
        st.json(cf_result)
        st.download_button(
            label="📥 CF JSON 다운로드",
            data=json_str,
            file_name=f"CF_{solution}_{mcc_mnc}.json",
            mime="application/json"
        )
    else:
        st.info("설정을 완료한 후 버튼을 눌러주세요.")

    # (선택) 관리자 전용
    if is_admin:
        st.warning("관리자 전용 모드입니다. 추가 기능을 여기에 구현할 수 있습니다.")
```

### 동작 순서

1. **NEW FORMAT** 체크 해제 상태일 때만 `.h` 파일 업로드 가능.  
2. 업로드된 `.h` 파일을 `parse_header_file(uploaded_file)`에 전달 → 전처리 후 `pandas` DataFrame 반환 → 미리보기 표시.  
3. Legacy Feature(7개 항목)에 대해 ADD/REMOVE 또는 ALLOW_MODE/BLOCK_MODE를 체크박스로 입력.  
4. **“CF 파일 생성”** 버튼 클릭 시 최종 JSON 생성 → 다운로드.

---

## 2) `file_utils.py` 예시

아래는 **새로운 함수** `parse_header_file()`를 추가하여,  
업로드된 `.h` 파일을 전처리한 뒤 **`pandas.DataFrame`** 형태로 반환하는 예시입니다.

```python
# modules/file_utils.py

import pandas as pd

def parse_header_file(uploaded_file):
    """
    업로드된 .h 파일을 전처리하여 pandas DataFrame으로 반환.
    여기서는 단순히 한 줄씩 읽어서 DataFrame으로 만드는 예시.
    실제 전처리 로직은 프로젝트 요구사항에 맞춰 구현하세요.
    """
    # 파일 바이트 → 텍스트 디코딩 → 라인별 split
    lines = uploaded_file.read().decode("utf-8").splitlines()

    # 예: 각 라인을 DataFrame 한 칼럼 'content'로 저장
    df = pd.DataFrame(lines, columns=["content"])

    # 실제 전처리 로직 (필터링, 파싱, 정규표현식 등) 추가 가능
    # ...

    return df
```

1. `.read().decode("utf-8")`로 파일 내용을 가져옴.  
2. `.splitlines()`로 줄 단위로 나눈 뒤, `pandas.DataFrame`으로 구성(가장 간단한 예시).  
3. **실무**에서는 매크로 추출, define 키워드 파싱, 등 프로젝트 목적에 맞게 자유롭게 전처리하시기 바랍니다.

---

## 3) `json_utils.py` 예시 (참고)

```python
# modules/json_utils.py

def create_cf_json(new_format, solution, mcc_mnc, feature_config, file_info):
    """
    CF용 JSON 데이터 생성 예시
    """
    data = {
        "new_format": new_format,
        "solution": solution,
        "mcc_mnc": mcc_mnc,
        "file_info": file_info,
        "features": []
    }

    for feat, mode_dict in feature_config.items():
        data["features"].append({
            "name": feat,
            **mode_dict  # e.g. {"ADD": True, "REMOVE": False} or {"ALLOW_MODE": True, "BLOCK_MODE": False}
        })
    return data
```

---

### 요약

- **carrier_feature_generator.py**:  
  - `.h` 파일 업로드 (NEW FORMAT 미사용 시),  
  - **`parse_header_file(...)`**로 전처리 → DataFrame 표시,  
  - Legacy Feature 체크,  
  - **CF 파일 생성** 버튼 → `create_cf_json(...)` 호출 & 다운로드.

- **file_utils.py**:  
  - **`parse_header_file()`** 함수에서 `.h` 파일 내용을 **DataFrame**으로 전처리.  
  - 실제 로직(매크로 추출, 주석 제거 등)은 프로젝트 요구사항에 맞게 구현 가능.

이렇게 구현하면, `.h` 파일 업로드 → 전처리 → CF JSON 생성 과정을 Streamlit UI에서 간편하게 수행할 수 있습니다.  
프로젝트 진행에 참고가 되길 바랍니다!
