#!/usr/bin/env python3
"""
Hermes MoneyBull Pipeline
trend-scanner -> blog-content -> wp-publisher
일일 1개 Draft 생성 + Discord 승인 알림
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _ensure_repo_on_path() -> None:
    repo_root = str(ROOT)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def run(top_n: int = 1, publish: bool = False) -> int:
    _ensure_repo_on_path()

    from trend_scanner.trend_scanner import run_pipeline as scan_pipeline  # type: ignore
    from blog_content.blog_content import generate_draft  # type: ignore
    from wp_publisher.wp_publisher import WPPublisher  # type: ignore
    from discord_notifier import DiscordNotifier  # type: ignore

    print("=== Hermes Pipeline 시작 ===")

    print("Step 1/2: trend-scanner -> blog-content")
    trends = scan_pipeline(top_n=max(top_n, 1))
    if not trends:
        print("발굴된 트렌드가 없어 파이프라인을 종료합니다.")
        return 0

    top = trends[0]
    draft = generate_draft(top)
    print(f"초안 생성 완료: {draft.get('keyword')} ({draft.get('category')})")

    post_id = None
    if publish:
        print("Step 2/2: blog-content -> wp-publisher")
        try:
            publisher = WPPublisher()
            meta = _build_rank_math_meta(draft)
            post_id = publisher.create_draft(
                title=draft.get("title") or draft.get("keyword", "Untitled"),
                content=draft.get("content", ""),
                category=draft.get("category"),
                tags=(draft.get("meta") or {}).get("tags") or [],
                status="draft",
                meta=meta,
            )
        except Exception as exc:
            print(f" - Draft 게시 실패: {draft.get('keyword')} — {exc}")

    DiscordNotifier().send_draft_notification(
        post_id=post_id or 0,
        title=draft.get("title") or draft.get("keyword", "Untitled"),
        keyword=draft.get("keyword", ""),
    )

    print("=== Pipeline 완료 ===")
    return 0


def _build_rank_math_meta(draft: Dict[str, Any]) -> Dict[str, Any]:
    meta = draft.get("meta", {}) or {}
    title = draft.get("title") or draft.get("keyword", "Untitled")
    focus = meta.get("focus_keyword") or draft.get("keyword", "")
    seo_title = meta.get("seo_title") or title
    seo_desc = meta.get("seo_description") or ""
    return {
        "rank_math_focus_keyword": focus,
        "rank_math_title": seo_title,
        "rank_math_description": seo_desc,
        "_yoast_wpseo_focuskw": focus,
        "_yoast_wpseo_title": seo_title,
        "_yoast_wpseo_metadesc": seo_desc,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--top-n", type=int, default=1)
    args = parser.parse_args()
    raise SystemExit(run(top_n=args.top_n, publish=args.publish))
