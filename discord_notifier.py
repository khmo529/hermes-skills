#!/usr/bin/env python3
"""
MoneyBull Discord 승인 워크플로우 알림
Hermes Discord 봇을 통해 현재 채널에 Draft 알림 전달
"""

from __future__ import annotations

from typing import Optional, Dict, Any


class DiscordNotifier:
    def send_draft_notification(
        self,
        post_id: int,
        title: str,
        keyword: str,
        edit_url: Optional[str] = None,
    ) -> str:
        if edit_url is None:
            edit_url = f"https://moneybull.co.kr/wp-admin/post.php?post={post_id}&action=edit"

        return (
            "📬 [MoneyBull] 새로운 Draft 생성 완료\n\n"
            f"제목: {title}\n"
            f"키워드: {keyword}\n"
            f"Draft ID: {post_id}\n"
            f"링크: {edit_url}\n\n"
            "응답:\n"
            "✅ 승인 → Publish\n"
            "🔄 수정 → 재생성\n"
            "⏸️ 보류 → 내일 다시"
        )
