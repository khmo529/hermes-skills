# trend-scanner
금융/정부/재테크 글감 자동 발굴 스킬

## 사용법
```bash
cd C:/Users/mark/AppData/Local/hermes/skills/trend-scanner
python trend_scanner.py
```

## 출력
- `output/trends/daily_YYYY-MM-DD.json`

## 지원 소스
- Google Trends: pytrends 기반 실제 검색량
- Naver DataLab: 데모 데이터 / 실제 연동 필요
- gov24: 현재 RSS 메타데이터만 제공, 수집 0건
- moef: 현재 HTML 반환, 수집 0건
- fsc: 현재 404, 수집 0건

## 확장
- `sources/` 내 신규 파서 추가
- KEYWORD_CATEGORIES, FINANCE_KEYWORDS 조정
