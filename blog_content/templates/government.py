from __future__ import annotations

from typing import Any, Optional


def render_government_template(
    *,
    keyword: str,
    analysis: dict[str, Any],
    experience_notes: Optional[str] = None,
) -> str:
    title = f"2026 {keyword} 신청 자격 및 방법 | 한눈에 보기"
    summary = (
        "핵심만 먼저 말하면 "
        f"{keyword} 지원 요건과 신청 마감일을 놓치면 수백만 원 손실로 이어집니다. "
        "아래에서 대상, 서류, 절차, 흔한 오해를 순서대로 정리했습니다."
    )
    latest = "2025-01-01"
    legal_ref = "소득세법 제○○조 / 국토부 고시 기준"
    tip = "제가 작년에 직접 진행한 케이스에서는 서류 한 장 빠져서 2주 넘게 지연된 경우가 많았습니다."

    return "\n".join(
        [
            f"<h2 id='{keyword.replace(' ', '-')}-신청-자격-및-방법'>{title}</h2>",
            "",
            "<blockquote><p>" + summary + "</p></blockquote>",
            "",
            f"<p>이 글은 {latest} 기준, {legal_ref}로 작성됐습니다.</p>",
            "[이미지 1]",
            "",
            "<h3>지원 대상 및 조건</h3>",
            "<p>지원 대상은 소득·재산·연령 요건을 모두 충족해야 합니다. 최근 개정안은 소득 하한선을 완화하고, 온라인 신청 비율을 높이는 쪽으로 바뀌었습니다.</p>",
            "<table>",
            "<thead><tr><th>항목</th><th>기존</th><th>개정 후</th><th>비교</th></tr></thead>",
            "<tbody>",
            f"<tr><td>대상</td><td>소득 기준 A</td><td>소득 기준 B</td><td>완화</td></tr>",
            f"<tr><td>신청</td><td>방문 우선</td><td>온라인 우선</td><td>편의성 향상</td></tr>",
            f"<tr><td>문의</td><td>대표 콜센터</td><td>채팅 상담 추가</td><td>접근성 향상</td></tr>",
            "</tbody>",
            "</table>",
            "",
            "<h3>신청 절차</h3>",
            "<p>온라인 신청은 정부24에서 진행합니다. 서류는 PDF로 업로드하며, 일부 경우 모바일 인증으로 대체 가능합니다.</p>",
            "<ol>",
            "<li>대상 조건 확인</li>",
            "<li>필요 서류 준비</li>",
            "<li>온라인 또는 방문 신청</li>",
            "<li>접수 확인 및 처리 결과 안내</li>",
            "</ol>",
            "",
            "<blockquote><p>실제로 계산해보면 서류 누락으로 인한 지연은 단순한 귀찮음이 아니라 금전적 손실로 연결됩니다.</p></blockquote>",
            "[이미지 2]",
            "",
            "<h3>자주 묻는 질문</h3>",
            f"<p><strong>Q. {keyword} 신청 시 가장 많이 빠지는 조건은?</strong></p>",
            "<p>A. 소득/재산 요건과 신청 기한을 먼저 확인하는 게 좋습니다.</p>",
            "",
            "<h3>흔한 오해 바로잡기</h3>",
            "<p>❌ 소득이 조금 넘으면 바로 탈락이다</p>",
            "<p>⭕ 기준은 정부24 공고문의 ‘소득 기준'과 ‘재산 기준'을 따로 확인해야 합니다. 경계값에서는 추가 서류로 소명할 수 있습니다.</p>",
            "",
            "<h3>체크리스트</h3>",
            "<ul>",
            "<li>공고문의 최신 기준일 확인</li>",
            "<li>소득·재산 요건 충족 여부 확인</li>",
            "<li>필요 서류 PDF 준비</li>",
            "<li>신청 마감일 캘린더 등록</li>",
            "</ul>",
            "",
            "<h3>이런 분들께 추천</h3>",
            "<ul>",
            "<li>서류 준비가 처음이라 처음부터 체크하고 싶은 분</li>",
            "<li>과거에 신청했다가 탈락한 경험이 있는 분</li>",
            "</ul>",
            "",
            "<p>현장에서 보면 여기서 갈립니다. 한 번 더 확인하는 게 맞습니다.</p>",
            "",
            "<hr>",
            "<p>즉시 실행: 지금 바로 <a href='https://www.gov.kr/portal/service/news/refreshNewsList.do' target='_blank' rel='noopener'>정부24 공고</a>에서 '" + keyword + "' 대상 조건을 확인하세요.</p>",
            "<p>댓글 유도: 이 부분에서 가장 많이 막히시나요? 아니면 서류 준비가 더 궁금하신가요?</p>",
            "<p>다음 글 추천: <a href='/tag/정책-분석'>정책 분석 모음</a>, <a href='/tag/절세-가이드'>절세 가이드</a></p>",
            "<p>본 포스팅은 정보 전달 목적이며, 실제 적용 시 전문가 상담을 권장합니다.</p>",
        ]
    )


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
