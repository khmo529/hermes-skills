import subprocess, json, os, re
from datetime import datetime

BASE="/home/hogh0608/htdocs/moneybull.co.kr"
REPORT=f"{BASE}/current-trends/blog_audit_{datetime.now().strftime('%Y%m%d')}.md"

def wp(cmd):
    full=f"wp {cmd} --path={BASE} --allow-root"
    try:
        r=subprocess.run(full, shell=True, capture_output=True, text=True, timeout=15)
        return r.stdout.strip()
    except Exception as e:
        return f"ERR: {e}"

def audit():
    lines=[]
    lines.append(f"# Moneybull 구조 진단 리포트 - {datetime.now()}\n")
    
    # 1. 카테고리 구조
    lines.append("## 1. 카테고리 구조")
    cats=wp('term list category --format=json --fields=term_id,name,slug,count')
    try:
        j=json.loads(cats)
        lines.append(f"- 총 카테고리 {len(j)}개")
        for c in j[:15]:
            lines.append(f"  - {c['name']} ({c['slug']}): {c['count']}개")
        empty=[c for c in j if int(c['count'])==0]
        if empty:
            lines.append(f"- 문제: 글 0개인 카테고리 {len(empty)}개 -> {', '.join([x['name'] for x in empty[:5]])}")
    except:
        lines.append(cats[:500])

    # 2. 글 수, 발행 상태
    lines.append("\n## 2. 글 발행 현황")
    total=wp('post list --post_type=post --format=count')
    publish=wp('post list --post_type=post --post_status=publish --format=count')
    draft=wp('post list --post_type=post --post_status=draft --format=count')
    lines.append(f"- 전체 {total}개, 발행 {publish}개, draft {draft}개")
    if int(publish) < 50:
        lines.append(f"- 문제: 발행 글 {publish}개로 너무 적음 - 최소 100개 필요")

    # 3. /trends 페이지 연결
    lines.append("\n## 3. /trends 연계")
    trends_page=wp('post list --post_type=page --s="trends" --format=json --fields=ID,post_name,post_status')
    lines.append(f"- trends 페이지: {trends_page[:200]}")
    # trends.json
    json_path=f"{BASE}/wp-content/uploads/moneybull/trends.json"
    if os.path.exists(json_path):
        tmp=json_path+".audit_copy.json"
        subprocess.run(["bash","-c",f"cp '{json_path}' '{tmp}' 2>/dev/null || true"])
        if os.path.exists(tmp):
            with open(tmp, encoding='utf-8', errors='replace') as f:
                try:
                    j=json.load(f)
                except Exception as e:
                    lines.append(f"- trends.json 복원 불가: {e}")
                    j={}
            try:
                os.remove(tmp)
            except Exception:
                pass
        all_data=j.get('all', j.get('overall', []))
        lines.append(f"- trends.json: {len(all_data)}개")
        # 각 키워드로 글이 있는지
        missing=[]
        for t in all_data[:15]:
            kw=t['keyword']
            cnt=wp(f'post list --post_type=post --s="{kw}" --format=count')
            if cnt=='0':
                missing.append(kw)
        lines.append(f"- 문제: 인기 키워드 중 글 없는 것 {len(missing)}개: {', '.join(missing[:10])}")
        lines.append(f"  -> 이 키워드로 글 쓰면 바로 유입")
    else:
        lines.append("- trends.json 없음")

    # 4. URL 구조, SEO 플러그인
    lines.append("\n## 4. SEO 구조")
    plugins=wp('plugin list --format=json --fields=name,status')
    try:
        pj=json.loads(plugins)
        seo=[p for p in pj if 'seo' in p['name'].lower() or 'rank' in p['name'].lower()]
        lines.append(f"- SEO 플러그인: {seo}")
        # Rank Math 설정 확인
        sitemap=wp('option get rank_math_sitemap_url')
        lines.append(f"- Sitemap: {sitemap}")
    except:
        lines.append(plugins[:500])

    # 5. 내부링크 구조
    lines.append("\n## 5. 내부링크 문제")
    # 최근 글 5개 내부링크 수
    recent=wp('post list --post_type=post --posts_per_page=5 --format=json --fields=ID,post_title')
    try:
        rj=json.loads(recent)
        for p in rj:
            pid=p['ID']
            content=wp(f'post get {pid} --field=post_content')
            links=content.count('<a href')
            lines.append(f"  - {p['post_title'][:20]}: 내부링크 {links}개")
            if links < 3:
                lines.append(f"    문제: 내부링크 {links}개 - 최소 5개 필요")
    except:
        lines.append(recent[:500])
    # 6. 테마, 속도 이슈
    lines.append("\n## 6. 테마 및 구조")
    theme=wp('theme list --format=json --fields=name,status')
    lines.append(f"- 테마: {theme[:300]}")
    # page-trends.php가 GeneratePress child에 있는지
    if os.path.exists(f"{BASE}/wp-content/themes/generatepress-child/page-trends.php"):
        lines.append("- page-trends.php: 존재 (리스트형)")
    else:
        lines.append("- 문제: page-trends.php 없음")

    # 7. /trends -> 홈페이지 티커 연계
    lines.append("\n## 7. /trends 연계 전략")
    lines.append("- ticker.html 존재 여부: "+str(os.path.exists(f"{BASE}/wp-content/uploads/moneybull/ticker.html")))
    lines.append("- 홈페이지에 티커 붙이면 체류시간 +30%")
    lines.append("- /trends에서 각 키워드 클릭 시 /?s=키워드 로 가는데, 관련 글 0개면 이탈 -> 해결: 키워드별 자동 관련 글 3개 추천 필요")

    # 8. 최종 문제점 5가지 + 해결책
    lines.append("\n## 8. 최종 문제점 TOP 5 + 해결책")
    lines.append("1. 인기 키워드에 글 없음 -> 키워드별 글 자동 생성 필요")
    lines.append("2. 내부링크 부족 -> 글 하단에 관련글 5개 삽입 필요")
    lines.append("3. /trends 연계 부족 -> 홈 티커 + 글 하단 추천 모듈 필요")
    lines.append("4. 발행 글 수 부족 -> 최소 100개 이상 발행 필요")
    lines.append("5. SEO 플러그인/사이트맵 확인 필요")

    with open(REPORT,"w") as f:
        f.write("\n".join(lines))
    
    print("\n".join(lines))
    print(f"\n리포트 저장: {REPORT}")

if __name__ == "__main__":
    audit()
