---
created: 2025-03-24T10:58:45+09:00
modified: 2025-03-24T10:58:58+09:00
---

# 2025-03-24-json_utils.py#1

# modules/json_utils.py

def create_cf_json(mcc_mnc, feature_config):
    """
    mcc_mnc (str): 사용자 입력 MCC_MNC
    feature_config (dict): 예: { 'NSA': {'ADD': True, 'REMOVE': False}, ... }
    
    반환: CF 파일로 쓸 JSON(dict)
    """
    # CF 데이터 구조 예시
    cf_data = {
        "format": "NEW",
        "mcc_mnc": mcc_mnc,
        "features": []
    }

    # feature_config 딕셔너리를 순회하며 구성
    for feat, options in feature_config.items():
        # ADD/REMOVE 체크 여부에 따라 로직
        item = {
            "feature": feat,
            "add": bool(options.get("ADD")),
            "remove": bool(options.get("REMOVE"))
        }
        cf_data["features"].append(item)

    return cf_data
