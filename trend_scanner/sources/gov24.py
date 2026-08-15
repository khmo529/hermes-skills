# -*- coding: utf-8 -*-
"""
정부24 새소식 — RSS 파서
현재 RSS는 메타데이터만 제공하고 있습니다.
"""
from __future__ import annotations
import logging
from typing import List, Dict, Any

import requests

logger = logging.getLogger("trend-scanner")


RSS_URL = "https://www.gov.kr/portal/rss/newsservice.xml"


def fetch() -> List[Dict[str, Any]]:
    try:
        headers = {"User-Agent": "trend-scanner/1.0 (+https://example.com)"}
        r = requests.get(RSS_URL, headers=headers, timeout=20)
        r.raise_for_status()
        if "text/html" in r.headers.get("Content-Type", ""):
            logger.error("정부24 RSS가 HTML을 반환합니다. 피드 주소를 확인하세요.")
            return []
    except Exception as exc:
        logger.error(f"정부24 RSS 요청 실패: {exc}")
        return []

    logger.info("정부24 후보: 0건")
    return []
