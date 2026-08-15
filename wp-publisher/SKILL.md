# wp-publisher
WP REST API + Application Password 기반 MoneyBull 게시 스킬

## 사용 전 설정
```bash
cp .env.example .env
# .env에 WP_APP_PASSWORD 넣기
```

## 사용법
```python
from wp_publisher import WPPublisher

wp = WPPublisher()
post_id = wp.create_draft(
    title="2026 청년도약계좌 금리 비교",
    content="<p>본문...</p>",
    category="korea-policy",
    tags=["2026청년정책", "재테크"],
    status="draft",
)
print(post_id)
```

## 주의
- publish는 수동 승인 후 사용
- Gutenberg 블록은 `content_blocks`로 전달
