---
created: 2025-04-03T11:54:38+09:00
modified: 2025-04-03T11:54:49+09:00
---

# 2025-04-03-streamlit-full-code_1

# 파일명: 2025-04-01-streamlit-full-code.md

```markdown
# 2025-04-01 | Streamlit 전체 코드 (캔버스 형태)

## 1. 폴더 구조

```
5G_feature_manager/
├── src/
│   ├── main.py
│   ├── views/
│   │   ├── home.py
│   │   ├── legacy_allow_list.py
│   │   ├── carrier_feature_generator.py
│   │   ├── file_comparison.py
│   │   └── data_visualization.py
│   ├── modules/
│   │   ├── config_loader.py
│   │   ├── security.py
│   │   ├── visitor_log.py
│   │   ├── json_utils.py
│   │   ├── file_utils.py
│   │   ├── visualization.py
│   │   └── config.yaml
│   └── tests/
│       ├── test_json_utils.py
│       ├── test_file_utils.py
│       ├── test_visualization.py
│       ├── test_visitor_log.py
│       └── test_security.py
├── .github/
│   └── workflows/
│       └── ci.yml
├── requirements.txt
└── README.md
```

---

## 2. main.py
```python
import streamlit as st
import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
VIEWS_DIR = os.path.join(CURRENT_DIR, 'views')
MODULES_DIR = os.path.join(CURRENT_DIR, 'modules')
sys.path.append(VIEWS_DIR)
sys.path.append(MODULES_DIR)

from home import run_home
from legacy_allow_list import run_legacy_allow_list
from carrier_feature_generator import run_cf_generator
from file_comparison import run_file_comparison
from data_visualization import run_data_visualization

from config_loader import load_config

def main():
    st.set_page_config(page_title="5G Feature Manager", layout="wide")

    config = load_config()
    menu_items = config["app_settings"]["menu"]
    choices = [f"{item['emoji']} {item['name']}" for item in menu_items]

    choice = st.sidebar.radio("메뉴 선택", choices)
    selected_name = choice.split(" ", 1)[1] if " " in choice else choice

    if selected_name == "Home":
        run_home()
    elif selected_name == "Legacy Allow List 업로드":
        run_legacy_allow_list()
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

## 3. views/home.py
```python
import streamlit as st

def run_home():
    st.title("🏠 홈 (Streamlit)")

    # 대화형 메시지로 사용 안내
    st.info("""
    ### 5G Feature Manager 사용 방법:

    1. **Legacy Allow List 업로드** 메뉴에서 .txt/.h 파일 업로드
       - 업로드 성공 시, 파일 내용이 DataFrame으로 표시됨
       - 세션에 저장되어, 이후 Carrier Feature Generator에서 활용 가능
    2. **Carrier Feature Generator** 메뉴로 이동
       - NEW FORMAT이면 파일 업로드 불필요
       - LEGACY FORMAT이면, Legacy Allow List 파일(또는 별도 업로드) 사용
       - Feature 설정 후 CF JSON 생성
    3. 나머지 메뉴(파일 비교, 데이터 시각화)는 향후 기능
    """)

    st.markdown("""
    - [GitHub 저장소](https://github.com/your-repo/5G_feature_manager)
    - [PRD 문서](https://your-link-to-prd)
    """)

    if st.button("🎈 프로젝트 축하 풍선 띄우기"):
        st.balloons()
```

---

## 4. views/legacy_allow_list.py
```python
import streamlit as st
from modules.file_utils import upload_and_parse_file

def run_legacy_allow_list():
    st.title("Legacy Allow List 업로드")

    df, error = upload_and_parse_file(
        label="Legacy Allow List 파일",
        allowed_types=["h"],
        help_text="여기서 Legacy Allow List (.h) 파일을 업로드해주세요."
    )
    if df is not None:
        st.success("파일 업로드 및 파싱 성공!")
        st.dataframe(df)
    else:
        if error:
            st.error(f"오류: {error}")
        else:
            st.info("파일을 업로드하세요.")

```

---

## 5. views/carrier_feature_generator.py
```python
import streamlit as st
from modules.json_utils import create_cf_json


def run():
    st.header("Carrier Feature Generator")

    new_format = st.checkbox("NEW FORMAT")
    omc_version = st.text_input("OMC VERSION", "91")
    mcc_mnc = st.text_input("MCC_MNC", "123456")

    features = ["NR_NSA","NR_DSS","NR_SA","NR_SA_DSS","NR_VONR","NR_NSA_NRCA","NR_SA_NRCA"]
    config = {}

    for feat in features:
        use_feat = st.checkbox(feat)
        if use_feat:
            col1, col2 = st.columns(2)
            with col1:
                mode = st.radio("MODE", ["ALLOW LIST","BLOCK LIST"], key=f"{feat}_mode")
            with col2:
                if new_format:
                    value = st.radio("VALUE", ["ADD","REMOVE"], key=f"{feat}_val")
                else:
                    value = st.radio("VALUE", ["ENABLE","DISABLE"], key=f"{feat}_val")
            config[feat] = {"MODE": mode, "VALUE": value}

    if st.button("JSON 생성"):
        cf_data = create_cf_json(new_format, omc_version, mcc_mnc, config)
        st.json(cf_data)
        st.download_button("다운로드", str(cf_data), file_name=f"CF_{mcc_mnc}.json")
```

---

## 6. views/file_comparison.py
```python
import streamlit as st

def run():
    st.header("파일 비교")
    st.info("준비 중인 기능입니다. 향후 5G 프로토콜 Feature 비교 로직이 추가될 예정입니다.")
```
``

## 7. views/data_visualization.py
```python
import streamlit as st

def run():
    st.header("데이터 시각화")
    st.info("준비 중인 기능입니다. Pandas, matplotlib 등으로 데이터를 시각화할 계획입니다.")
```

## 8. modules/config_loader.py
```python
import yaml
import os

def load_config():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
       return yaml.safe_load(f)
```  
## 9. modules/config.yaml

```
`python
app_settings:
  title: "5G Feature Manager"
  menu:
    - name: "Home"
      emoji: "🏠"
    - name: "Legacy Allow List 업로드"  # 순서 변경 (앞으로 이동)
      emoji: "📄"
    - name: "Carrier Feature Generator"
      emoji: "⚙️"
    - name: "파일 비교"
      emoji: "🔍"
    - name: "데이터 시각화"
      emoji: "📊"

```

```markdown
## 10. modules/security.py
```python
import streamlit as st

# 사내 IP 기반 관리자 체크 등, 단순 예시

def is_admin(ip_address):
    # TODO: config 파일에서 admin 목록 로드 후 비교
    admin_ips = ["192.168.1.100"]
    return ip_address in admin_ips
```
```

```markdown
## 11. modules/visitor_log.py
```python
import datetime
import pandas as pd

visitor_data = pd.DataFrame(columns=["ip", "timestamp"])

def log_visitor(ip):
    global visitor_data
    new_row = {"ip": ip, "timestamp": datetime.datetime.now()}
    visitor_data = visitor_data.append(new_row, ignore_index=True)


def get_visitor_log():
    return visitor_data
```
```

```markdown
## 12. modules/json_utils.py
```python
def create_cf_json(new_format, omc_version, mcc_mnc, feature_dict):
    return {
        "new_format": new_format,
        "omc_version": omc_version,
        "mcc_mnc": mcc_mnc,
        "features": feature_dict
    }
```
```

```markdown
## 13. modules/file_utils.py
```python
import pandas as pd

def parse_uploaded_file(uploaded_file):
    try:
        lines = uploaded_file.read().decode("utf-8", errors="replace").splitlines()
        return pd.DataFrame(lines, columns=["Line"])
    except Exception as e:
        return pd.DataFrame([f"Error: {str(e)}"])

import streamlit as st
import pandas as pd

def upload_and_parse_file(label="파일 업로드", allowed_types=None, help_text=None):
    """
    파일 업로드 + 파싱을 하나의 함수로 처리,
    성공 시 (df, None), 실패 시 (None, error) 반환
    """
    if allowed_types is None:
        allowed_types = ["h", "txt"]

    uploaded_file = st.file_uploader(label=label, type=allowed_types, help=help_text)

    if not uploaded_file:
        return None, None

    try:
        content = uploaded_file.read().decode("utf-8", errors="replace").splitlines()
        if not content:
            return None, "파일 내용이 비어 있습니다."
        df = pd.DataFrame(content, columns=["Line"])
        return df, None
    except Exception as e:
        return None, f"파일 파싱 오류: {str(e)}"

```
```

```markdown
## 14. modules/visualization.py
```python
# 시각화 유틸, 추후 확장용

def create_chart(data):
    pass
```
```

```markdown
## 15. tests/test_json_utils.py
```python
import unittest
from modules.json_utils import create_cf_json

class TestJsonUtils(unittest.TestCase):
    def test_create_cf_json(self):
        result = create_cf_json(True, "91", "123456", {"NR_NSA": {"MODE":"ALLOW","VALUE":"ADD"}})
        self.assertTrue("features" in result)
```
```

```markdown
## 16. tests/test_file_utils.py
```python
import unittest
from io import BytesIO
from modules.file_utils import parse_uploaded_file

class TestFileUtils(unittest.TestCase):
    def test_parse_uploaded_file(self):
        fake_file = BytesIO(b"Line1\nLine2")
        df = parse_uploaded_file(fake_file)
        self.assertEqual(len(df), 2)
```
```

```markdown
## 17. tests/test_visualization.py
```python
# 시각화 로직이 아직 미완성
import unittest
class TestVisualization(unittest.TestCase):
    def test_placeholder(self):
        self.assertTrue(True)
```
```

```markdown
## 18. tests/test_visitor_log.py
```python
import unittest
from modules.visitor_log import log_visitor, get_visitor_log

class TestVisitorLog(unittest.TestCase):
    def test_log(self):
        log_visitor("127.0.0.1")
        df = get_visitor_log()
        self.assertEqual(df.iloc[0]["ip"], "127.0.0.1")
```
```

```markdown
## 19. tests/test_security.py
```python
import unittest
from modules.security import is_admin

class TestSecurity(unittest.TestCase):
    def test_is_admin(self):
        self.assertTrue(is_admin("192.168.1.100"))
        self.assertFalse(is_admin("192.168.1.101"))
```
```

```markdown
## 끝!

이상으로 Streamlit 전체 코드(캔버스 형태)와 기본 테스트 코드까지 모두 정리했습니다.
```
