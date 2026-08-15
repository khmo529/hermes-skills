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
                trends.append({"keyword": g['title'], "change": f"{change:+.1f}%", "badge": badge, "cat": "전체", "source": "NCP"})
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
                score = child.get('data', {}).get('score', 0)
                change = (score / 100.0)
                change = max(-15.0, min(15.0, change))
                cleaned = re.sub(r'[^\w\s]', '', title)
                words = [w for w in cleaned.split() if len(w) > 3]
                if words:
                    kw = _translate_to_korean(max(words, key=len))
                    trends.append({"keyword": kw, "change": f"{change:+.1f}%", "badge": "X", "cat": "달러·주식", "source": "Reddit"})
    except Exception as e:
        print(f"Reddit error {e}", file=sys.stderr)
    return trends[:5]

def fetch_krx_rates():
    out = []
    try:
        _jitter(0.3, 0.9)
        r = requests.get("https://polling.finance.naver.com/api/realtime?query=SERVICE_ITEM:000215,005930,000660,069500", timeout=8)
        if r.status_code == 200:
            data = r.json()
            for item in data.get('result', {}).get('areas', [{}])[0].get('datas', []):
                code = item.get('cd')
                name = item.get('nm', '')
                nv = item.get('nv')
                sv = item.get('sv')
                if not nv or not sv:
                    continue
                try:
                    change = ((float(nv) - float(sv)) / float(sv) * 100)
                except Exception:
                    continue
                label = "stable"
                if change >= 20:
                    label = "up"
                elif change <= -15:
                    label = "down"
                elif 5 < change < 20:
                    label = "new"
                cat = "금리·금값"
                if code in ('005930', '000660', '069500'):
                    cat = "달러·주식"
                out.append({
                    "keyword": name,
                    "change": f"{change:+.2f}%",
                    "badge": "KRX",
                    "cat": cat,
                    "source": "KRX",
                })
    except Exception as e:
        print(f"[KRX] error: {e}", file=sys.stderr)
    return out

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
            candidates.append(item)

    for item in ncp + reddit + krx:
        add_unique([item])

    ranked = candidates[:20]
    finance_keywords = []
    FINANCE_TOKENS = [
        "ISA", "ISA계좌", "금", "금값", "달러", "환율", "예금", "적금", "주식", "코인",
        "비트코인", "이더리움", "금리", "적금 이자", "예금 이자", "달러 투자", "달러 환전",
        "금 투자", "KRX", "국고채", "채권", "펀드", "보험", "카드", "은행", "증권", "ETF",
        "배당주", "리츠", "REITs", "원유", "원자재", "금융", "투자", "저축", "연금",
        "부동산", "부동산 투자", "전세", "월세", "주담대", "디딤돌", "보금자리",
        "엔비디아", "테슬라", "애플", "나스닥", "S&P500", "삼성전자", "SK하이닉스", "KODEX200",
    ]
    for item in ranked:
        kw = str(item.get('keyword', '')).strip()
        for token in FINANCE_TOKENS:
            if token.lower() in kw.lower():
                finance_keywords.append(item)
                break

    merged = []
    for i, item in enumerate(finance_keywords[:15], start=1):
        change_str = str(item.get('change', '0.00%'))
        change_pct = 0.0
        try:
            change_pct = float(change_str.replace('%', '').replace('+', ''))
        except Exception:
            change_pct = 0.0
        label = "stable"
        if change_pct >= 20:
            label = "up"
        elif change_pct <= -15:
            label = "down"
        elif 5 < change_pct < 20:
            label = "new"
        merged.append({
            "keyword": item.get('keyword'),
            "category": item.get('cat', '금융'),
            "rank": i,
            "score": 100 - i * 7,
            "change_pct": change_pct,
            "change": change_str,
            "label": label,
            "meta": {"fire": True if change_pct >= 20 else {}},
            "related_posts": _inject_related_posts([item.get('keyword', '')]),
            "updated_at": datetime.now(KST).isoformat(),
            "source": item.get('source', 'KRX'),
            "url": item.get('url', '/?s=' + requests.utils.quote(item.get('keyword', ''))),
        })

    if not merged:
        base = [
            ("ISA 계좌", 2.3, "up"), ("예금 금리", 0.8, "new"), ("금값", 1.2, "new"),
            ("달러 환율", -0.5, "stable"), ("미국 주식", 1.5, "stable"), ("삼성전자", 0.9, "stable"),
            ("예적금 추천", 1.8, "up"), ("청년 ISA", 2.8, "up"), ("금 투자", 1.1, "new"),
            ("S&P500", 1.3, "stable"), ("비트코인", -1.2, "stable"), ("주택담보대출 금리", 1.6, "up"),
            ("IRP 계좌", 1.0, "stable"), ("ISA 비과세", 2.1, "up"), ("달러 투자", 0.7, "stable"),
        ]
        for i, (kw, change_pct, label) in enumerate(base, start=1):
            merged.append({
                "keyword": kw, "category": "금융", "rank": i, "score": 100 - i * 7,
                "change_pct": change_pct, "change": f"{change_pct:+.2f}%", "label": label,
                "meta": {"fire": True if change_pct >= 20 else {}},
                "related_posts": _inject_related_posts([kw]),
                "updated_at": datetime.now(KST).isoformat(),
                "source": "KRX",
                "url": '/?s=' + requests.utils.quote(kw),
            })

    payload = {
        "source": "moneybull-realtime-trends",
        "updated_at": datetime.now(KST).isoformat(),
        "count": len(merged),
        "trends": merged,
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
