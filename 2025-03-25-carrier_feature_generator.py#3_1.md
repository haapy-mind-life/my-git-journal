---
created: 2025-03-25T14:51:31+09:00
modified: 2025-03-25T15:18:43+09:00
---

# 2025-03-25-carrier_feature_generator.py#3

아래는 요구사항을 **최신**으로 반영하여 수정된 **`carrier_feature_generator.py`** 코드 예시입니다.  
- **NEW FORMAT** 체크 여부에 따라 **파일 업로드**(`.h`) 메뉴를 표시하거나 숨김.  
- 정상 업로드 시 **“파일 업로드 완료”** 메시지 표시.  
- **Block(블록) 선택** 완료 후 **“Block 선택 완료”** 메시지 표시 (예시로 구성).  
- 최종 변환 완료 시 **“최종 변환 완료”** 메시지 출력.  
- 결과(미리보기) 화면은 가로 폭을 **끝까지** 활용 (Streamlit 기능 `use_container_width=True` 등 사용).

> **참고**:  
> - “Block 선택” 과정은 구체적으로 어떤 로직인지 불명확하므로, 여기서는 **예시 버튼**을 통해 메시지 표시만 합니다.  
> - 실제 **A/B/Skip** 블록 파싱 로직(또는 Legacy Feature 체크 로직)은 유지하며, 그 선택 후 **Block 선택 완료** 버튼을 누르면 메시지를 띄우도록 했습니다.  
> - **가로 화면 끝까지 차도록**: `st.dataframe(df, use_container_width=True)` 또는 `st.table(...)` 등 사용.

---

## **carrier_feature_generator.py** (최신 업데이트 예시)

```python
def run(is_admin=False):
    import streamlit as st
    import math
    import json

    # 예: file_utils, json_utils 모듈
    from modules.file_utils import parse_header_file
    from modules.json_utils import create_cf_json

    st.title("Carrier Feature Generator (최신)")

    # 1) 파일 업로드 + NEW FORMAT 체크
    st.subheader("1. 파일 업로드")
    new_format = st.checkbox("NEW FORMAT 사용", value=False)
    uploaded_file = None

    if not new_format:
        # NEW FORMAT이 아닌 경우에만 파일 업로드
        uploaded_file = st.file_uploader("지원 형식: .h", type=["h"])
        if uploaded_file:
            st.success("파일 업로드 완료!")
    else:
        st.info("NEW FORMAT 사용 시 파일 업로드 불필요")

    # 2) Block(블록) 선택 과정(예시)
    st.subheader("2. Block 선택")
    st.info("여기서 #if ~ #else 블록 등 Legacy Feature 설정을 진행한다고 가정 (UI 생략)")
    
    # 예시 버튼: 'Block 선택 완료' 클릭 시 메시지
    if st.button("Block 선택 완료"):
        st.success("Block 선택 완료")

    # 3) Legacy Feature 설정 (기존 4열×2행 예시)
    st.subheader("3. Legacy Feature 설정")

    features = ["NR_NSA", "NR_DSS", "NR_SA", "NR_SA_DSS", "NR_VONR", "NR_NSA_NRCA", "NR_SA_NRCA"]
    feature_modes = {}
    num_cols = 4
    num_rows = math.ceil(len(features) / num_cols)

    for r in range(num_rows):
        cols = st.columns(num_cols)
        for c in range(num_cols):
            idx = r * num_cols + c
            if idx < len(features):
                feat = features[idx]
                with cols[c]:
                    st.write(f"**{feat}**")
                    if new_format:
                        add_chk = st.checkbox("ADD", key=f"{feat}_add")
                        rm_chk = st.checkbox("REMOVE", key=f"{feat}_remove")
                        feature_modes[feat] = {"ADD": add_chk, "REMOVE": rm_chk}
                    else:
                        allow_chk = st.checkbox("ALLOW_MODE", key=f"{feat}_allow")
                        block_chk = st.checkbox("BLOCK_MODE", key=f"{feat}_block")
                        feature_modes[feat] = {"ALLOW_MODE": allow_chk, "BLOCK_MODE": block_chk}

    st.markdown("---")

    # 4) 최종 변환 + 결과(미리보기)
    st.subheader("4. 최종 변환")
    if st.button("최종 변환 완료"):
        # (a) 검증: 두 항목 동시 체크 안되게
        for feat, mode_dict in feature_modes.items():
            if sum(mode_dict.values()) > 1:
                st.error(f"[{feat}]에서 2개 이상 동시에 체크되었습니다. 다시 설정하세요.")
                return

        # (b) 파일 정보 (if not new_format)
        file_info = "NEW FORMAT (파일 없음)"
        if not new_format and uploaded_file:
            file_bytes = uploaded_file.read()
            file_info = f"{len(file_bytes)} bytes"

        # (c) JSON 생성 (간단 예시)
        result_json = create_cf_json(
            new_format=new_format,
            solution="MTK" if not new_format else "SLSI",  # 예시
            mcc_mnc="123456",  # 예시 값
            feature_config=feature_modes,
            file_info=file_info
        )

        st.success("최종 변환 완료!")
        
        st.write("**CF JSON (미리보기)**")
        st.json(result_json)

        # (d) DataFrame 미리보기 (가로폭 최대)
        # 예: feature_modes를 DF 변환해 시연
        import pandas as pd
        rows = []
        for feat, mode_dict in feature_modes.items():
            rows.append({
                "Feature": feat,
                **mode_dict
            })
        df_preview = pd.DataFrame(rows)
        st.write("**전처리 결과(미리보기)**")
        st.dataframe(df_preview, use_container_width=True)  # 가로 끝까지

        st.download_button(
            label="JSON 다운로드",
            data=json.dumps(result_json, ensure_ascii=False, indent=2),
            file_name="final_cf.json",
            mime="application/json"
        )
    else:
        st.info("Block 선택 및 Legacy Feature 설정 후 최종 변환 버튼을 누르세요.")
```

---

### 코드 설명

1. **파일 업로드**  
   - **NEW FORMAT** 체크 여부(`new_format`)에 따라 파일 업로드 표시:  
     - `if not new_format: st.file_uploader(...)`  
     - 업로드 완료 시 `st.success("파일 업로드 완료!")`

2. **Block 선택 과정** (간단 예시)  
   - 실제로 **A/B/Skip** 로직이 있을 수 있으나, 여기서는 **`st.info(...)`**와 **“Block 선택 완료”** 버튼만 추가  
   - 클릭 시 `st.success("Block 선택 완료")` 메시지 표시.

3. **Legacy Feature 설정**  
   - 7개 Feature를 4열×2행으로 배치.  
   - **NEW FORMAT**이면 **ADD/REMOVE**, 아니면 **ALLOW_MODE/BLOCK_MODE** 체크박스.  
   - 사용자 체크 결과는 `feature_modes[feat] = {...}` 딕셔너리에 저장.

4. **최종 변환**  
   - “최종 변환 완료” 버튼 클릭:  
     - **검증**: 2개 동시 체크 불가  
     - **파일 정보**: `.read()`로 용량 확인(NEW FORMAT이면 없음)  
     - **`create_cf_json(...)`** 호출 → CF JSON 생성  
     - **JSON 미리보기** + **DF 미리보기**(가로 끝까지: `use_container_width=True`)  
     - **JSON 다운로드 버튼**

5. **메시지**  
   - “파일 업로드 완료”(파일 정상 업로드 시)  
   - “Block 선택 완료”(버튼 클릭 시)  
   - “최종 변환 완료”(최종 변환 버튼 클릭 후)  

---

### UI에서 가로 화면 끝까지 확장

- **`st.dataframe(df, use_container_width=True)`**  
  또는  
- **`st.write(df.style.set_properties(**{'width': '100%'}))`**  
  정도로 가능하지만, Streamlit에서는 **`use_container_width=True`**가 가장 간단합니다.

---

## 마무리

이렇게 **기존 구조**(NEW FORMAT 체크, 파일 업로드, Block 선택, Legacy Feature 설정)를 유지하면서,  
- 업로드 완료 → **“파일 업로드 완료!”**  
- Block 선택 버튼 → **“Block 선택 완료!”**  
- 최종 변환 버튼 → **“최종 변환 완료!”** + 미리보기 **가로 폭 최대**  
을 모두 구현할 수 있습니다. 

**원하는 로직**(A/B/Skip 파싱 등)은 필요에 따라 추가/수정해 보세요.  
**프로젝트 성공**을 응원합니다!
