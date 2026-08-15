import os, requests, random, re, time, sys
from datetime import datetime, timedelta

def _load_dotenv(path: str):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())
    except Exception:
        pass

_load_dotenv('/home/hogh0608/htdocs/moneybull.co.kr/current-trends/.env')
_load_dotenv('/var/www/moneybull/current-trends/.env')

KST = datetime.now().astimezone().tzinfo
OUT_FILE = __import__('pathlib').Path('/home/hogh0608/htdocs/moneybull.co.kr/wp-content/uploads/moneybull/trends.json')

UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
]

def _session():
    s = requests.Session()
    s.headers.update({"User-Agent": random.choice(UA_POOL), "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.5"})
    return s

def _jitter(lo=0.4, hi=1.4):
    time.sleep(random.uniform(lo, hi))

def _translate_to_korean(text: str) -> str:
    mapping = {
        'nvda': '엔비디아', 'tsla': '테슬라', 'aapl': '애플', 'msft': '마이크로소프트',
        'gold': '금값', 'btc': '비트코인', 'eth': '이더리움', 'usd': '달러',
        'spy': 'S&P500', 'qqq': '나스닥100', 'fed': '연준', 'cpi': '물가상승률',
        'youtube': '유튜브', 'google': '구글', 'amazon': '아마존',
    }
    lower = text.lower()
    for k, v in mapping.items():
        if k in lower:
            return v
    return text

def fetch_ncp_datalab():
    cid = os.getenv('NAVER_CLOUD_CLIENT_ID') or os.getenv('NAVER_CLIENT_ID')
    csec = os.getenv('NAVER_CLOUD_CLIENT_SECRET') or os.getenv('NAVER_CLIENT_SECRET')
    if not cid or not csec:
        return []
    use_ncp = os.getenv('NAVER_API_HUB') == 'true'
    url = "https://naveropenapi.apigw.ntruss.com/datalab/v1/search" if use_ncp else "https://openapi.naver.com/v1/datalab/search"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": cid,
        "X-NCP-APIGW-API-KEY": csec,
        "Content-Type": "application/json"
    } if use_ncp else {
        "X-Naver-Client-Id": cid,
        "X-Naver-Client-Secret": csec,
        "Content-Type": "application/json"
    }
    start = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
    end = datetime.now().strftime('%Y-%m-%d')
    body = {
        "startDate": start, "endDate": end, "timeUnit": "date",
        "keywordGroups": [
            {"groupName":"ISA","keywords":["ISA 계좌","청년 ISA","IRP"]},
            {"groupName":"예금금리","keywords":["예금 금리","예적금 추천"]},
            {"groupName":"금","keywords":["금값","금 투자"]},
            {"groupName":"달러","keywords":["달러 환율","달러 투자"]},
            {"groupName":"미국주식","keywords":["미국 주식","S&P500","엔비디아","테슬라"]}
        ]
    }
    try:
        _jitter(0.5, 1.2)
        r = requests.post(url, headers=headers, json=body, timeout=10)
        if r.status_code != 200:
            print(f"NCP Datalab failed {r.status_code} {r.text[:200]}", file=sys.stderr)
            return []
        data = r.json()
        trends = []
        for g in data.get('results', []):
            ratios = g.get('data', [])
            if len(ratios) >= 2:
                change = ((ratios[-1]['ratio'] - ratios[0]['ratio']) / max(1, ratios[0]['ratio']) * 100)
                badge = "🔥 급상승" if change > 10 else ("NEW" if change > 5 else "LIVE")
                trends.append({"keyword": g['title'], "change": f"{change:+.1f}%", "badge": badge, "cat": "전체", "source": "NCP Datalab"})
        return trends
    except Exception as e:
        print(f"Datalab error {e}", file=sys.stderr)
        return []

def fetch_reddit_x():
    trends = []
    try:
        _jitter(0.3, 0.9)
        r = requests.get("https://www.reddit.com/r/wallstreetbets/hot.json?limit=15", headers={"User-Agent": "MoneyBull/1.0"}, timeout=8)
        if r.ok:
            for child in r.json().get('data', {}).get('children', [])[:10]:
                title = child.get('data', {}).get('title', '')
                if not title:
                    continue
                cleaned = re.sub(r'[^\w\s]', '', title)
                words = [w for w in cleaned.split() if len(w) > 3]
                if words:
                    kw = _translate_to_korean(max(words, key=len))
                    trends.append({"keyword": kw, "change": "+0%", "badge": "X", "cat": "달러·주식", "source": "Reddit"})
    except Exception as e:
        print(f"Reddit error {e}")
    return trends[:5]

def fetch_krx_rates():
    try:
        _jitter(0.3, 0.9)
        r = requests.get("https://polling.finance.naver.com/api/realtime?query=SERVICE_ITEM:000215", timeout=8)
        if r.status_code == 200:
            return {"gold": r.json()}
    except Exception as e:
        print(f"[KRX] gold error: {e}")
    try:
        _jitter(0.3, 0.9)
        r = requests.get("https://m.stock.naver.com/api/stocks/finance/marketIndex", timeout=8)
        if r.status_code == 200:
            return {"fx": r.json()}
    except Exception as e:
        print(f"[KRX] fx error: {e}")
    return {}

def _inject_related_posts(keywords, limit=3):
    return [{"title": f"{kw} 최신 동향", "url": f"/?s={requests.utils.quote(kw)}"} for kw in keywords[:limit]]

def collect():
    cached = None
    if OUT_FILE.exists():
        try:
            cached = __import__('json').loads(OUT_FILE.read_text(encoding='utf-8'))
        except Exception:
            cached = None
    if cached and cached.get('count', 0) > 0:
        return cached

    ncp = fetch_ncp_datalab()
    reddit = fetch_reddit_x()
    krx = fetch_krx_rates()

    candidates = []
    seen = set()

    def add_unique(trends_list):
        for item in trends_list:
            kw = str(item.get('keyword', '')).strip()
            if not kw or kw in seen:
                continue
            seen.add(kw)
            candidates.append(kw)

    for item in ncp + reddit:
        add_unique([item])

    ranked_kw = candidates[:20]
    finance_keywords = []
    FINANCE_TOKENS = [
        "ISA", "ISA계좌", "금", "금값", "달러", "환율", "예금", "적금", "주식", "코인",
        "비트코인", "이더리움", "금리", "적금 이자", "예금 이자", "달러 투자", "달러 환전",
        "금 투자", "KRX", "국고채", "채권", "펀드", "보험", "카드", "은행", "증권", "ETF",
        "배당주", "리츠", "REITs", "원유", "원자재", "금융", "투자", "저축", "연금",
        "부동산", "부동산 투자", "전세", "월세", "주담대", "디딤돌", "보금자리",
        "엔비디아", "테슬라", "애플", "나스닥", "S&P500",
    ]
    for kw in ranked_kw:
        for token in FINANCE_TOKENS:
            if token.lower() in kw.lower():
                finance_keywords.append(kw)
                break

    merged = []
    for i, kw in enumerate(finance_keywords[:15], start=1):
        change_pct = 25.0 if i <= 2 else (18.0 if i <= 5 else (-6.0 if i > 10 else 0.0))
        label = "up" if change_pct >= 20 else ("new" if i <= 3 else "stable")
        merged.append({
            "keyword": kw,
            "category": "금융",
            "rank": i,
            "score": 100 - i * 7,
            "change_pct": change_pct,
            "label": label,
            "meta": {"fire": True if change_pct >= 20 else {}},
            "related_posts": _inject_related_posts([kw]),
            "updated_at": datetime.now(KST).isoformat(),
        })

    if not merged:
        base = [
            ("ISA 계좌", 25.0, "up"), ("예금 금리", 18.0, "new"), ("금값", 15.0, "new"),
            ("달러 환율", -6.0, "stable"), ("미국 주식", 8.0, "stable"), ("삼성전자", 5.0, "stable"),
            ("예적금 추천", 22.0, "up"), ("청년 ISA", 28.0, "up"), ("금 투자", 12.0, "new"),
            ("S&P500", 9.0, "stable"), ("비트코인", -8.0, "stable"), ("주택담보대출 금리", 20.0, "up"),
            ("IRP 계좌", 14.0, "stable"), ("ISA 비과세", 24.0, "up"), ("달러 투자", 7.0, "stable"),
        ]
        for i, (kw, change_pct, label) in enumerate(base, start=1):
            merged.append({
                "keyword": kw, "category": "금융", "rank": i, "score": 100 - i * 7,
                "change_pct": change_pct, "label": label,
                "meta": {"fire": True if change_pct >= 20 else {}},
                "related_posts": _inject_related_posts([kw]),
                "updated_at": datetime.now(KST).isoformat(),
            })

    payload = {
        "source": "moneybull-realtime-trends",
        "updated_at": datetime.now(KST).isoformat(),
        "count": len(merged),
        "trends": merged,
        "market": krx,
    }
    try:
        OUT_FILE.write_text(__import__('json').dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    except Exception:
        pass
    return payload

def main():
    cid = os.getenv('NAVER_CLOUD_CLIENT_ID') or os.getenv('NAVER_CLIENT_ID')
    csec = os.getenv('NAVER_CLOUD_CLIENT_SECRET') or os.getenv('NAVER_CLIENT_SECRET')
    use_ncp = os.getenv('NAVER_API_HUB') == 'true'
    print(f"[ENV] NAVER_API_HUB={use_ncp} client_id={'set' if cid else 'missing'} secret={'set' if csec else 'missing'}", file=sys.stderr)
    print(__import__('json').dumps(collect(), ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
