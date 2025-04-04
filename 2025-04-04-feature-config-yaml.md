---
created: 2025-04-04T11:32:15+09:00
modified: 2025-04-04T11:32:29+09:00
---

# 2025-04-04-feature-config-yaml

```markdown
# 2025-04-04-feature-config-yaml.md

## Git Journal 업데이트 (YAML 기반 Feature Config)

### 작업 일시
2025-04-04

---

## 변경 내용 요약
- **carrier_feature_generator.py**: Feature 동적 생성 로직 개선 → YAML 파일(`feature_config.yaml`)로 분리
- **config_loader.py**: `load_feature_config()` 함수 추가 → YAML 파싱
- **feature_config.yaml**: Feature 옵션 정의 (desc, nf_opts, lg_opts 등)

---

## 변경된 파일 상세 (캔버스 형식)

### 1) feature_config.yaml (신규)
```yaml
NR_NSA:
  desc: "Non-Standalone"
  nf_opts: ["ADD", "REMOVE"]
  lg_opts: ["ENABLE", "DISABLE"]

NR_SA:
  desc: "Standalone"
  nf_opts: ["ADD", "REMOVE"]
  lg_opts: ["ENABLE", "DISABLE"]

NR_DSS:
  desc: "Dynamic Spectrum Sharing"
  nf_opts: ["ADD", "REMOVE"]
  lg_opts: ["ENABLE", "DISABLE"]

NR_SA_DSS:
  desc: "SA + DSS"
  nf_opts: ["ADD", "REMOVE"]
  lg_opts: ["ENABLE", "DISABLE"]

NR_VONR:
  desc: "Voice over NR"
  nf_opts: ["ADD", "REMOVE"]
  lg_opts: ["ENABLE", "DISABLE"]

NR_NSA_NRCA:
  desc: "NSA NR CA"
  nf_opts: ["ADD", "REMOVE"]
  lg_opts: ["ENABLE", "DISABLE"]

NR_SA_NRCA:
  desc: "SA NR CA"
  nf_opts: ["ADD", "REMOVE"]
  lg_opts: ["ENABLE", "DISABLE"]
```

---

### 2) config_loader.py (수정)
```python
import yaml
import os

def load_config():
    # 기존 config.yaml 로드
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_feature_config():
    # feature_config.yaml 로드
    base_dir = os.path.dirname(os.path.abspath(__file__))
    feat_path = os.path.join(base_dir, "feature_config.yaml")
    with open(feat_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
```

---

### 3) carrier_feature_generator.py (최신)
```python
import streamlit as st
from modules.config_loader import load_feature_config
from modules.json_utils import create_cf_json

def run_cf_generator():
    st.title("Carrier Feature Generator (YAML 기반)")

    # NEW FORMAT 체크
    is_new_format = st.checkbox("NEW FORMAT")

    # 기본 설정 입력
    omc_version = st.text_input("OMC VERSION", "91")
    mcc_mnc = st.text_input("MCC_MNC", "123456")

    # LEGACY FORMAT이면, legacy_df 세션 사용
    if not is_new_format:
        if "legacy_df" not in st.session_state:
            st.warning("LEGACY FORMAT: 'Legacy Allow List'에서 파일 업로드가 필요합니다.")
        else:
            st.success("이미 업로드된 Legacy Allow List 데이터가 있습니다.")
            st.dataframe(st.session_state["legacy_df"], use_container_width=True)
    else:
        st.info("NEW FORMAT → 파일 업로드 불필요")

    st.markdown("---")
    st.subheader("Feature 설정")

    feature_opts = load_feature_config()  # YAML 로드
    feature_settings = {}

    for feat_key, meta in feature_opts.items():
        col1, col2, col3 = st.columns([1,1.3,1.7])
        with col1:
            enabled = st.checkbox(label=feat_key, key=f"{feat_key}_enabled", help=meta.get("desc", ""))
        if enabled:
            with col2:
                mode = st.selectbox("MODE", ["ALLOW LIST", "BLOCK LIST"], key=f"{feat_key}_mode")
            with col3:
                if is_new_format:
                    value_options = meta["nf_opts"]
                else:
                    value_options = meta["lg_opts"]
                value = st.selectbox("VALUE", value_options, key=f"{feat_key}_value")

            feature_settings[feat_key] = {"MODE": mode, "VALUE": value}
        else:
            feature_settings[feat_key] = None

    st.markdown("---")
    if st.button("💾 CF 파일 생성"):
        cf_data = create_cf_json(
            new_format=is_new_format,
            omc_version=omc_version.strip(),
            mcc_mnc=mcc_mnc.strip(),
            feature_settings=feature_settings
        )
        st.success("CF JSON 생성 완료!")
        st.json(cf_data)
        st.download_button(
            label="📥 CF JSON 다운로드",
            data=str(cf_data),
            file_name=f"CF_{mcc_mnc}.json",
            mime="application/json"
        )
```

---

## 정리

- **feature_config.yaml**: Feature 이름, 설명, NEW/LEGACY 용 옵션을 YAML으로 분리
- **config_loader.py**: `load_feature_config()` 함수로 YAML 파싱
- **carrier_feature_generator.py**: YAML dict 기반 동적 UI 생성
- **legacy_allow_list.py**, **file_utils.py**: 기존 구조 유지 (파일 업로드 후 `st.session_state["legacy_df"]` 저장)

이로써 Feature 옵션이 늘어나도 YAML만 업데이트하면 되므로 유지보수가 용이해졌습니다.
```
