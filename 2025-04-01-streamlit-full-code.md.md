---
created: 2025-04-03T11:09:55+09:00
modified: 2025-04-03T11:10:31+09:00
---

# 2025-04-01-streamlit-full-code.md

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

def main():
    st.set_page_config(page_title="5G Feature Manager")
    st.title("5G Feature Manager")

    menu = ["Home", "Legacy Allow List", "Carrier Feature Generator", "파일 비교", "데이터 시각화"]
    choice = st.sidebar.selectbox("메뉴 선택", menu)

    if choice == "Home":
        import views.home as home
        home.run()
    elif choice == "Legacy Allow List":
        import views.legacy_allow_list as lal
        lal.run()
    elif choice == "Carrier Feature Generator":
        import views.carrier_feature_generator as cfg
        cfg.run()
    elif choice == "파일 비교":
        import views.file_comparison as fc
        fc.run()
    elif choice == "데이터 시각화":
        import views.data_visualization as dv
        dv.run()

if __name__ == "__main__":
    main()
```

---

## 3. views/home.py
```python
import streamlit as st

def run():
    st.header("Home")
    st.write("이곳은 프로젝트 정보 및 링크를 제공하는 화면입니다.")
    st.markdown("""
    - [GitHub Repo](https://github.com/your_repo)
    - [PRD 문서](https://your_prd_link)
    """)
```

---

## 4. views/legacy_allow_list.py
```python
import streamlit as st
from modules.file_utils import parse_uploaded_file

def run():
    st.header("Legacy Allow List")
    uploaded_file = st.file_uploader("Allow List(.h) 업로드", type=["h"])

    if uploaded_file:
        df = parse_uploaded_file(uploaded_file)
        st.success("파일 업로드 완료")
        st.dataframe(df)
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
    - name: "Legacy Allow List"
    - name: "Carrier Feature Generator"
    - name: "파일 비교"
    - name: "데이터 시각화"
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
