#!/usr/bin/env python3
"""
MoneyBull content quality gate.
- wp: 주석 검출
- class/style 속성 검출
- 금지 문구 검출
- 필수 요소 존재 검증
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


BLOCKED_PATTERNS = [
    (r"<!--\s*wp:", "wp 블록 주석"),
    (r"\bclass\s*=", "class 속성"),
    (r"\bstyle\s*=", "style 속성"),
    (r"colspan", "colspan 속성"),
    (r"rowspan", "rowspan 속성"),
    (r"첫째,", "금지 문구: 첫째"),
    (r"둘째,", "금지 문구: 둘째"),
    (r"결론적으로", "금지 문구: 결론적으로"),
    (r"~인 것이죠", "금지 문구: ~인 것이죠"),
    (r"~셈입니다", "금지 문구: ~셈입니다"),
    (r"알아보겠습니다", "금지 문구: 알아보겠습니다"),
    (r"말씀드리겠습니다", "금지 문구: 말씀드리겠습니다"),
    (r"라고 할 수 있습니다", "금지 문구: ~라고 할 수 있습니다"),
    (r"생각해볼 필요가 있습니다", "금지 문구: 생각해볼 필요가 있습니다"),
    (r"대박", "금지 문구: 대박"),
    (r"무조건", "금지 문구: 무조건"),
    (r"필수", "금지 문구: 필수"),
    (r"100%", "금지 문구: 100%"),
]
REQUIRED_PATTERNS = [
    (r"<blockquote", "요약 박스(blockquote)"),
    (r"<table", "시뮬레이션/비교 테이블"),
    (r"<hr", "SEO 메타데이터 구분자(<hr>)"),
]


def check(path: str) -> int:
    text = Path(path).read_text(encoding="utf-8")
    failed = []
    lower = text.lower()
    for pat, name in BLOCKED_PATTERNS:
        if re.search(pat, lower):
            failed.append(f"BLOCKED: {name}")
    for pat, name in REQUIRED_PATTERNS:
        if not re.search(pat, lower):
            failed.append(f"MISSING required: {name}")
    if failed:
        print(f"FAIL: {path}")
        for f in failed:
            print(f"  - {f}")
        return 1
    print(f"PASS: {path}")
    return 0


def main() -> int:
    files = sys.argv[1:]
    if not files:
        print("usage: quality_check.py <file1> [file2 ...]")
        return 2
    return max((check(f) for f in files), default=0)


if __name__ == "__main__":
    raise SystemExit(main())
