from __future__ import annotations

from typing import Any


def analyze_keyword(keyword: str) -> dict[str, Any]:
    lowered = keyword.lower()
    if any(k in lowered for k in ["지원금", "보조금", "환급", "신청"]):
        intent = "transactional"
        category = "government"
        cpc_band = "medium-high"
    elif any(k in lowered for k in ["카드", "적금", "예금", "대출", "금리"]):
        intent = "transactional"
        category = "finance"
        cpc_band = "medium"
    elif any(k in lowered for k in ["절세", "종합소득세", "환급"]):
        intent = "transactional"
        category = "tax"
        cpc_band = "medium-high"
    else:
        intent = "informational"
        category = "moneybull"
        cpc_band = "low-medium"
    return {"keyword": keyword, "intent": intent, "category": category, "cpc_band": cpc_band}
