# -*- coding: utf-8 -*-
"""
금융위원회 보도자료 — RSS 파서
현재 엔드포인트가 404입니다.
"""
from __future__ import annotations
import logging
from typing import List, Dict, Any

logger = logging.getLogger("trend-scanner")


def fetch() -> List[Dict[str, Any]]:
    logger.error("금융위원회 RSS 엔드포인트가 유효하지 않습니다. 주소를 확인하세요.")
    return []
