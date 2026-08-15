# -*- coding: utf-8 -*-
"""
기획재정부 보도자료 — RSS/JSON 파서
현재 엔드포인트는 HTML 페이지를 반환합니다.
"""
from __future__ import annotations
import logging
from typing import List, Dict, Any

import requests

logger = logging.getLogger("trend-scanner")


RSS_URL = "https://www.moef.go.kr/nw/nes/rss/naver/rssNewsDetail.do?mid=mw3_111000000000000"


def fetch() -> List[Dict[str, Any]]:
    try:
        headers = {"User-Agent": "trend-scanner/1.0 (+https://example.com)"}
        r = requests.get(RSS_URL, headers=headers, timeout=20)
        r.raise_for_status()
        if "text/html" in r.headers.get("Content-Type", ""):
            logger.error("기획재정부 RSS가 HTML을 반환합니다. 피드 주소를 확인하세요.")
            return []
    except Exception as exc:
        logger.error(f"기획재정부 RSS 요청 실패: {exc}")
        return []

    logger.info("기획재정부 후보: 0건")
    return []
