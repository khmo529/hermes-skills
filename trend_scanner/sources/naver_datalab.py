# -*- coding: utf-8 -*-
"""
네이버 데이터랩 — 검색어 트렌드
실제 API는 로그인/쿠키 필요하므로 데모 모드를 기본 제공
"""
from __future__ import annotations
import logging
from typing import List, Dict, Any
from datetime import datetime, date

logger = logging.getLogger("trend-scanner")


DEMO_KEYWORDS = [
    "2026 청년도약계좌 금리",
    "청년희망적금 신청",
    "주식 양도소득세",
    "ETF 분산투자",
    "고배당주 순위",
    "연금저축 펀드",
    "금리 인상 전망",
    "환율 원화 약세",
    "코인 세금 신고",
    "절세 IRP 이체",
]


def _demo_items() -> List[Dict[str, Any]]:
    today = date.today().toordinal()
    items: List[Dict[str, Any]] = []
    for idx, kw in enumerate(DEMO_KEYWORDS):
        growth = round(0.1 + (idx % 5) * 0.25, 2)
        score = 20 + idx * 8
        items.append({
            "keyword": kw,
            "source": "naver_datalab",
            "trend": f"+{int(growth * 100)}%",
            "score": score,
            "growth": growth,
            "days": 7 + idx * 10,
            "snippet": f"네이버 검색량 상승 {kw}",
        })
    return items


def fetch() -> List[Dict[str, Any]]:
    logger.warning("네이버 데이터랩: 데모 데이터 사용 (실제 API 연동 필요)")
    return _demo_items()
