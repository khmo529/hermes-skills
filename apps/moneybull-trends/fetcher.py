#!/usr/bin/env python3
"""MoneyBull 실시간 금융 트렌드 수집기.

Sources:
- Naver DataLab 검색어 트렌드
- Google Trends (pytrends)
- KRX 금/달러 시세

Output: trends.json (finance keywords only)
"""
from __future__ import annotations

import json
import os
import sys
import time
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:
    requests = None

try:
    from pytrends.request import TrendReq
except ImportError:
    TrendReq = None

try:
    import pandas as pd
except ImportError:
    pd = None

KST = timezone(timedelta(hours=9))
BASE_DIR = Path(__file__).resolve().parent
OUT_FILE = BASE_DIR / "trends.json"
CACHE_TTL_SECONDS = 55  # slightly less than 1 minute polling interval


@dataclass
class TrendItem:
    keyword: str
    category: str  # ISA | 적금 | 예금 | 금리 | 금값 | 달러 | 주식 | 코인
    rank: int
    score: float
    change_pct: float
    label: str  # new | up | down | stable
    related_posts: list[dict[str, Any]] = field(default_factory=list)
    updated_at: str = field(default_factory=lambda: datetime.now(KST).isoformat())
    meta: dict[str, Any] = field(default_factory=dict)


# Finance-only allow-list tokens for naive filtering
FINANCE_TOKENS = [
    "ISA", "ISA계좌", "금", "금값", "달러", "환율", "예금", "적금", "주식", "코인",
    "비트코인", "이더리움", "금리", "적금 이자", "예금 이자", "달러 투자", "달러 환전",
    "금 투자", "KRX", "국고채", "채권", "펀드", "보험", "카드", "은행", "증권", "ETF",
    "배당주", "리츠", "REITs", "원유", "원자재", "금융", "투자", "저축", "연금",
]


def _finance_filter(keywords: list[str]) -> list[str]:
    out = []
    for kw in keywords:
        for token in FINANCE_TOKENS:
            if token.lower() in kw.lower():
                out.append(kw)
                break
    # de-dup preserving order
    seen: set[str] = set()
    result = []
    for kw in out:
        if kw not in seen:
            seen.add(kw)
            result.append(kw)
    return result


def _latest_cache() -> dict[str, Any] | None:
    if not OUT_FILE.exists():
        return None
    try:
        data = json.loads(OUT_FILE.read_text(encoding="utf-8"))
        updated = datetime.fromisoformat(data.get("updated_at", ""))
        if updated.tzinfo is None:
            updated = updated.replace(tzinfo=KST)
        if datetime.now(KST) - updated < timedelta(seconds=CACHE_TTL_SECONDS):
            return data
    except Exception:
        return None
    return None


def fetch_naver_datalab() -> list[dict[str, Any]]:
    if not requests:
        return []
    client_id = os.getenv("NAVER_DATALAB_CLIENT_ID")
    client_secret = os.getenv("NAVER_DATALAB_CLIENT_SECRET")
    if not client_id or not client_secret:
        return []
    url = "https://openapi.naver.com/v1/datalab/search"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
        "Content-Type": "application/json",
    }
    end = datetime.now(KST)
    start = end - timedelta(hours=2)
    body = {
        "startDate": start.strftime("%Y-%m-%d"),
        "endDate": end.strftime("%Y-%m-%d"),
        "timeUnit": "minute",
        "keywordGroups": [
            {
                "groupName": "금융",
                "keywords": [
                    "ISA", "예금", "적금", "금리", "금값", "달러", "주식", "코인", "비트코인"
                ],
            }
        ],
        "device": "",
        "ages": [],
        "gender": "",
    }
    try:
        resp = requests.post(url, headers=headers, json=body, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        items = []
        for group in data.get("results", []):
            for d in group.get("data", []):
                items.append(
                    {
                        "keyword": group.get("groupName", "금융"),
                        "period": d.get("period"),
                        "ratio": float(d.get("ratio", 0)),
                    }
                )
        return items
    except Exception as exc:
        print(f"[NAVER] error: {exc}", file=sys.stderr)
        return []


def fetch_google_trends() -> list[str]:
    if TrendReq is None:
        return []
    try:
        pytrends = TrendReq(hl="ko-KR", tz=540)
        kw = ["ISA", "예금", "적금", "금리", "금값", "달러", "주식", "코인"]
        pytrends.build_payload(kw, timeframe="now 1-H")
        df = pytrends.interest_over_time()
        if df is None or df.empty:
            return []
        df = df.drop(columns=["isPartial"], errors="ignore")
        current = df.iloc[-1]
        ranked = sorted([(int(current[k]), k) for k in kw], reverse=True)
        return [k for _, k in ranked[:10]]
    except Exception as exc:
        print(f"[GOOGLE] error: {exc}", file=sys.stderr)
        return []


def fetch_krx_rates() -> dict[str, Any]:
    if not requests:
        return {}
    out: dict[str, Any] = {}
    try:
        url = "https://api.odcloud.kr/api/uris001ws/getGoldPriceInfo?page=1&perPage=5&serviceKey=DUMMY"
        # 실패해도 전체 파이프라인은 중단하지 않는다.
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            out["gold"] = data
    except Exception as exc:
        print(f"[KRX] gold error: {exc}", file=sys.stderr)
    try:
        url = "https://api.odcloud.kr/api/uris001ws/getExchangeRate?page=1&perPage=5&serviceKey=DUMMY"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            out["fx"] = data
    except Exception as exc:
        print(f"[KRX] fx error: {exc}", file=sys.stderr)
    return out


def _inject_related_posts(keywords: list[str], limit: int = 3) -> list[dict[str, Any]]:
    """Naver/Google에서 나온 키워드를 MoneyBull 내부 검색 링크로 연결."""
    return [
        {
            "title": f"{kw} 최신 동향",
            "url": f"/?s={requests.utils.quote(kw)}" if requests else f"/?s={kw}",
        }
        for kw in keywords[:limit]
    ]


def collect() -> dict[str, Any]:
    cached = _latest_cache()
    if cached:
        return cached

    naver_items = fetch_naver_datalab()
    google_kw = fetch_google_trends()
    krx = fetch_krx_rates()

    # build candidate pool
    candidates: list[TrendItem] = []
    for item in naver_items:
        if item.get("ratio", 0) > 0:
            candidates.append(
                TrendItem(
                    keyword=item.get("keyword", ""),
                    category="금융",
                    rank=0,
                    score=float(item.get("ratio", 0)),
                    change_pct=0.0,
                    label="stable",
                )
            )
    google_filtered = _finance_filter(google_kw)
    for idx, kw in enumerate(google_filtered, start=1):
        candidates.append(
            TrendItem(
                keyword=kw,
                category="금융",
                rank=idx,
                score=100 - idx * 7,
                change_pct=20.0 if idx <= 3 else -5.0,
                label="up" if idx <= 3 else "stable",
            )
        )

    # dedupe by keyword with best score
    best: dict[str, TrendItem] = {}
    for c in candidates:
        if c.keyword not in best or c.score > best[c.keyword].score:
            best[c.keyword] = c
    merged = sorted(best.values(), key=lambda x: x.score, reverse=True)[:15]

    # assign ranks
    for i, item in enumerate(merged, start=1):
        item.rank = i
        if item.change_pct >= 20:
            item.label = "up"
            item.meta["fire"] = True
        elif item.change_pct <= -15:
            item.label = "down"
        elif item.label not in {"new", "up", "down"}:
            item.label = "stable"
        item.related_posts = _inject_related_posts([item.keyword])

    trends = [asdict(t) for t in merged]
    payload = {
        "source": "moneybull-realtime-trends",
        "updated_at": datetime.now(KST).isoformat(),
        "count": len(trends),
        "trends": trends,
        "market": {
            "gold": krx.get("gold"),
            "fx": krx.get("fx"),
        },
    }
    try:
        OUT_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass
    return payload


def main() -> int:
    print(json.dumps(collect(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
