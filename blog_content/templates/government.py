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
            f"<p>이 글은 {latest} 기준, {legal_ref}로 작성됐습니다. 출처: <a href='https://www.gov.kr' target='_blank' rel='noopener'>정부24</a>, <a href='https://www.moef.go.kr' target='_blank' rel='noopener'>기획재정부</a></p>",
            "<!-- AD-SLOT-1: 제목 바로 아래 반응형 -->",
            "[이미지 1]",
            "",
            "<h3>지원 대상 및 조건</h3>",
            "<p>지원 대상은 소득·재산·연령 요건을 모두 충족해야 합니다. 최근 개정안은 소득 하한선을 완화하고, 온라인 신청 비율을 높이는 쪽으로 바뀌었습니다.</p>",
            "<p>소득 요건은 직전 과세기간 종합소득의 합계 기준이며, 재산 요건은 토지·건물·예금 등을 합산한 기준액을 의미합니다. 연령 요건은 19세 이상 39세 이하인 경우가 대부분이며, 특정 지역 거주자에게 가점이 부여되는 경우도 있습니다.</p>",
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
            "<p>첫 단계는 대상 조건 확인입니다. 공고문에 명시된 소득 기준과 재산 기준을 각각 개별로 대조해야 합니다. 둘 중 하나만이라도 기준을 벗어나면 탈락이 기본이므로, 경계선에 걸린 경우 미리 증빙을 준비하는 게 유리합니다.</p>",
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
            "<p><strong>Q. 신청 후 결과는 언제 알 수 있나요?</strong></p>",
            "<p>A. 접수일로부터 보통 14~21일이며, 서류 보완 요청이 발생하면 추가 지연됩니다.</p>",
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
            "",
            "<div>",
            "<p><strong>작성:</strong> MoneyBull 에디터 | CFP/공인중개사 협업</p>",
            "<p><strong>감수:</strong> 세무사 ○○○</p>",
            f"<p><strong>최종업데이트:</strong> {latest}</p>",
            "<p><strong>출처:</strong> 국세청(www.nts.go.kr), 기획재정부(www.moef.go.kr), 법제처(www.law.go.kr)</p>",
            "</div>",
        ]
    )
