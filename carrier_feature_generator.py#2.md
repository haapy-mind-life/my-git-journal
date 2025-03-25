---
created: 2025-03-25T09:19:37+09:00
modified: 2025-03-25T09:19:53+09:00
---

# carrier_feature_generator.py#2

아래는 **`carrier_feature_generator.py`**의 간결한 예시 코드입니다.  
- **NEW FORMAT** 여부에 따라 각 Feature에서 체크박스가 달라집니다.  
- **ADD / REMOVE** 또는 **ALLOW_MODE / BLOCK_MODE**를 **체크박스로** 선택하되, **동시에 둘 다** 체크할 수 없습니다(선택 안 할 수도 있음).  
- 4열×2행의 그리드 형태로 7개 Feature(NSA, DSS, SA, ...)를 표시합니다.  
- 파일 생성 버튼 클릭 시, 최종 검증(둘 다 체크한 경우 에러 처리) 후 JSON 파일을 생성해 다운로드합니다.

```python
def run(is_admin=False):
    import streamlit as st
    import json, math

    from modules.json_utils import create_cf_json  # 예시: json_utils 내 함수

    # 1. 파일 업로드 섹션
    st.subheader("1. 파일 업로드")
    new_format = st.checkbox("NEW FORMAT 사용")
    uploaded_file = None
    if not new_format:
        uploaded_file = st.file_uploader("지원 형식: .json, .csv, .txt", type=["json", "csv", "txt"])
    else:
        st.info("NEW FORMAT 사용: 파일 업로드 불필요")
    
    st.markdown("---")
    
    # 2. 기본 설정 섹션
    st.subheader("2. 기본 설정")
    # NEW FORMAT 여부로 SOLUTION 자동 결정 (예시)
    solution = "SLSI" if new_format else "MTK"
    st.write(f"SOLUTION: {solution} (자동 결정)")

    # MCC_MNC 입력
    mcc_mnc = st.text_input("MCC_MNC 입력", placeholder="예: 123456 또는 99999F")
    
    st.markdown("---")
    
    # 3. Legacy Feature 설정 (4열×2행)
    st.subheader("3. Legacy Feature 설정")

    features = ["NSA", "DSS", "SA", "SA_DSS", "NSA_NRCA", "SA_NRCA", "VONR"]
    feature_modes = {}
    num_cols = 4
    num_rows = math.ceil(len(features) / num_cols)

    # NEW FORMAT이면 ADD/REMOVE 체크, 아니면 ALLOW_MODE/BLOCK_MODE 체크
    # * 둘 다 동시에 체크될 수 없도록, 버튼 클릭 시 최종 검증
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
                        feature_modes[feat] = {"ADD": add_checked, "REMOVE": remove_checked}
                    else:
                        allow_checked = st.checkbox("ALLOW_MODE", key=f"{feat}_allow")
                        block_checked = st.checkbox("BLOCK_MODE", key=f"{feat}_block")
                        feature_modes[feat] = {"ALLOW_MODE": allow_checked, "BLOCK_MODE": block_checked}

    st.markdown("---")

    # 4. 생성 및 다운로드 섹션
    st.subheader("4. 생성 및 다운로드")
    if st.button("💾 CF 파일 생성", use_container_width=True):
        # 최종 검증: 각 Feature에서 두 체크박스가 동시에 True면 에러
        for feat, mode_dict in feature_modes.items():
            vals = list(mode_dict.values())
            if sum(vals) > 1:
                # 둘 이상 선택된 경우 (ADD & REMOVE or ALLOW_MODE & BLOCK_MODE 동시 체크)
                st.error(f"Feature '{feat}' 에서는 두 항목을 동시에 선택할 수 없습니다. 다시 설정해주세요.")
                return  # 바로 종료

        # 파일 정보
        if uploaded_file:
            file_bytes = uploaded_file.read()
            file_info = f"파일 크기: {len(file_bytes)} bytes"
        else:
            file_info = "파일 업로드 없음"

        # JSON 생성 (예시)
        # create_cf_json() 내에서 원하는 최종 구조를 정의할 수 있음
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

---

## `json_utils.py` 내 함수 예시

```python
# modules/json_utils.py

def create_cf_json(new_format, solution, mcc_mnc, feature_config, file_info):
    """
    CF용 JSON 데이터 생성 예시.
    feature_config: 각 Feature별 체크 상태 (ADD/REMOVE or ALLOW_MODE/BLOCK_MODE)
    """
    data = {
        "new_format": new_format,
        "solution": solution,
        "mcc_mnc": mcc_mnc,
        "file_info": file_info,
        "features": []
    }

    for feat, mode_dict in feature_config.items():
        # mode_dict 예: {"ADD": True, "REMOVE": False} / {"ALLOW_MODE": False, "BLOCK_MODE": True}
        data["features"].append({
            "name": feat,
            **mode_dict  # {"ADD": True, "REMOVE": False} 등
        })
    return data
```

이 함수는 **사용자가 체크한 항목**을 받아 최종 JSON 구조를 만들고, 반환합니다.  
(원하는 포맷에 맞추어 자유롭게 수정하시면 됩니다.)

---

### 동작 요약

1. **NEW FORMAT** 체크 시 파일 업로드 UI 숨김, Feature 옵션 "ADD/REMOVE"  
   미체크 시 파일 업로드 UI 표시, Feature 옵션 "ALLOW_MODE/BLOCK_MODE"  
2. **각 Feature(7개)**를 4열×2행(그리드)로 배치, **체크박스**로 입력  
3. **동시에 둘 다 체크**(ADD+REMOVE, ALLOW_MODE+BLOCK_MODE)는 허용 안 함 → 버튼 클릭 시 에러  
4. **CF 파일 생성** 버튼 → `create_cf_json()` 호출 → JSON 생성 & 미리보기 & 다운로드

위 코드를 적용하면, **체크박스 기반**의 Legacy Feature 설정 로직을 간단히 구현할 수 있고,  
동시에 두 개가 선택되는 상황을 제한할 수 있습니다. (기본 Streamlit으로는 즉시 uncheck 기능은 어렵지만,  
최종 생성 버튼 클릭 시 검증/차단하여 사용자의 실수를 방지할 수 있습니다.)  

원하는 로직에 따라, **개별 Feature 선택**이 잘 드러나도록 UI/스타일을 추가로 수정해 보세요.  
**프로젝트 진행을 응원합니다!**
