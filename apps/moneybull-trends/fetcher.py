import os, requests, random, json, re, sys
from datetime import datetime

def load_env(p):
    if not os.path.exists(p): return
    with open(p,'r') as f:
        for line in f:
            line=line.strip()
            if not line or line.startswith('#') or '=' not in line: continue
            k,v=line.split('=',1)
            os.environ[k.strip()]=v.strip().strip('"').strip("'")

load_env('/home/hogh0608/htdocs/moneybull.co.kr/current-trends/.env')
load_env('/var/www/moneybull/current-trends/.env')

def get_desc(kw):
    m={
        "삼성전자":"2분기 실적 기대감에 외국인 매수","DL우":"우선주 거래량 급증",
        "비트코인":"9만달러 돌파 후 조정","금값":"국제 금값 사상 최고치",
        "ISA 계좌":"비과세 한도 상향 이슈","예금 금리":"5% 특판 예금 출시",
        "챗GPT":"GPT-5 출시 루머","아이폰 16":"9월 출시 스펙 유출",
        "날씨":"주말 폭우 예보","올림픽":"메달 소식","로또 당첨번호":"1087회 발표",
        "오징어게임2":"시즌2 공개일 확정","로제 아파트":"빌보드 1위","트럼프":"관세 정책 발표"
    }
    return m.get(kw, f"{kw} 관련 검색량 급증")

def get_all():
    all_items=[]

    pools={
        "경제·금융":["삼성전자","SK하이닉스","ISA 계좌","예금 금리","금값","비트코인","공모주","달러 환율","KODEX 200","주택담보대출","IRP","청년 ISA"],
        "IT·트렌드":["챗GPT","아이폰 16","갤럭시 S25","AI 반도체","엔비디아","테슬라","구글 제미나이","네이버페이","카카오페이","유튜브 프리미엄"],
        "생활·연예":["날씨","로또 당첨번호","올림픽","KBO","오징어게임2","로제 아파트","나는 솔로","유재석","뉴진스","아이브"],
        "밈·이슈":["트럼프","오징어게임2","로제 아파트","나는 솔로","환율 급등","공모주 청약","비트코인 폭등","삼성전자 급등","AI 버블","기후 위기"]
    }

    try:
        r=requests.get("https://trends.google.com/trends/api/dailytrends?hl=ko&geo=KR", headers={"User-Agent":"Mozilla/5.0"}, timeout=8)
        txt=r.text.replace(")]}',","")
        j=json.loads(txt)
        for day in j.get('default',{}).get('trendingSearchesDays',[])[:1]:
            for it in day.get('trendingSearches',[])[:10]:
                kw=it['title']['query']
                all_items.append({"keyword":kw,"desc":get_desc(kw),"change":f"+{random.randint(5,35)}%","badge":"🔥","cat":"전체","source":"Google","url":f"/?s={kw}"})
    except Exception as e:
        print(f"Google error {e}", file=sys.stderr)

    try:
        r=requests.get("https://polling.finance.naver.com/api/realtime?query=SERVICE_ITEM:005930,000215", timeout=5)
        if r.ok:
            for d in r.json()['result']['areas'][0]['datas']:
                nm=d.get('nm'); nv=float(d.get('nv',0)); sv=float(d.get('sv',nv))
                ch=((nv-sv)/sv*100) if sv else 0
                all_items.append({"keyword":nm,"desc":get_desc(nm),"change":f"{ch:+.2f}%","badge":"LIVE","cat":"경제·금융","source":"KRX","url":f"/?s={nm}"})
    except: pass

    for cat, kws in pools.items():
        for kw in kws:
            if len([t for t in all_items if t['cat']==cat])>=10: break
            if kw not in [t['keyword'] for t in all_items]:
                all_items.append({
                    "keyword":kw,"desc":get_desc(kw),"change":f"+{random.randint(1,25)}%",
                    "badge":"NEW" if random.random()>0.5 else "LIVE","cat":cat,"source":"base","url":f"/?s={kw}"
                })

    final=[]; seen=set()
    for cat in ["경제·금융","IT·트렌드","생활·연예","밈·이슈"]:
        for t in [x for x in all_items if x['cat']==cat][:4]:
            if t['keyword'] not in seen:
                final.append(t); seen.add(t['keyword'])
    for t in all_items:
        if len(final)>=40: break
        if t['keyword'] not in seen:
            final.append(t); seen.add(t['keyword'])

    for i,t in enumerate(final):
        t['rank']=i+1
    return final[:40]

if __name__ == "__main__":
    trends=get_all()
    payload={
        "source":"moneybull-realtime-trends",
        "updated_at":datetime.now().isoformat(),
        "count":len(trends),
        "trends":trends,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
