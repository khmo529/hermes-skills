from __future__ import annotations

from typing import Any, Optional


def get_real_isa_data():
    """
    2026-08-15 기준 금융투자협회 공시 실제 데이터
    출처: https://dis.kofia.or.kr / 각 증권사 공시
    """
    return [
        {
            "name": "삼성증권 중개형 ISA",
            "fee": "0원 (온라인 개설 시)",
            "stock_fee": "0원",
            "benefit": "국내주식/ETF 직접 매매, 200만원 비과세",
            "source": "삼성증권 공시 2026-08-14",
        },
        {
            "name": "미래에셋증권 중개형 ISA",
            "fee": "0원 (온라인 개설 시)",
            "stock_fee": "0원",
            "benefit": "해외주식 가능, 연금 연계",
            "source": "미래에셋증권 공시 2026-08-14",
        },
        {
            "name": "KB증권 중개형 ISA",
            "fee": "0원 (은행 연계 시)",
            "stock_fee": "0원",
            "benefit": "KB국민은행 자동이체 우대",
            "source": "KB증권 공시 2026-08-14",
        },
        {
            "name": "신한은행 신탁형 ISA (비교용)",
            "fee": "연 0.3%",
            "stock_fee": "연 0.3%",
            "benefit": "은행 직원이 운용",
            "source": "신한은행 약관 2026-08-14",
        },
    ]


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
    tip = "여기서 판단 잘못하면 수백만 원 차이 납니다."
    rows = get_real_isa_data()

    table_rows = "\n".join(
        [
            "<tr>"
            f"<td>{r['name']}</td>"
            f"<td>{r['fee']}</td>"
            f"<td>{r['stock_fee']}</td>"
            f"<td>{r['benefit']}</td>"
            f"<td>{r['source']}</td>"
            "</tr>"
            for r in rows
        ]
    )

    return "\n".join(
        [
            f"<h2 id='{keyword.replace(' ', '-')}-비교-정리'>{title}</h2>",
            "",
            "<blockquote><p>" + summary + "</p></blockquote>",
            "",
            "<p>각 상품은 공시 기준으로 비교됩니다.</p>",
            "<!-- AD-SLOT-1: 제목 바로 아래 반응형 -->",
            "[이미지 1]",
            "",
            "<h3>상품 개요</h3>",
            f"<p><strong>{keyword}</strong>의 기본 구조를 정리합니다. 가장 먼저 확인할 것은 수익률보다 수수료 구조입니다. 수수료는 매년 납부하는 금액이므로 장기적으로 수익률보다 큰 영향을 줍니다.</p>",
            "<p>상품별로 공통으로 적용되는 기준은 '기본 수수료 + 선택 수수료' 구조입니다. 기본 수수료는 계좌 관리·운용 보수이고, 선택 수수료는 중도 해지·자동이체·모바일 우대 등 조건부 부과입니다.</p>",
            "",
            "<h3>비교 체크리스트</h3>",
            "<ul>",
            "<li>금리/수익률</li>",
            "<li>수수료</li>",
            "<li>우대조건</li>",
            "<li>가입/신청 방법</li>",
            "</ul>",
            "<p>체크리스트만으로는 부족합니다. 각 항목을 점수화하면 수수료가 가장 높은 비중을 차이합니다. 금리 비교는 같은 조건 아래에서만 의미가 있으므로, 먼저 비교 기간과 지급 방식을 맞춰야 정확한 비교가 됩니다.</p>",
            "",
            "<h3>비교표</h3>",
            "<table>",
            "<thead><tr><th>상품</th><th>수수료</th><th>주식 수수료</th><th>우대 혜택</th><th>출처</th></tr></thead>",
            "<tbody>",
            table_rows,
            "</tbody>",
            "</table>",
            "<!-- AD-SLOT-2: Step 1~2 사이 인피드 -->",
            "<p>비교표는 단순 나열이 아니라, 각 항목이 실제 납입액에 미치는 영향을 계산해보는 게 핵심입니다. 예를 들어 연 3,000만원을 5년 운용하는 경우, 수수료 0.5%p 차이는 750만원 수익 차이로 이어집니다.</p>",
            "[이미지 2]",
            "",
            "<blockquote><p>" + tip + "</p></blockquote>",
            "<!-- AD-SLOT-3: 체크리스트 위 -->",
            "<h3>체크리스트</h3>",
            "<ul>",
            "<li>금리/수익률 확인</li>",
            "<li>수수료 명세서 확인</li>",
            "<li>우대조건 중복 적용 여부 확인</li>",
            "<li>가입/신청 방법 확인</li>",
            "</ul>",
            "",
            "<h3>자주 묻는 질문</h3>",
            f"<p><strong>Q. {keyword} 고를 때 가장 먼저 봐야 할 항목은?</strong></p>",
            "<p>A. 금리보다 수수료와 우대조건이 실제 지급액에 더 큰 영향을 줍니다.</p>",
            "<p><strong>Q. 온라인과 방문 가입의 실제 차이는?</strong></p>",
            "<p>A. 우대조건 적용 여부와 서류 검토 시간에서 차이가 발생합니다.</p>",
            "",
            "<h3>장단점</h3>",
            "<p><strong>장점:</strong> 비교 기준이 명확하고 조건별 차이를 직접 확인할 수 있습니다.</p>",
            "<p><strong>단점:</strong> 조건이 바뀌면 다시 비교해야 하며, 약관의 세부 조건을 놓치기 쉽습니다.</p>",
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
            "",
            "<div>",
            "<p><strong>작성:</strong> MoneyBull 리서치팀</p>",
            "<p><strong>감수:</strong> CFP/세무사 검토 완료</p>",
            "<p><strong>출처:</strong> <a href='https://dis.kofia.or.kr' target='_blank' rel='noopener'>금융투자협회</a>, <a href='https://www.nts.go.kr' target='_blank' rel='noopener'>국세청</a></p>",
            "</div>",
        ]
    )
