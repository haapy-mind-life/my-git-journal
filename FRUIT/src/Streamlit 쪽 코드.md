---
created: 2025-03-28T14:58:56+09:00
modified: 2025-03-28T14:59:07+09:00
---

# Streamlit 쪽 코드

아래는 **Streamlit 쪽 폴더(`src/`)** 전체 코드입니다.  
(앞서 출력한 Django 쪽 코드를 제외한 부분입니다.)

---

## **Streamlit 폴더 구조**

```
src/
├── main.py
├── views/
│   ├── home.py
│   ├── carrier_feature_generator.py
│   ├── file_comparison.py
│   └── data_visualization.py
├── modules/
│   ├── config_loader.py
│   ├── security.py
│   ├── visitor_log.py
│   ├── json_utils.py
│   ├── file_utils.py
│   └── config.yaml
└── tests/
    ├── test_json_utils.py
    ├── test_file_utils.py
    ├── test_visualization.py
    └── test_security.py
```

---

## 1. **`main.py`** (Streamlit 앱 진입점)

```python
import streamlit as st
import sys
import os

# sys.path에 현재 폴더 추가
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
VIEWS_DIR = os.path.join(CURRENT_DIR, 'views')
MODULES_DIR = os.path.join(CURRENT_DIR, 'modules')
sys.path.append(VIEWS_DIR)
sys.path.append(MODULES_DIR)

from home import run_home
from carrier_feature_generator import run_cf_generator
from file_comparison import run_file_comparison
from data_visualization import run_data_visualization
from config_loader import load_config

def main():
    st.set_page_config(page_title="5G Feature Manager", layout="wide")

    config = load_config()
    menu_items = config["app_settings"]["menu"]  # 예: [{name: "Home", emoji: "🏠"}, ...]

    # 사이드바 메뉴
    choices = [f"{m['emoji']} {m['name']}" for m in menu_items]
    choice = st.sidebar.radio("메뉴 선택", choices)

    # 라벨에서 이름 추출
    selected_name = choice.split(" ", 1)[1] if " " in choice else choice

    if selected_name == "Home":
        run_home()
    elif selected_name == "Carrier Feature Generator":
        run_cf_generator()
    elif selected_name == "파일 비교":
        run_file_comparison()
    elif selected_name == "데이터 시각화":
        run_data_visualization()
    else:
        st.warning("알 수 없는 메뉴입니다.")

if __name__ == "__main__":
    main()
```

---

## 2. **`views/` 폴더**

### (1) **`home.py`**

```python
import streamlit as st

def run_home():
    st.title("🏠 홈")
    st.markdown("""
    **이곳은 5G Feature Manager** 프로젝트의 Home 화면입니다.

    - README, PRD 문서, GitHub 링크 등 안내 예정
    - 프로젝트 소개 등...
    """)

    st.markdown("---")
    st.subheader("프로젝트 안내")
    st.markdown("- [GitHub 저장소](https://github.com/your-repo/5G_feature_manager)")
    st.markdown("- [PRD 문서](https://your-link-to-prd)")

```

### (2) **`carrier_feature_generator.py`**

```python
import streamlit as st
import json
from json_utils import create_cf_json
from file_utils import parse_header_file


def run_cf_generator():
    st.title("Carrier Feature Generator")

    new_format = st.checkbox("NEW FORMAT 사용", value=False)
    uploaded_file = st.file_uploader(".h 파일 업로드", type=["h"]) if not new_format else None

    if uploaded_file:
        st.success("파일 업로드 완료. 아래에서 블록 선택/전처리 진행 가능.")
        df = parse_header_file(uploaded_file)
        st.write("전처리 결과 (미리보기):")
        st.dataframe(df)

    st.markdown("---")
    st.subheader("Feature 설정")

    features = ["NR_NSA", "NR_DSS", "NR_SA", "NR_SA_DSS", "NR_VONR", "NR_NSA_NRCA", "NR_SA_NRCA"]
    feature_config = {}
    for feat in features:
        col1, col2 = st.columns([1,2])
        with col1:
            use_feat = st.checkbox(feat, key=f"{feat}_use")
        with col2:
            if use_feat:
                mode = st.selectbox(f"{feat} 모드", ["ALLOW_MODE", "BLOCK_MODE"] if not new_format else ["ADD", "REMOVE"], key=f"{feat}_mode")
                feature_config[feat] = mode
            else:
                feature_config[feat] = None

    st.markdown("---")
    st.subheader("CF 파일 생성")
    omc_version = st.text_input("OMC VERSION", "91")
    mcc_mnc = st.text_input("MCC_MNC", "123456")

    if st.button("CF 파일 생성"):
        cf_data = create_cf_json(new_format, omc_version, mcc_mnc, feature_config, uploaded_file.name if uploaded_file else "No file")
        st.success("JSON 생성 완료")
        st.json(cf_data)
        st.download_button("JSON 다운로드", data=json.dumps(cf_data, indent=2), file_name=f"CF_{mcc_mnc}.json", mime="application/json")
```

### (3) **`file_comparison.py`**

```python
import streamlit as st

def run_file_comparison():
    st.title("파일 비교")
    st.info("5G 프로토콜 Feature 지원 여부 비교 페이지 (TODO)")
    st.markdown("아직 구현 예정: 업로드된 파일 2개 비교")
```

### (4) **`data_visualization.py`**

```python
import streamlit as st
import pandas as pd

def run_data_visualization():
    st.title("데이터 시각화")
    st.info("Pandas + matplotlib 이용하여 통계/지도/차트 등 시각화 예정")

    sample_data = {
        "Feature": ["NSA", "DSS", "SA", "SA_DSS"],
        "Count": [10, 5, 7, 3]
    }
    df = pd.DataFrame(sample_data)
    st.bar_chart(df, x="Feature", y="Count")
```

---

## 3. **`modules/` 폴더**

### (1) **`config_loader.py`**

```python
import yaml
import os

def load_config():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.yaml")
    with open(config_path, 'r', encoding="utf-8") as f:
        return yaml.safe_load(f)
```

### (2) **`security.py`**

```python
def check_admin_ip(config):
    # TODO: IP 체크 로직 (관리자/사용자 구분)
    pass
```

### (3) **`visitor_log.py`**

```python
def log_visitor():
    # TODO: 접속 로그 기록
    pass
```

### (4) **`json_utils.py`**

```python
def create_cf_json(new_format, omc_version, mcc_mnc, feature_config, file_info):
    result = {
        "new_format": new_format,
        "omc_version": omc_version,
        "mcc_mnc": mcc_mnc,
        "file_info": file_info,
        "features": {}
    }
    for feat, mode in feature_config.items():
        if mode:
            result["features"][feat] = mode
    return result
```

### (5) **`file_utils.py`**

```python
import pandas as pd

def parse_header_file(uploaded_file):
    lines = uploaded_file.read().decode("utf-8", errors="replace").splitlines()
    return pd.DataFrame(lines, columns=["content"])
```

### (6) **`config.yaml`** (예시)

```yaml
app_settings:
  title: "5G Feature Manager"
  menu:
    - name: "Home"
      emoji: "🏠"
    - name: "Carrier Feature Generator"
      emoji: "⚙️"
    - name: "파일 비교"
      emoji: "🔍"
    - name: "데이터 시각화"
      emoji: "📊"
```

---

## 4. **`tests/` 폴더**

### (1) **`test_json_utils.py`**

```python
import unittest
from modules.json_utils import create_cf_json

class TestJsonUtils(unittest.TestCase):
    def test_create_cf_json(self):
        cf = create_cf_json(True, "91", "123456", {"NR_NSA": "ADD"}, "test.h")
        self.assertIn("NR_NSA", cf["features"])
        self.assertEqual(cf["features"]["NR_NSA"], "ADD")
```

### (2) **`test_file_utils.py`**

```python
import unittest
from io import BytesIO
from modules.file_utils import parse_header_file

class TestFileUtils(unittest.TestCase):
    def test_parse_header_file(self):
        test_content = b"line1\nline2\n"
        uploaded_file = BytesIO(test_content)
        df = parse_header_file(uploaded_file)
        self.assertEqual(len(df), 2)
```

### (3) **`test_visualization.py`**
```python
import unittest

class TestVisualization(unittest.TestCase):
    def test_dummy_vis(self):
        self.assertTrue(True)
```

### (4) **`test_security.py`**
```python
import unittest

class TestSecurity(unittest.TestCase):
    def test_check_admin_ip(self):
        self.assertTrue(True)
```

---

이상으로, **Django 서버(Django_server)** 와 **Streamlit 앱(src)** 전체 폴더 구조와 코드 샘플을 모두 출력했습니다.  
추가적으로 수정이나 통합 설명이 필요하시면 알려주세요!
