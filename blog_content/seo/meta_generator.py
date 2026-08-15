from __future__ import annotations

import re

from blog_content.seo.keyword_analyzer import analyze_keyword


def _truncate(text: str, limit: int) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def generate_seo_metadata(keyword: str, analysis: dict[str, Any] | None, body: str) -> dict:
    analysis = analysis or analyze_keyword(keyword)
    focus_keyword = keyword.strip()
    title = _truncate(f"2026 {focus_keyword} 신청 자격 및 방법 | 한눈에 보기", 60)
    description = _truncate(
        f"{focus_keyword}에 대한 신청 조건, 절차, 필요 서류, 문의처까지 정리했습니다. 최신 정보로 쉽게 확인하세요.",
        155,
    )
    headings = re.findall(r"^##\s+(.+)$", body, flags=re.MULTILINE)
    internal_links = [
        "관련 지원금 비교 정리",
        "신청 서류 체크리스트",
        "정부24 바로가기",
        "기관별 공식 안내",
    ][:3]

    return {
        "focus_keyword": focus_keyword,
        "seo_title": title,
        "meta_description": description,
        "intent": analysis.get("intent"),
        "category": analysis.get("category"),
        "cpc_band": analysis.get("cpc_band"),
        "headings": headings,
        "internal_links": internal_links,
    }
