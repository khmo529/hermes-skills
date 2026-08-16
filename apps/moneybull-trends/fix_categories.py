import subprocess, json

BASE="/home/hogh0608/htdocs/moneybull.co.kr"

def wp(cmd):
    full=f"wp {cmd} --path={BASE} --allow-root"
    r=subprocess.run(full, shell=True, capture_output=True, text=True, timeout=15)
    return r.stdout.strip()

# 1. 삭제: 빈 카테고리
cats=wp('term list category --format=json --fields=term_id,name,slug,count')
j=json.loads(cats)
for c in j:
    if int(c['count'])==0:
        print(f"delete empty: {c['name']} ({c['term_id']})")
        wp(f"term delete category {c['term_id']}")

# 2. 매핑: 중복/유사 카테고리 합치기
mapping={
    "🇰🇷 국내주식":"📈 주식",
    "🇺🇸 미국주식":"📈 주식",
    "₿ 비트코인":"🪙 코인",
    "🌍 경제":"📰 뉴스",
    "🏢 기업분석":"📈 주식",
    "💡 절세":"💰 배당주",
    "💱 환율":"📈 주식",
    "💵 재테크":"📚 투자 가이드",
    "📖 초보자 가이드":"📚 투자 가이드",
    "🛠️ 투자 방법":"📚 투자 가이드",
    "📰 코인뉴스":"🪙 코인",
    "2":"📈 주식",
    "23":"📰 뉴스",
    "24":"🔥 이슈",
    "26":"📈 주식",
    "8":"📈 주식",
    "9":"📈 주식"
}
for old,new in mapping.items():
    old_id=wp(f'term list category --search="{old}" --format=ids')
    new_id=wp(f'term list category --search="{new}" --format=ids')
    if old_id and new_id and old_id!=new_id:
        posts=wp(f'post list --category={old_id} --format=ids')
        if posts:
            for pid in posts.split():
                wp(f'post term remove {pid} category {old_id}')
                wp(f'post term add {pid} category {new_id}')
            print(f"move: {old}({old_id}) -> {new}({new_id}) {len(posts.split())} posts")
        wp(f'term delete category {old_id}')

print("\n=== final categories ===")
cats2=wp('term list category --format=json --fields=name,count')
print(cats2)
