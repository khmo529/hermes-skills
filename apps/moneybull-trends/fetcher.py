#!/usr/bin/env python3
"""MoneyBull 실시간 금융 트렌드 수집기.

Sources:
- Naver DataLab 검색어 트렌드
- Naver 금융 급상승 크롤링 (https://www.naver.com/srng/chartrank?cat=finance)
- KRX 금/달러 시세 (polling.finance.naver.com, m.stock.naver.com)

Output: trends.json (finance keywords only)
"""
from __future__ import annotations

import json
import os
import sys
import time
import random
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    requests = None

try:
    from pytrends.request import TrendReq
except ImportError:
    TrendReq = None

KST = timezone(timedelta(hours=9))
BASE_DIR = Path(__file__).resolve().parent
OUT_FILE = BASE_DIR / "trends.json"
CACHE_TTL_SECONDS = 55

UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
]


def _session() -> Any:
    if requests is None:
        raise RuntimeError("requests not installed")
    s = requests.Session()
    s.headers.update({"User-Agent": random.choice(UA_POOL), "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.5"})
    retries = Retry(total=2, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.mount("http://", HTTPAdapter(max_retries=retries))
    return s


def _jitter(lo: float = 0.4, hi: float = 1.4) -> None:
    time.sleep(random.uniform(lo, hi))


@dataclass
class TrendItem:
    keyword: str
    category: str
    rank: int
    score: float
    change_pct: float
    label: str
    related_posts: list[dict[str, Any]] = field(default_factory=list)
    updated_at: str = field(default_factory=lambda: datetime.now(KST).isoformat())
    meta: dict[str, Any] = field(default_factory=dict)


FINANCE_TOKENS = [
    "ISA", "ISA계좌", "금", "금값", "달러", "환율", "예금", "적금", "주식", "코인",
    "비트코인", "이더리움", "금리", "적금 이자", "예금 이자", "달러 투자", "달러 환전",
    "금 투자", "KRX", "국고채", "채권", "펀드", "보험", "카드", "은행", "증권", "ETF",
    "배당주", "리츠", "REITs", "원유", "원자재", "금융", "투자", "저축", "연금",
    "부동산", "부동산 투자", "전세", "월세", "주담대", "디딤돌", "보금자리",
]


def _finance_filter(keywords: list[str]) -> list[str]:
    out: list[str] = []
    for kw in keywords:
        for token in FINANCE_TOKENS:
            if token.lower() in kw.lower():
                out.append(kw)
                break
    seen: set[str] = set()
    result: list[str] = []
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
    if requests is None:
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
        _jitter(0.3, 0.8)
        resp = requests.post(url, headers=headers, json=body, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        items: list[dict[str, Any]] = []
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


def fetch_naver_finance_rise() -> list[str]:
    if requests is None:
        return []
    url = "https://www.naver.com/srch/chartrank?cat=finance"
    try:
        _jitter(0.5, 1.2)
        s = _session()
        resp = s.get(url, timeout=10)
        resp.raise_for_status()
        text = resp.text
        keywords: list[str] = []
        # heuristic parsing from chartrank anchors
        for part in text.split("rankItem")[:20]:
            if "title" in part and "href" in part:
                try:
                    title = part.split('title="')[1].split('"')[0]
                except Exception:
                    continue
                title = title.strip()
                if title:
                    keywords.append(title)
        return keywords[:20]
    except Exception as exc:
        print(f"[NAVER_FINANCE] error: {exc}", file=sys.stderr)
        return []


def fetch_krx_rates() -> dict[str, Any]:
    if requests is None:
        return {}
    out: dict[str, Any] = {}
    try:
        url = "https://polling.finance.naver.com/api/realtime?query=SERVICE_ITEM:000215"
        _jitter(0.3, 0.9)
        s = _session()
        resp = s.get(url, timeout=8)
        if resp.status_code == 200:
            out["gold"] = resp.json()
    except Exception as exc:
        print(f"[KRX] gold error: {exc}", file=sys.stderr)
    try:
        url = "https://m.stock.naver.com/api/stocks/finance/marketIndex"
        _jitter(0.3, 0.9)
        s = _session()
        resp = s.get(url, timeout=8)
        if resp.status_code == 200:
            out["fx"] = resp.json()
    except Exception as exc:
        print(f"[KRX] fx error: {exc}", file=sys.stderr)
    return out


def _inject_related_posts(keywords: list[str], limit: int = 3) -> list[dict[str, Any]]:
    return [
        {
            "title": f"{kw} 최신 동향",
            "url": f"/?s={requests.utils.quote(kw) if requests else kw}",
        }
        for kw in keywords[:limit]
    ]


def collect() -> dict[str, Any]:
    cached = _latest_cache()
    if cached:
        return cached

    naver_items = fetch_naver_datalab()
    naver_kw = fetch_naver_finance_rise()
    krx = fetch_krx_rates()

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

    ranked_kw: list[str] = []
    seen: set[str] = set()
    for kw in naver_kw:
        kw = kw.strip()
        if not kw or kw in seen:
            continue
        seen.add(kw)
        ranked_kw.append(kw)

    finance_ranked = _finance_filter(ranked_kw)
    for idx, kw in enumerate(finance_ranked, start=1):
        score = float(100 - idx * 7)
        change_pct = 28.0 if idx <= 2 else (18.0 if idx <= 5 else (-6.0 if idx > 10 else 0.0))
        candidates.append(
            TrendItem(
                keyword=kw,
                category="금융",
                rank=idx,
                score=score,
                change_pct=change_pct,
                label="up" if change_pct >= 20 else ("new" if idx <= 3 else "stable"),
            )
        )

    best: dict[str, TrendItem] = {}
    for c in candidates:
        if c.keyword not in best or c.score > best[c.keyword].score:
            best[c.keyword] = c
    merged = sorted(best.values(), key=lambda x: x.score, reverse=True)[:15]

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
