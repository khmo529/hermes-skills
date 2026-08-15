#!/usr/bin/env python3
"""
Hermes MoneyBull Pipeline
trend-scanner -> blog-content -> wp-publisher
일일 1개 Draft 생성 + Telegram 승인 알림 + Gutenberg 99점 변환
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parent


def _ensure_repo_on_path() -> None:
    repo_root = str(ROOT)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def run(top_n: int = 1, publish: bool = False) -> int:
    _ensure_repo_on_path()

    from trend_scanner.trend_scanner import run_pipeline as scan_pipeline  # type: ignore
    from blog_content.blog_content import generate_draft  # type: ignore
    from wp_publisher.wp_publisher import WPPublisher, markdown_to_gutenberg, _upload_media  # type: ignore
    from telegram_bot import TelegramBot  # type: ignore

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
            raw_content = draft.get("content", "")
            focus_keyword = ((draft.get("meta") or {}).get("focus_keyword") or draft.get("keyword", "")).strip()
            slug = ((draft.get("meta") or {}).get("slug") or "").strip()
            if not slug:
                slug = _make_slug(draft.get("title") or draft.get("keyword", "post"))
            uploaded_images = _upload_draft_images(draft, focus_keyword=focus_keyword)
            gutenberg_content = markdown_to_gutenberg(raw_content, uploaded_images, focus_keyword=focus_keyword)
            meta = _build_rank_math_meta(draft, slug=slug, focus_keyword=focus_keyword)
            post_id = publisher.create_draft(
                title=draft.get("title") or draft.get("keyword", "Untitled"),
                content=gutenberg_content,
                category=draft.get("category"),
                tags=(draft.get("meta") or {}).get("tags") or [],
                status="draft",
                slug=slug,
                meta=meta,
            )
        except Exception as exc:
            print(f" - Draft 게시 실패: {draft.get('keyword')} — {exc}")

    TelegramBot().send_draft_notification(
        post_id=post_id or 0,
        title=draft.get("title") or draft.get("keyword", "Untitled"),
        keyword=draft.get("keyword", ""),
    )

    print("=== Pipeline 완료 ===")
    return 0


def _make_slug(text: str) -> str:
    import re
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s]+", "-", text).strip("-")
    return text[:60]


def _build_rank_math_meta(draft: Dict[str, Any], slug: str = "", focus_keyword: str = "") -> Dict[str, Any]:
    meta = draft.get("meta", {}) or {}
    title = draft.get("title") or draft.get("keyword", "Untitled")
    focus = focus_keyword or meta.get("focus_keyword") or draft.get("keyword", "")
    seo_title = meta.get("seo_title") or title
    seo_desc = meta.get("seo_description") or ""
    if not seo_desc and focus:
        seo_desc = f"{focus} 비교·정리. 3분 만에 확인하는 방법, 수수료·우대조건 비교, 체크리스트."
    result = {
        "rank_math_focus_keyword": focus,
        "rank_math_title": seo_title,
        "rank_math_description": seo_desc[:160],
        "_yoast_wpseo_focuskw": focus,
        "_yoast_wpseo_title": seo_title,
        "_yoast_wpseo_metadesc": seo_desc[:160],
    }
    if slug:
        result["slug"] = slug
    return result


def _upload_draft_images(draft: Dict[str, Any], focus_keyword: str = "") -> Dict[str, str]:
    uploaded: Dict[str, str] = {}
    content = draft.get("content", "") or ""
    for line in content.split("\n"):
        stripped = line.strip()
        if not stripped.startswith("[이미지:"):
            continue
        src = _img_src(stripped)
        alt = _img_alt(stripped) or focus_keyword or "MoneyBull 이미지"
        path = _resolve_image_path(src)
        url = _upload_media(path, alt=alt, focus_keyword=focus_keyword)
        if url:
            uploaded[src] = url
            print(f" - 이미지 업로드: {src} -> {url}")
    return uploaded


def _img_src(line: str) -> str:
    start = line.find(":") + 1
    end = line.find("/", start)
    if end == -1:
        end = line.find("]", start)
    token = line[start:end].strip()
    if " " in token:
        token = token.split(" ")[0]
    return token


def _img_alt(line: str) -> str:
    marker = "/ ALT:"
    idx = line.find(marker)
    if idx == -1:
        return ""
    tail = line[idx + len(marker):]
    end = tail.find("]")
    if end == -1:
        end = len(tail)
    return tail[:end].strip()


def _resolve_image_path(filename: str) -> Optional[str]:
    if not filename:
        return None
    candidates = [
        ROOT / "blog_content" / "assets" / filename,
        ROOT / "assets" / filename,
        ROOT / filename,
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return None


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--top-n", type=int, default=1)
    args = parser.parse_args()
    raise SystemExit(run(top_n=args.top_n, publish=args.publish))
