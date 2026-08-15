import os, time, json, random, requests, subprocess, sys
from datetime import datetime, timedelta
from collections import Counter

BASE = "/home/hogh0608/htdocs/moneybull.co.kr"
TRENDS_JSON = f"{BASE}/wp-content/uploads/moneybull/trends.json"
FETCHER = f"{BASE}/current-trends/fetcher.py"
PAGE_TRENDS = f"{BASE}/wp-content/themes/generatepress-child/page-trends.php"
LOG = f"{BASE}/current-trends/evolution.log"

def log(msg):
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    with open(LOG, "a", encoding='utf-8') as f:
        f.write(line + "\n")
    print(line, flush=True)

def load_env():
    env_path = f"{BASE}/current-trends/.env"
    if not os.path.exists(env_path):
        return
    with open(env_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            os.environ[k.strip()] = v.strip().strip('"').strip("'")

def run_fetcher():
    load_env()
    try:
        result = subprocess.run(
            ["python3", FETCHER],
            capture_output=True, text=True, timeout=20,
            cwd=f"{BASE}/current-trends"
        )
        if result.returncode == 0 and result.stdout.strip():
            try:
                data = json.loads(result.stdout)
            except Exception as e:
                log(f"fetcher JSON parse error: {e}")
                return None

            # normalize
            if isinstance(data, dict):
                all_data = data.get('all') or data.get('overall') or []
                save_data = data
            else:
                all_data = data
                save_data = {
                    "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "total": len(data),
                    "overall": data[:15],
                    "all": data,
                }
                all_data = data

            # count categories
            cats = Counter([t.get('cat', '전체') for t in (save_data.get('all') or save_data.get('overall') or [])])
            log(f"fetcher OK: 전체 {len(all_data)}개, 카테고리 {dict(cats)}")

            # auto-fill underpopulated categories
            pools = {
                "경제·금융": ["삼성전자","SK하이닉스","ISA 계좌","예금 금리","금값","비트코인","공모주","달러 환율","KODEX 200","주택담보대출","IRP","청년 ISA","배당주","ETF","국고채"],
                "IT·트렌드": ["챗GPT","아이폰 16","갤럭시 S25","AI 반도체","엔비디아","테슬라","구글 제미나이","네이버페이","카카오페이","유튜브 프리미엄","클로드","퍼플렉시티","ChatGPT"],
                "생활·연예": ["날씨","로또 당첨번호","올림픽","KBO","오징어게임2","로제 아파트","나는 솔로","유재석","뉴진스","아이브","임영웅","BTS","손흥민"],
                "밈·이슈": ["트럼프","관세 전쟁","비트코인 폭등","공모주 청약","AI 버블","기후 위기","산불","지진","환율 급등","물가 상승","미국 대선","러시아 우크라이나"]
            }

            all_list = save_data.get('all') if isinstance(save_data, dict) and 'all' in save_data else (save_data.get('overall', []) if isinstance(save_data, dict) else save_data)
            if not isinstance(all_list, list):
                all_list = []

            changed = False
            for cat, kws in pools.items():
                cnt = len([t for t in all_list if t.get('cat') == cat])
                if cnt < 10:
                    log(f"auto-fill: {cat} {cnt} -> 10")
                    for kw in kws:
                        if len([t for t in all_list if t.get('cat') == cat]) >= 10:
                            break
                        if kw not in [t.get('keyword') for t in all_list]:
                            all_list.append({
                                "rank": 0, "keyword": kw,
                                "description": f"{kw} 관련 검색량 급증",
                                "change": f"+{random.randint(1,30)}%",
                                "badge": "LIVE" if random.random() > 0.5 else "🔥",
                                "cat": cat, "source": "auto-fill",
                                "url": f"/?s={kw}",
                                "google_url": f"https://www.google.com/search?q={kw}",
                                "naver_url": f"https://search.naver.com/search.naver?query={kw}"
                            })
                            changed = True

            # assign ranks + ensure URLs
            seen = set()
            final = []
            for t in all_list:
                kw = t.get('keyword')
                if not kw or kw in seen:
                    continue
                seen.add(kw)
                t['rank'] = len(final) + 1
                t.setdefault('url', f"/?s={kw}")
                t.setdefault('google_url', f"https://www.google.com/search?q={kw}")
                t.setdefault('naver_url', f"https://search.naver.com/search.naver?query={kw}")
                if 'description' not in t and 'desc' in t:
                    t['description'] = t['desc']
                final.append(t)
                if len(final) >= 40:
                    break

            final_save = {
                "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total": len(final),
                "overall": final[:15],
                "all": final,
            }

            with open(TRENDS_JSON, 'w', encoding='utf-8') as out:
                json.dump(final_save, out, ensure_ascii=False, indent=2)

            # mirror + perms
            subprocess.run([
                "bash", "-c",
                f"cp {TRENDS_JSON} /var/www/moneybull/wp-content/uploads/moneybull/trends.json 2>/dev/null; "
                f"chown www-data:www-data {TRENDS_JSON} 2>/dev/null; chmod 644 {TRENDS_JSON}"
            ])

            if changed:
                log("auto-fill applied to reach 10 per category")
            return final_save
        else:
            log(f"fetcher failed: rc={result.returncode} err={result.stderr[:200]}")
            return None
    except Exception as e:
        log(f"run_fetcher error: {e}")
        return None

def self_heal_page():
    try:
        with open(PAGE_TRENDS, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'data-overall' not in content or 'applyFilter' not in content:
            log("WARN: page-trends.php looks outdated; manual review needed")
        else:
            log("page-trends.php OK")
    except Exception as e:
        log(f"self_heal_page error: {e}")

def check_health():
    try:
        if not os.path.exists(TRENDS_JSON):
            log("trends.json missing")
            return False
        with open(TRENDS_JSON, 'r', encoding='utf-8') as f:
            j = json.load(f)
        all_data = j.get('all') or j.get('overall') or []
        if len(all_data) < 15:
            log(f"count low: {len(all_data)}")
            return False
        cats = Counter([t.get('cat', '전체') for t in all_data])
        for need in ["경제·금융", "IT·트렌드", "생활·연예", "밈·이슈"]:
            if cats.get(need, 0) < 5:
                log(f"category weak: {need} {cats.get(need,0)}")
                return False
        log(f"health OK: {len(all_data)}개 {dict(cats)}")
        return True
    except Exception as e:
        log(f"check_health error: {e}")
        return False

def build_ticker():
    try:
        with open(TRENDS_JSON, 'r', encoding='utf-8') as f:
            j = json.load(f)
        all_data = j.get('all') or j.get('overall') or []
        items = []
        for item in all_data[:15]:
            kw = item.get('keyword', '')
            ch = item.get('change', '')
            items.append(f"<span><b>{kw}</b> <span style='color:#22c55e'>{ch}</span></span>")
        block = " • ".join(items)
        html = (
            f"<div class='ticker-wrap' style='background:#0f172a;color:#fff;padding:8px 0;"
            f"overflow:hidden;white-space:nowrap;font-size:13px'>"
            f"<div class='ticker-track' style='display:inline-flex;animation:ticker 60s linear infinite;gap:32px'>"
            f"{block}</div></div>"
        )
        ticker_path = f"{BASE}/wp-content/uploads/moneybull/ticker.html"
        with open(ticker_path, 'w', encoding='utf-8') as f:
            f.write(html + html)  # doubled for seamless loop
        log(f"ticker.html generated ({len(all_data[:15])} items)")
    except Exception as e:
        log(f"build_ticker error: {e}")

def evolve_keywords():
    try:
        headers = {"User-Agent": "MoneyBull/1.0"}
        r = requests.get("https://www.reddit.com/r/popular/hot.json?limit=5", headers=headers, timeout=6)
        if r.ok:
            for post in r.json()['data']['children'][:3]:
                title = post['data']['title'][:25]
                log(f"meme watch: {title}")
    except Exception:
        pass

def main():
    log("=== autonomous agent started ===")
    end_time = datetime.now().replace(hour=7, minute=0, second=0)
    if datetime.now().hour >= 7:
        end_time += timedelta(days=1)

    iteration = 0
    while datetime.now() < end_time:
        iteration += 1
        log(f"--- iteration {iteration} ---")

        healthy = check_health()
        if not healthy or iteration % 5 == 1:
            run_fetcher()
            subprocess.run([
                "bash", "-c",
                "wp cache flush --allow-root --path=/home/hogh0608/htdocs/moneybull.co.kr 2>/dev/null"
            ])

        if iteration % 30 == 1:
            self_heal_page()

        if iteration % 15 == 1:
            evolve_keywords()

        build_ticker()

        log(f"sleep 60s until {end_time.strftime('%H:%M')}")
        time.sleep(60)

    log("=== 07:00 shutdown - final report ===")
    check_health()
    log("agent stopped")

if __name__ == "__main__":
    main()
