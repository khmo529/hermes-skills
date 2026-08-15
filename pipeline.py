#!/usr/bin/env python3
"""
Hermes MoneyBull Pipeline
trend-scanner -> blog-content -> wp-publisher
일일 1개 Draft 생성 + Telegram 승인 알림
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

    print("=== Hermes Pipeline 시작 ===")

    print("Step 1/2: trend-scanner -> blog-content")
    trends = scan_pipeline(top_n=max(top_n, 1))
    if not trends:
        print("발굴된 트렌드가 없어 파이프라인을 종료합니다.")
        return 0

    item = trends[0]
    draft = generate_draft(item)
    print(f"초안 생성 완료: {draft.get('keyword')} ({draft.get('category')})")

    post_id = None
    if publish:
        print("Step 2/2: blog-content -> wp-publisher")
        try:
            from wp_publisher.wp_publisher import WPPublisher  # type: ignore
            publisher = WPPublisher()
            payload = _build_wp_payload(draft)
            import requests
            r = requests.post(
                f"{publisher.url}/wp-json/wp/v2/posts",
                json=payload,
                auth=(publisher.user, publisher.password),
                timeout=30,
            )
            if r.status_code == 201:
                post_id = r.json()["id"]
                print(f"✅ Draft 생성: ID {post_id} — {payload['title']}")
            else:
                raise RuntimeError(f"게시 실패 HTTP {r.status_code}: {r.text[:300]}")
        except Exception as exc:
            print(f" - Draft 게시 실패: {draft.get('keyword')} — {exc}")

    _notify_telegram(draft, post_id)

    print("=== Pipeline 완료 ===")
    return 0


def _build_wp_payload(draft: Dict[str, Any]) -> Dict[str, Any]:
    meta = draft.get("meta", {}) or {}
    title = draft.get("title") or draft.get("keyword", "Untitled")
    content = draft.get("content", "")
    category = draft.get("category") or meta.get("category") or "general"
    tags = meta.get("tags") or []
    seo_title = meta.get("seo_title") or title
    seo_desc = meta.get("seo_description") or ""
    focus = meta.get("focus_keyword") or draft.get("keyword", "")

    payload: Dict[str, Any] = {
        "title": title,
        "content": content,
        "status": "draft",
        "meta": {
            "rank_math_focus_keyword": focus,
            "rank_math_title": seo_title,
            "rank_math_description": seo_desc,
            "_yoast_wpseo_focuskw": focus,
            "_yoast_wpseo_title": seo_title,
            "_yoast_wpseo_metadesc": seo_desc,
        },
    }
    slug = meta.get("slug")
    if slug:
        payload["slug"] = slug
    return payload


def _notify_telegram(draft: Dict[str, Any], post_id: Optional[int]) -> None:
    try:
        from telegram_bot import TelegramBot  # type: ignore
        bot = TelegramBot()
        bot.send_draft_notification(
            post_id=post_id or 0,
            title=draft.get("title") or draft.get("keyword", "Untitled"),
            keyword=draft.get("keyword", ""),
        )
        print("✅ Telegram 알림 전송 완료")
    except Exception as exc:
        print(f"ℹ️ Telegram 알림 건너뜀: {exc}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--top-n", type=int, default=1)
    args = parser.parse_args()
    raise SystemExit(run(top_n=args.top_n, publish=args.publish))
