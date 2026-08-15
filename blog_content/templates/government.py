from __future__ import annotations

from typing import Any, Optional


def render_government_template(
    *,
    keyword: str,
    analysis: dict[str, Any],
    experience_notes: Optional[str] = None,
) -> str:
    title = f"2026 {keyword} 신청 자격 및 방법 | 한눈에 보기"
    summary_bullets = [
        f"지원요건: {keyword} 기본 자격 요건 확인",
        "신청기한: 공식 사이트 공지 기준",
        "핵심포인트: 서류 준비 및 온라인/오프라인 신청 경로",
    ]
    if experience_notes:
        summary_bullets.append(f"실무팁: {experience_notes}")

    lines = [
        f"# {title}",
        "",
        "> 📌 3줄 요약",
    ]
    for b in summary_bullets:
        lines.append(f"> - {b}")
    lines += [
        "",
        "광고 상단",
        "",
        "## 1. 지원 대상 및 조건",
        "| 항목 | 내용 |",
        "| --- | --- |",
        f"| 대상 | {keyword} 지원 요건을 갖춘 개인/사업자 |",
        "| 신청 | 정부24 또는 관련 기관 포털 |",
        "| 문의 | 대표 콜센터/담당 부서 |",
        "",
        "## 2. 신청 절차",
        "1. 대상 조건 확인",
        "2. 필요 서류 준비",
        "3. 온라인 또는 방문 신청",
        "4. 접수 확인 및 처리 결과 안내",
        "",
        "광고 중간",
        "",
        "## 3. 자주 묻는 질문",
        f"**Q. {keyword} 신청 시 가장 많이 빠지는 조건은?**",
        "A. 소득/재산 요건과 신청 기한을 먼저 확인하는 게 좋습니다.",
        "",
        "## 4. 함께 보면 좋은 정보",
        "- 관련 지원금 비교 정리",
        "- 신청 서류 체크리스트",
        "",
        "광고 하단",
    ]
    return "\n".join(lines)
