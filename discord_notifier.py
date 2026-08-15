#!/usr/bin/env python3
"""
MoneyBull Discord 승인 워크플로우 알림
"""

from __future__ import annotations

from typing import Optional


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
        msg = (
            f"📬 [MoneyBull] Draft {post_id} 생성\n"
            f"제목: {title}\n"
            f"키워드: {keyword}\n"
            f"링크: {edit_url}\n\n"
            "Discord에서 '승인' 입력 시 Publish"
        )
        print(msg)
        return msg
