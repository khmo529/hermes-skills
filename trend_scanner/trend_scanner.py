# -*- coding: utf-8 -*-
"""
trend-scanner — 금융/정부/재테크 글감 자동 발굴
"""
from __future__ import annotations
import os
import sys
import json
import logging
import datetime
from typing import List, Dict, Any
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trend_scanner.sources import google_trends, gov24, moef, fsc
from trend_scanner.sources import naver_datalab

# ──────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output" / "trends"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

KEYWORD_CATEGORIES = [
    "정부지원금", "정책", "주식", "ETF", "배당", "금리", "환율",
    "은행", "연금", "세금", "절세", "코인", "재테크", "투자",
    "경제지표", "물가", "적금", "청년정책", "퇴직연금", "펀드",
]

FINANCE_KEYWORDS = [
    "계좌", "금리", "투자", "주식", "ETF", "펀드", "배당", "연금",
    "은행", "저축", "적금", "예금", "보험", "세금", "절세", "환율",
    "물가", "인플레이션", "코인", "암호화폐", "부동산", "대출",
    "카드", "신용", "퇴직", "청년", "정책", "지원금", "수당",
]

MIN_GROWTH = 0.30  # 30%
MIN_SUSTAIN_DAYS = 90

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("trend-scanner")


# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────

def _category_for(keyword: str) -> str:
    kw = keyword.lower()
    for cat in KEYWORD_CATEGORIES:
        if cat in kw:
            return cat
    return "기타"


def _estimated_cpc(trend_score: int, category: str) -> str:
    if category in ["정부지원금", "정책", "청년정책"]:
        return "high"
    if trend_score >= 80:
        return "high"
    if trend_score >= 50:
        return "medium"
    return "low"


def _sustainability(days: int) -> str:
    if days >= MIN_SUSTAIN_DAYS:
        return "high"
    if days >= 30:
        return "medium"
    return "low"


def _filter_keywords(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    filtered: List[Dict[str, Any]] = []
    for item in items:
        growth = item.get("growth", 0)
        if isinstance(growth, str):
            try:
                growth = float(growth.replace("%", "").replace("+", "")) / 100.0
            except Exception:
                growth = 0
        if growth < MIN_GROWTH:
            continue

        keyword = item.get("keyword", "")
        category = item.get("category") or _category_for(keyword)
        cat_match = any(k in keyword for k in FINANCE_KEYWORDS) or category != "기타"
        if not cat_match:
            continue

        item["category"] = category
        item["estimated_cpc"] = _estimated_cpc(item.get("score", 0), category)
        item["sustainability"] = _sustainability(item.get("days", 0))
        filtered.append(item)

    filtered.sort(key=lambda x: x.get("score", 0), reverse=True)
    for idx, item in enumerate(filtered, 1):
        item["rank"] = idx

    return filtered


# ──────────────────────────────────────────────
# COLLECTORS
# ──────────────────────────────────────────────

def collect_all() -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []

    sources = [
        ("google_trends", google_trends.fetch),
        ("naver_datalab", naver_datalab.fetch),
        ("gov24", gov24.fetch),
        ("moef", moef.fetch),
        ("fsc", fsc.fetch),
    ]

    for name, fetcher in sources:
        try:
            logger.info(f"소스 수집 시작: {name}")
            result = fetcher()
            if isinstance(result, list):
                items.extend(result)
            else:
                items.append(result)
            logger.info(f"소스 수집 완료: {name} — {len(result) if isinstance(result, list) else 1}건")
        except Exception as exc:
            logger.error(f"소스 수집 실패: {name} — {exc}")

    return items


# ──────────────────────────────────────────────
# OUTPUT
# ──────────────────────────────────────────────

def save_trends(items: List[Dict[str, Any]]) -> str:
    today = datetime.date.today().isoformat()
    path = OUTPUT_DIR / f"daily_{today}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    logger.info(f"결과 저장 완료: {path} ({len(items)}건)")
    return str(path)


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

def main() -> int:
    logger.info("trend-scanner 실행 시작")
    items = collect_all()
    filtered = _filter_keywords(items)
    path = save_trends(filtered)
    print(f"\n오늘의 글감 후보: {len(filtered)}건")
    print(f"저장 경로: {path}")
    for item in filtered[:10]:
        print(
            f"  #{item.get('rank')} {item.get('keyword')} "
            f"({item.get('source')}, {item.get('trend')}, {item.get('category')})"
        )
    logger.info("trend-scanner 실행 완료")
    return 0


def run_pipeline(top_n: int = 3, output_dir: str | None = None):
    repo_root = BASE_DIR.parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    base_output = Path(output_dir) if output_dir else BASE_DIR / "output" / "pipeline"
    base_output.mkdir(parents=True, exist_ok=True)

    from blog_content.blog_content import generate_draft, save_draft

    items = collect_all()
    filtered = _filter_keywords(items)
    trends = filtered[: max(1, int(top_n))]

    results = []
    for trend in trends:
        keyword = trend.get("keyword") or trend.get("title") or ""
        category = trend.get("category") or "moneybull"
        experience_notes = trend.get("experience_notes")

        draft = generate_draft(
            {
                "keyword": keyword,
                "category": category,
                "experience_notes": experience_notes,
                "trend": trend,
            }
        )
        md_path, meta_path = save_draft(keyword, draft, base_output)
        try:
            meta_dict = json.loads(Path(meta_path).read_text(encoding="utf-8"))
        except Exception:
            meta_dict = {}
        results.append(
            {
                "keyword": keyword,
                "category": category,
                "trend": trend,
                "md": str(md_path),
                "meta": meta_dict,
                "title": draft.get("title"),
                "content": draft.get("content"),
            }
        )
    return results


if __name__ == "__main__":
    sys.exit(main())
