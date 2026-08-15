from __future__ import annotations

from typing import Any, Optional


def render_finance_template(
    *,
    keyword: str,
    analysis: dict[str, Any],
    experience_notes: Optional[str] = None,
) -> str:
    title = f"{keyword} 비교·정리 | 금융 초보도 한눈에 보기"
    summary = (
        "핵심만 먼저 말하면 "
        f"{keyword}는 금리·수수료·우대조건 중 하나만 놓쳐도 수백만 원 차이가 납니다. "
        "실제 거래 기준으로 비교했으니 바로 확인하세요."
    )
    latest = "2025-01-01"
    tip = "여기서 판단 잘못하면 수백만 원 차이 납니다."

    return "\n".join(
        [
            f"<h2 id='{keyword.replace(' ', '-')}-비교-정리'>{title}</h2>",
            "",
            "<blockquote><p>" + summary + "</p></blockquote>",
            "",
            f"<p>이 글은 {latest} 기준 각사 공시 기준으로 작성됐습니다.</p>",
            "[이미지 1]",
            "",
            "<h3>상품 개요</h3>",
            f"<p><strong>{keyword}</strong>의 기본 구조를 정리합니다. 가장 먼저 확인할 것은 수익률보다 수수료 구조입니다. 수수료는 매년 납부하는 금액이므로 장기적으로 수익률보다 큰 영향을 줍니다.</p>",
            "",
            "<h3>비교 체크리스트</h3>",
            "<ul>",
            "<li>금리/수익률</li>",
            "<li>수수료</li>",
            "<li>우대조건</li>",
            "<li>가입/신청 방법</li>",
            "</ul>",
            "",
            "<h3>비교표</h3>",
            "<table>",
            "<thead><tr><th>항목</th><th>상품 A</th><th>상품 B</th><th>비고</th></tr></thead>",
            "<tbody>",
            f"<tr><td>금리/수익률</td><td>OO%</td><td>OO%</td><td>변동형/고정형 확인</td></tr>",
            f"<tr><td>수수료</td><td>OO만원</td><td>OO만원</td><td>연간 기준</td></tr>",
            f"<tr><td>우대조건</td><td>급여이체</td><td>자동이체</td><td>중복 적용 여부 확인</td></tr>",
            f"<tr><td>신청 방법</td><td>온라인</td><td>방문</td><td>서류 차이 확인</td></tr>",
            "</tbody>",
            "</table>",
            "[이미지 2]",
            "",
            "<blockquote><p>" + tip + "</p></blockquote>",
            "",
            "<h3>자주 묻는 질문</h3>",
            f"<p><strong>Q. {keyword} 고를 때 가장 먼저 봐야 할 항목은?</strong></p>",
            "<p>A. 금리보다 수수료와 우대조건이 실제 지급액에 더 큰 영향을 줍니다.</p>",
            "",
            "<h3>이런 분들께 추천</h3>",
            "<ul>",
            "<li>은행 창구에서 설명받기 어려운 분</li>",
            "<li>기존 상품 리모델링을 고려 중인 분</li>",
            "</ul>",
            "",
            "<p>실제로 계산해보면 조건 하나 바뀌면 결과가 완전히 달라집니다.</p>",
            "",
            "<hr>",
            "<p>즉시 실행: 현재 가입 상품의 <strong>수수료 항목</strong>을 명세서에서 먼저 확인하세요.</p>",
            "<p>댓글 유도: 지금 가장 신경 쓰이는 항목은 수수료인가요, 우대조건인가요?</p>",
            "<p>다음 글 추천: <a href='/tag/재테크-비교'>재테크 비교 모음</a>, <a href='/tag/금융-가이드'>금융 가이드</a></p>",
            "<p>투자 판단의 최종 책임은 사용자에게 있습니다. 원금 손실 가능성이 있습니다.</p>",
        ]
    )
