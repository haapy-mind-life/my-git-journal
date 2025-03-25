---
created: 2025-03-26T03:15:39+09:00
modified: 2025-03-26T03:16:12+09:00
---

# main.py

다음은 전체 구조와 현재까지의 구현 내용을 반영한 **최신 버전의 `main.py`** 예시 코드입니다.  
깔끔하고 확장 가능한 구조를 유지했습니다.

### `main.py` 최신 코드

```python
import streamlit as st
import sys
import os

# 경로 설정
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
VIEWS_DIR = os.path.join(CURRENT_DIR, "views")
MODULES_DIR = os.path.join(CURRENT_DIR, "modules")

sys.path.append(VIEWS_DIR)
sys.path.append(MODULES_DIR)

# views 폴더의 페이지 import
import home
import carrier_feature_generator as carrier_gen
import file_comparison as file_comp
import data_visualization as data_viz

# 공통 모듈 import
from config_loader import load_config
from security import check_admin_ip
from visitor_log import log_visitor

def main():
    # 설정 로딩
    config = load_config()
    app_settings = config["app_settings"]

    # 페이지 설정
    st.set_page_config(
        page_title=app_settings["title"],
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 앱 제목 출력
    st.title(f"{app_settings['title']} (MVP)")

    # 방문자 로그
    log_visitor()

    # 관리자 확인
    is_admin = check_admin_ip(config)

    # 사이드바 메뉴 구성 (라디오 버튼 방식)
    menu_items = app_settings.get("menu", [])
    menu_labels = [f"{item['emoji']} {item['name']}" for item in menu_items]

    # 사이드바에서 메뉴 선택
    choice = st.sidebar.radio("메뉴 선택", menu_labels)

    # 메뉴 이름 추출 (이모지 제거)
    selected_menu = choice.split(" ", 1)[1] if " " in choice else choice

    # 메뉴에 따른 페이지 분기 처리
    if selected_menu == "Home":
        home.run(is_admin=is_admin)
    elif selected_menu == "Carrier Feature Generator":
        carrier_gen.run(is_admin=is_admin)
    elif selected_menu == "파일 비교":
        file_comp.run(is_admin=is_admin)
    elif selected_menu == "데이터 시각화":
        data_viz.run(is_admin=is_admin)
    else:
        st.error("알 수 없는 메뉴입니다. 메뉴 설정을 확인하세요.")

if __name__ == "__main__":
    main()
```

---

### 구조 설명

- **경로 설정**:
  - `views`, `modules` 폴더를 모듈 경로에 추가하여 import 용이.
  
- **페이지 별 import**:
  - 각 기능은 `views` 폴더 내 별도 Python 파일로 관리.

- **모듈**:
  - 설정 로딩 (`config_loader.py`)
  - 관리자 IP 확인 및 보안 처리 (`security.py`)
  - 방문자 기록 (`visitor_log.py`)

- **UI 구성**:
  - 메뉴는 `config.yaml` 파일에서 관리.
  - 메뉴 선택을 사이드바의 라디오 버튼으로 구성하여 직관성 향상.

- **페이지 분기 처리**:
  - 선택된 메뉴에 따라 각 페이지를 로드.

---

### `config.yaml` (예시)

참고로, 앱 설정을 `config.yaml`에 관리할 경우 아래와 같이 구성될 수 있습니다.

```yaml
app_settings:
  title: "5G Feature Manager"
  menu:
    - name: "Home"
      emoji: "🏠"
    - name: "Carrier Feature Generator"
      emoji: "🚀"
    - name: "파일 비교"
      emoji: "📁"
    - name: "데이터 시각화"
      emoji: "📊"

security:
  admin_ips:
    - "127.0.0.1"
    - "192.168.1.100"
```

---

이 구조로 관리하면 새로운 기능 추가 및 유지보수가 쉽고 직관적입니다. 추가 요청사항 있으면 말씀해주세요!
