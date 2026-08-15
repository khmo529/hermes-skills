# -*- coding: utf-8 -*-
"""
wp-publisher — MoneyBull WordPress REST API 연동 스킬

사용법:
    from wp_publisher import WPPublisher
    
    wp = WPPublisher()
    post_id = wp.create_draft(
        title="2026 청년도약계좌 금리 비교",
        content="<p>청년도약계좌는 만 19~34세 청년이 가입할 수 있는...</p>",
        category="policy",           # 슬러그 또는 이름
        tags=["2026청년정책", "재테크"],
        status="draft",              # publish는 Min 승인 후
    )
    print(f"Draft 생성: {post_id}")
"""

from __future__ import annotations
import os
import json
import requests
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Union, Dict, Any

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None


def _load_hermes_env() -> None:
    if not load_dotenv:
        return
    if os.getenv("WP_APP_PASSWORD"):
        return
    candidates = [
        Path.home() / ".hermes" / ".env",
        Path(__file__).resolve().parent / ".env",
    ]
    for path in candidates:
        if path.exists():
            load_dotenv(path, override=False)
            if os.getenv("WP_APP_PASSWORD"):
                return


_load_hermes_env()


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


WP_URL = _env("WP_URL", _env("WP_BASE_URL", "https://moneybull.co.kr")).rstrip("/")
WP_USER = _env("WP_USER", "hogh0608")
WP_APP_PASSWORD = _env("WP_APP_PASSWORD", "")

DEFAULT_CATEGORY = _env("WP_DEFAULT_CATEGORY", "general")
DEFAULT_TAGS = [t.strip() for t in _env("WP_DEFAULT_TAGS", "").split(",") if t.strip()]


# ──────────────────────────────────────────────
# ENV BACKUP
# ──────────────────────────────────────────────

def backup_env_before_write() -> None:
    """어떤 스크립트도 .env를 덮어쓰기 전에 자동 백업"""
    env_file = Path.home() / ".hermes" / ".env"
    backup_dir = Path.home() / ".hermes" / ".backup"
    backup_dir.mkdir(exist_ok=True)
    if env_file.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = backup_dir / f".env.{timestamp}"
        shutil.copy2(env_file, backup)
        print(f"✅ .env 백업 완료: {backup}")


# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────

import base64


def _auth_headers() -> Dict[str, str]:
    token = base64.b64encode(f"{WP_USER}:{WP_APP_PASSWORD}".encode("utf-8")).decode("utf-8")
    return {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _api_path(endpoint: str) -> str:
    return f"{WP_URL}/wp-json/wp/v2/{endpoint}"


def _resolve_category(cat: Union[str, int, None]) -> Optional[int]:
    if cat is None:
        return 1
    if isinstance(cat, int):
        return cat
    r = requests.get(
        _api_path("categories"),
        params={"search": cat, "per_page": 50},
        auth=(WP_USER, WP_APP_PASSWORD),
        timeout=20,
    )
    if r.status_code != 200:
        return None
    for c in r.json():
        if c.get("name") == cat or c.get("slug") == cat:
            return c.get("id")
    return None


def _resolve_tag(tag: Union[str, int], tags_cache: Optional[Dict[str, int]] = None) -> Optional[int]:
    if isinstance(tag, int):
        return tag
    if tags_cache and tag in tags_cache:
        return tags_cache[tag]
    r = requests.get(
        _api_path("tags"),
        params={"search": tag, "per_page": 50},
        auth=(WP_USER, WP_APP_PASSWORD),
        timeout=20,
    )
    if r.status_code != 200:
        return None
    for t in r.json():
        if t.get("name") == tag:
            return t.get("id")
    return None


def _build_tags_cache() -> Dict[str, int]:
    r = requests.get(
        _api_path("tags"),
        params={"per_page": 200},
        auth=(WP_USER, WP_APP_PASSWORD),
        timeout=20,
    )
    if r.status_code != 200:
        return {}
    return {t.get("name", ""): t.get("id") for t in r.json() if t.get("name")}


def _blocks_to_html(blocks: List[Dict[str, Any]]) -> str:
    if not blocks:
        return ""
    return json.dumps(blocks, ensure_ascii=False)


# ──────────────────────────────────────────────
# CORE
# ──────────────────────────────────────────────

class WPPublisher:
    """WordPress REST API 연동 클래스. Draft 생성 → Min 승인 → Publish 흐름."""

    def __init__(self, url: Optional[str] = None, user: Optional[str] = None,
                 app_password: Optional[str] = None):
        self.url = url or WP_URL
        self.user = user or WP_USER
        self.password = app_password or WP_APP_PASSWORD
        self._tags_cache: Optional[Dict[str, int]] = None

    # ── 인증 확인 ──

    def health_check(self) -> Dict[str, Any]:
        result = {"api_ok": False, "auth_ok": False, "user": None, "error": None}

        r = requests.get(f"{self.url}/wp-json/wp/v2/posts?per_page=1", timeout=15)
        if r.status_code == 200:
            result["api_ok"] = True

        r = requests.get(f"{self.url}/wp-json/wp/v2/users/me", auth=(self.user, self.password), timeout=15)
        if r.status_code == 200:
            data = r.json()
            result["auth_ok"] = True
            result["user"] = data.get("name", data.get("slug", "unknown"))
        else:
            result["error"] = f"auth 실패: HTTP {r.status_code} — {r.text[:120]}"

        return result

    # ── 게시글 CRUD ──

    def create_draft(
        self,
        title: str,
        content: Optional[str] = None,
        category: Optional[Union[str, int]] = None,
        tags: Optional[List[Union[str, int]]] = None,
        status: str = "draft",
        excerpt: Optional[str] = None,
        featured_media: int = 0,
        content_blocks: Optional[List[Dict[str, Any]]] = None,
    ) -> int:
        cat_id = _resolve_category(category or DEFAULT_CATEGORY)
        if cat_id is None:
            cat_id = 1

        tag_ids: List[int] = []
        merged_tags = [*(tags or []), *DEFAULT_TAGS]
        if merged_tags:
            self._tags_cache = self._tags_cache or _build_tags_cache()
            for t in merged_tags:
                tid = _resolve_tag(t, self._tags_cache)
                if tid:
                    tag_ids.append(tid)

        raw_content = content or ""
        if content_blocks:
            raw_content = _blocks_to_html(content_blocks)

        payload = {
            "title": title,
            "content": raw_content,
            "status": status,
            "categories": [cat_id],
            "tags": tag_ids,
            "featured_media": featured_media,
        }
        if excerpt:
            payload["excerpt"] = excerpt

        r = requests.post(
            _api_path("posts"),
            json=payload,
            auth=(self.user, self.password),
            timeout=30,
        )

        if r.status_code == 201:
            post_id = r.json()["id"]
            print(f"✅ Draft 생성: ID {post_id} — {title}")
            return post_id
        else:
            raise RuntimeError(f"게시 실패 HTTP {r.status_code}: {r.text[:300]}")

    def get_post(self, post_id: int) -> Dict[str, Any]:
        r = requests.get(_api_path(f"posts/{post_id}"), auth=(self.user, self.password), timeout=15)
        if r.status_code == 200:
            return r.json()
        raise RuntimeError(f"조회 실패 HTTP {r.status_code}")

    def update_draft(self, post_id: int, title: Optional[str] = None,
                     content: Optional[str] = None, status: Optional[str] = None,
                     category: Optional[Union[str, int]] = None,
                     tags: Optional[List[Union[str, int]]] = None,
                     content_blocks: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        if title is not None:
            payload["title"] = title
        if content is not None or content_blocks is not None:
            payload["content"] = _blocks_to_html(content_blocks) if content_blocks else content
        if status is not None:
            payload["status"] = status
        if category is not None:
            cat_id = _resolve_category(category)
            if cat_id:
                payload["categories"] = [cat_id]
        if tags is not None:
            self._tags_cache = self._tags_cache or _build_tags_cache()
            tag_ids = [_resolve_tag(t, self._tags_cache) for t in tags]
            tag_ids = [t for t in tag_ids if t]
            if tag_ids:
                payload["tags"] = tag_ids

        r = requests.post(
            _api_path(f"posts/{post_id}"),
            json=payload,
            auth=(self.user, self.password),
            timeout=30,
        )

        if r.status_code == 200:
            data = r.json()
            print(f"✅ 수정 완료: ID {post_id} — {data.get('title', {}).get('rendered', '제목 없음')}")
            return data
        else:
            raise RuntimeError(f"수정 실패 HTTP {r.status_code}: {r.text[:300]}")

    def publish(self, post_id: int) -> Dict[str, Any]:
        return self.update_draft(post_id, status="publish")

    def delete(self, post_id: int) -> bool:
        r = requests.delete(_api_path(f"posts/{post_id}"), auth=(self.user, self.password), timeout=15)
        return r.status_code in (200, 204)

    def list_drafts(self, per_page: int = 20) -> List[Dict[str, Any]]:
        r = requests.get(
            _api_path("posts"),
            params={"status": "draft", "per_page": per_page, "orderby": "date", "order": "desc"},
            auth=(self.user, self.password),
            timeout=15,
        )
        return r.json() if r.status_code == 200 else []

    # ── 유틸리티 ──

    def list_categories(self) -> List[Dict[str, Any]]:
        r = requests.get(
            _api_path("categories"),
            params={"per_page": 100},
            auth=(self.user, self.password),
            timeout=15,
        )
        return r.json() if r.status_code == 200 else []

    def list_tags(self) -> List[Dict[str, Any]]:
        r = requests.get(
            _api_path("tags"),
            params={"per_page": 200},
            auth=(self.user, self.password),
            timeout=15,
        )
        return r.json() if r.status_code == 200 else []


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    wp = WPPublisher()

    if len(sys.argv) < 2:
        print("사용법:")
        print("  python wp_publisher.py health       — 상태 점검")
        print("  python wp_publisher.py draft        — 테스트 Draft 생성")
        print("  python wp_publisher.py drafts       — Draft 목록")
        print("  python wp_publisher.py categories   — 카테고리 목록")
        print("  python wp_publisher.py tags         — 태그 목록")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "health":
        result = wp.health_check()
        for k, v in result.items():
            print(f"  {k}: {v}")

    elif cmd == "draft":
        post_id = wp.create_draft(
            title="[wp-publisher] 자동 테스트",
            content="<p>wp-publisher Skill 동작 확인용 테스트 게시글입니다.</p>",
            category="general",
            tags=["재테크"],
        )
        print(f"\n생성된 Draft ID: {post_id}")

    elif cmd == "drafts":
        drafts = wp.list_drafts()
        if not drafts:
            print("Draft 없음")
        for d in drafts:
            print(f"  ID {d['id']}: {d['title']['rendered']} ({d['date']})")

    elif cmd == "categories":
        for c in wp.list_categories():
            print(f"  [{c['name']}] 슬러그: {c['slug']} (ID: {c['id']})")

    elif cmd == "tags":
        for t in wp.list_tags():
            print(f"  [{t['name']}] 슬러그: {t['slug']} (ID: {t['id']})")

    else:
        print(f"알 수 없는 명령: {cmd}")

