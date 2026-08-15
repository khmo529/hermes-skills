#!/usr/bin/env python3
"""
Hermes .env 중앙 저장소 초기화
기존 .env는 절대 덮어쓰지 않습니다.
"""
from pathlib import Path

EXAMPLE_CONTENT = """# Hermes Secret 중앙 저장소
# 이 파일은 Git에 포함되지 않습니다
# 아래 값을 실제 값으로 교체하세요

WP_USER=hogh0608
WP_APP_PASSWORD=your_application_password
WP_BASE_URL=https://moneybull.co.kr

# Telegram Bot (선택)
# TELEGRAM_BOT_TOKEN=your_telegram_bot_token
# TELEGRAM_CHAT_ID=your_telegram_chat_id

# AI API Keys (선택)
# ANTHROPIC_API_KEY=sk-ant-...
# OPENAI_API_KEY=sk-...
"""


def init() -> None:
    hermes_dir = Path.home() / ".hermes"
    hermes_dir.mkdir(exist_ok=True)

    env_file = hermes_dir / ".env"
    example_file = hermes_dir / ".env.example"
    gitignore_file = hermes_dir / ".gitignore"
    backup_dir = hermes_dir / ".backup"

    example_file.write_text(EXAMPLE_CONTENT, encoding="utf-8")
    print(f"생성/갱신됨: {example_file}")

    if env_file.exists():
        print(f"⚠️  {env_file} 이미 존재합니다. 덮어쓰지 않습니다.")
        print("   → 필요하면 수동으로 수정하세요.")
    else:
        env_file.write_text(EXAMPLE_CONTENT, encoding="utf-8")
        print(f"✅ {env_file} 생성 완료")
        print("   → 실제 비밀번호로 교체하세요")

    gitignore_file.write_text(".env\n.backup\n", encoding="utf-8")
    backup_dir.mkdir(exist_ok=True)
    print(f"\n중앙 저장소: {hermes_dir}")
    print(f"백업 디렉토리: {backup_dir}")


if __name__ == "__main__":
    init()
