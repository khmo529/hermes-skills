# -*- coding: utf-8 -*-
"""
Google Trends — pytrends 기반
"""
from __future__ import annotations
import logging
from typing import List, Dict, Any

logger = logging.getLogger("trend-scanner")


def fetch() -> List[Dict[str, Any]]:
    try:
        from pytrends.request import TrendReq
    except ImportError:
        logger.warning("pytrends 미설치. Google Trends 소스를 건너뜁니다.")
        return []

    pytrends = TrendReq(hl="ko-KR", tz=540)
    keywords = ["청년도약계좌", "주식 투자", "ETF", "배당주", "연금"]

    try:
        pytrends.build_payload(keywords, timeframe="now 7-d", geo="KR")
        interest = pytrends.interest_over_time()
    except Exception as exc:
        logger.error(f"Google Trends 요청 실패: {exc}")
        return []

    if interest is None or interest.empty:
        return []

    results: List[Dict[str, Any]] = []
    for kw in keywords:
        if kw not in interest.columns:
            continue
        values = interest[kw].dropna()
        if len(values) < 2:
            continue
        current = int(values.iloc[-1])
        previous = int(values.iloc[0])
        if previous == 0:
            continue
        growth = (current - previous) / previous
        if growth <= 0:
            continue
        days = len(values)
        results.append({
            "keyword": kw,
            "source": "google_trends",
            "trend": f"+{int(growth * 100)}%",
            "score": min(current, 100),
            "growth": growth,
            "days": days * 1,
            "snippet": f"최근 7일 검색량 {current}",
        })

    logger.info(f"Google Trends 후보: {len(results)}건")
    return results
