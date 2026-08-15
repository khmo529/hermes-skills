#!/usr/bin/env python3
"""
MoneyBull Telegram Bot 알림
Draft 생성 완료 → Telegram 승인 요청
"""

from __future__ import annotations

import os
import requests
from typing import Optional, Dict, Any
from pathlib import Path


def _load_env() -> None:
    from dotenv import load_dotenv
    candidates = [
        Path.home() / ".hermes" / ".env",
        Path(__file__).resolve().parent.parent / "wp_publisher" / ".env",
    ]
    for path in candidates:
        if path.exists():
            load_dotenv(path, override=False)
            if os.getenv("TELEGRAM_BOT_TOKEN"):
                return


_load_env()


class TelegramBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
        if not self.token or not self.chat_id:
            raise RuntimeError(
                "TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID가 설정되지 않았습니다.\n"
                "1. @BotFather에게 /newbot\n"
                "2. 토큰/CHAT_ID를 C:/Users/mark/.hermes/.env에 저장\n"
            )
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def send_draft_notification(
        self,
        post_id: int,
        title: str,
        keyword: str,
        edit_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Draft 생성 완료 승인 요청"""
        if edit_url is None:
            edit_url = f"https://moneybull.co.kr/wp-admin/post.php?post={post_id}&action=edit"

        text = (
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
        return self._send(text)

    def _send(self, text: str) -> Dict[str, Any]:
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML",
        }
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        return r.json()
