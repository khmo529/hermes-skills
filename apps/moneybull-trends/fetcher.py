import os, requests, random, json, re
from datetime import datetime

def load_env(path):
    if not os.path.exists(path): return
    with open(path,'r') as f:
        for line in f:
            line=line.strip()
            if not line or line.startswith('#') or '=' not in line: continue
            k,v=line.split('=',1)
            os.environ[k.strip()]=v.strip().strip('"').strip("'")

load_env('/home/hogh0608/htdocs/moneybull.co.kr/current-trends/.env')
load_env('/var/www/moneybull/current-trends/.env')

def get_all_popular():
    trends=[]

    # A. Google Trends 한국 일간 인기 (키 없이)
    try:
        r=requests.get("https://trends.google.com/trends/api/dailytrends?hl=ko&geo=KR", headers={"User-Agent":"Mozilla/5.0"}, timeout=8)
        text=r.text.replace(")]}',","")
        j=json.loads(text)
        for day in j.get('default',{}).get('trendingSearchesDays',[])[:1]:
            for item in day.get('trendingSearches',[])[:8]:
                kw=item['title']['query']
                traffic=item.get('formattedTraffic','')
                change=f"+{random.uniform(5,30):.0f}%"
                if 'K' in traffic:
                    try:
                        num=int(traffic.replace('K+','').replace(',',''))
                        change=f"+{num}%"
                    except Exception as e: pass
                trends.append({"rank":0,"keyword":kw,"change":change,"badge":"🔥 인기","cat":"전체","source":"Google","url":f"/?s={kw}"})
    except Exception as e:
        print(f"Google error {e}", __import__("sys").stderr)

    # B. Reddit r/popular + r/all 핫
    try:
        headers={"User-Agent":"MoneyBull/1.0"}
        r=requests.get("https://www.reddit.com/r/popular/hot.json?limit=15", headers=headers, timeout=6)
        if r.ok:
            for post in r.json()['data']['children'][:5]:
                title=post['data']['title']
                kw=title[:15].strip()
                if len(kw)>2 and kw not in [t['keyword'] for t in trends]:
                    trends.append({"rank":0,"keyword":kw,"change":f"+{random.uniform(3,15):.1f}%","badge":"NEW","cat":"밈·이슈","source":"Reddit","url":f"/?s={kw}"})
    except Exception as e: pass

    # C. Naver Most Searched 대체 - Naver DataLab 쇼핑인사이트 + 금융 합쳐서 인기검색어 느낌
    try:
        r=requests.get("https://www.naver.com/srchrank?frm=main", headers={"User-Agent":"Mozilla/5.0"}, timeout=5)
        kws=re.findall(r'"keyword":"([^"]+)"', r.text)[:5]
        for kw in kws:
            if kw not in [t['keyword'] for t in trends]:
                trends.append({"rank":0,"keyword":kw,"change":f"+{random.uniform(5,20):.0f}%","badge":"급상승","cat":"전체","source":"Naver","url":f"/?s={kw}"})
    except Exception as e: pass

    # D. X.com 트렌드 대체 - Nitter
    try:
        r=requests.get("https://nitter.net/search?f=tweets&q=lang%3Ako", headers={"User-Agent":"Mozilla/5.0"}, timeout=5)
        tags=re.findall(r'#([가-힣\w]+)', r.text)[:5]
        for tag in tags:
            if tag not in [t['keyword'] for t in trends] and len(tag)>1:
                trends.append({"rank":0,"keyword":f"#{tag}","change":f"+{random.uniform(10,50):.0f}%","badge":"LIVE","cat":"밈·이슈","source":"X","url":f"/?s={tag}"})
    except Exception as e: pass

    # E. 기존 KRX 금융도 3개는 유지 (블로그 금융글 키워드로 쓸 수 있게)
    try:
        r=requests.get("https://polling.finance.naver.com/api/realtime?query=SERVICE_ITEM:000215,005930", timeout=5)
        if r.ok:
            for d in r.json()['result']['areas'][0]['datas'][:2]:
                nm=d.get('nm','금')
                nv=float(d.get('nv',0)); sv=float(d.get('sv',nv))
                ch=((nv-sv)/sv*100) if sv else 0
                trends.append({"rank":0,"keyword":nm,"change":f"{ch:+.2f}%","badge":"LIVE","cat":"경제·금융","source":"KRX","url":f"/?s={nm}"})
    except Exception as e: pass

    # 15개 채우기
    fallback=["챗GPT","아이폰 16","로또 당첨번호","날씨","비트코인","삼성전자","올림픽","유튜브","넷플릭스 신작","공모주","ISA 계좌","예금 금리","금값","달러 환율","KBO"]
    for kw in fallback:
        if len(trends)>=15: break
        if kw not in [t['keyword'] for t in trends]:
            cat="경제·금융" if kw in ["ISA 계좌","예금 금리","금값","달러 환율","비트코인","공모주","삼성전자"] else "전체"
            trends.append({"rank":0,"keyword":kw,"change":f"+{random.uniform(1,20):.0f}%","badge":"","cat":cat,"source":"base","url":f"/?s={kw}"})

    seen=set(); final=[]
    for t in trends:
        if t['keyword'] not in seen:
            final.append(t); seen.add(t['keyword'])
        if len(final)>=15: break
    for i,t in enumerate(final):
        t['rank']=i+1
    return final[:15]

if __name__ == "__main__":
    print(json.dumps({"source":"moneybull-realtime-trends","updated_at":datetime.now().isoformat(),"count":len(get_all_popular()),"trends":get_all_popular()}, ensure_ascii=False, indent=2))
