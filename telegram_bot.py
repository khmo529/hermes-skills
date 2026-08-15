#!/usr/bin/env python3
"""
MoneyBull Telegram 알림
현재 Mr.Krabs Telegram 세션을 사용해 알림 메시지를 출력합니다.
별도 봇 토큰 없이 Hermes 메시징 경로로 전달합니다.
"""

from __future__ import annotations

from typing import Optional


class TelegramBot:
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
            f"📬 [MoneyBull] Draft {post_id} 생성 완료 (99점 버전)\n"
            f"제목: {title}\n"
            f"키워드: {keyword}\n"
            f"링크: {edit_url}\n\n"
            "이 메시지 아래에 '승인' 입력 시 Publish"
        )
        print(msg)
        return msg
