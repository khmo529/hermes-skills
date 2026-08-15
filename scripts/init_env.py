#!/usr/bin/env python3
"""
Hermes .env 중앙 저장소 초기화
Min이 한 번만 실행하면 됨
"""
from pathlib import Path

def init() -> None:
    hermes_dir = Path.home() / ".hermes"
    hermes_dir.mkdir(exist_ok=True)

    env_file = hermes_dir / ".env"
    example_file = hermes_dir / ".env.example"
    gitignore_file = hermes_dir / ".gitignore"
    backup_dir = hermes_dir / ".backup"

    example_content = """# Hermes Secret 중앙 저장소
# 이 파일은 Git에 포함되지 않습니다
# 아래 값을 실제 값으로 교체하세요

WP_USER=hogh0608
WP_APP_PASSWORD=your_application_password
WP_BASE_URL=https://moneybull.co.kr

# AI API Keys (선택)
# ANTHROPIC_API_KEY=sk-ant-...
# OPENAI_API_KEY=sk-...
"""

    if not example_file.exists():
        example_file.write_text(example_content, encoding="utf-8")
        print(f"생성됨: {example_file}")

    if not env_file.exists():
        env_file.write_text(example_content, encoding="utf-8")
        print(f"생성됨: {env_file}")
        print("   -> 실제 비밀번호로 교체하세요")
    else:
        print(f"이미 존재: {env_file}")

    if not gitignore_file.exists():
        gitignore_file.write_text(".env\n.backup\n", encoding="utf-8")
        print(f"생성됨: {gitignore_file}")

    backup_dir.mkdir(exist_ok=True)
    print(f"\n중앙 저장소: {hermes_dir}")
    print("   이 위치는 Git 외부에 있어 영구 보존됩니다.")
    print(f"백업 디렉토리: {backup_dir}")


if __name__ == "__main__":
    init()
