#!/usr/bin/env python3
"""
Hermes MoneyBull Pipeline
trend-scanner -> blog-content -> wp-publisher
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


def run(top_n: int = 3, publish: bool = False) -> int:
    _ensure_repo_on_path()

    from trend_scanner.trend_scanner import run_pipeline as scan_pipeline  # type: ignore
    from blog_content.blog_content import publish_draft  # type: ignore

    print("=== Hermes Pipeline 시작 ===")

    print("Step 1/2: trend-scanner -> blog-content")
    drafts = scan_pipeline(top_n=top_n)
    if not drafts:
        print("발굴된 트렌드가 없어 파이프라인을 종료합니다.")
        return 0

    print(f"초안 생성 완료: {len(drafts)}건")
    for d in drafts:
        print(f" - {d['keyword']} ({d['category']})")

    if publish:
        print("Step 2/2: blog-content -> wp-publisher")
        for d in drafts:
            try:
                result = publish_draft(d, status="draft")
                print(f" - Draft 게시 완료: {result['title']} (ID {result['post_id']})")
            except Exception as exc:
                print(f" - Draft 게시 실패: {d['keyword']} — {exc}")

    print("=== Pipeline 완료 ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
