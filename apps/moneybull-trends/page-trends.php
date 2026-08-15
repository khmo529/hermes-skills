<?php
/* Template Name: MoneyBull 인기검색어 */
get_header();
$json_path='/home/hogh0608/htdocs/moneybull.co.kr/wp-content/uploads/moneybull/trends.json';
if(!file_exists($json_path)) $json_path='/var/www/moneybull/wp-content/uploads/moneybull/trends.json';
$raw=json_decode(@file_get_contents($json_path), true);
if(!$raw || !isset($raw['trends']) || count($raw['trends'])<5){
 $trends=[
  ["rank"=>1,"keyword"=>"챗GPT","change"=>"+3%","badge"=>"NEW","cat"=>"IT·트렌드","source"=>"base","url"=>"/?s=챗GPT"],
  ["rank"=>2,"keyword"=>"아이폰 16","change"=>"+3%","badge"=>"NEW","cat"=>"IT·트렌드","source"=>"base","url"=>"/?s=아이폰 16"],
  ["rank"=>3,"keyword"=>"비트코인","change"=>"+2%","badge"=>"","cat"=>"경제·금융","source"=>"base","url"=>"/?s=비트코인"],
 ];
} else {
 $trends=$raw['trends'];
}
?>
<style>
.trends-wrap{max-width:1100px;margin:0 auto;padding:40px 20px 140px}
.filter-bar{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin:24px 0}
.filter-bar button{padding:10px 18px;border-radius:999px;border:1px solid #e5e7eb;background:#fff!important;color:#0f172a!important;font-weight:700!important;font-size:13px!important;cursor:pointer}
.filter-bar button.active{background:#0f172a!important;color:#fff!important}
.trends-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.trend-card{background:#fff;border:1px solid #eef0f3;border-radius:20px;padding:20px;cursor:pointer}
.trend-kw{font-size:17px;font-weight:800;color:#0f172a!important;margin:12px 0 6px}
.trend-change{font-size:13px;font-weight:700;color:#16a34a}
.trend-src{font-size:10px;color:#94a3b8;margin-top:6px}
@media(max-width:768px){.trends-grid{grid-template-columns:1fr}}
</style>
<div class="trends-wrap">
<h1 style="text-align:center;font-size:32px;font-weight:800">지금 가장 많이 보는 키워드 <span style="font-size:12px;background:#fee2e2;color:#dc2626;padding:6px 12px;border-radius:20px">● LIVE</span></h1>
<p style="text-align:center;color:#64748b;font-size:13px;margin-top:8px">마지막 업데이트: <?php echo date('H:i:s');?> · 블로그 글 키워드로 쓰세요 · <?php echo count($trends);?>개</p>
<div class="filter-bar">
<button class="active" data-filter="전체">전체</button>
<button data-filter="경제·금융">경제·금융</button>
<button data-filter="밈·이슈">밈·이슈</button>
<button data-filter="IT·트렌드">IT·트렌드</button>
<button data-filter="생활·연예">생활·연예</button>
</div>
<div class="trends-grid" id="trendsGrid">
<?php foreach($trends as $t):
 $cat=$t['cat']??'전체';
 if(preg_match('/챗GPT|아이폰|유튜브|넷플릭스|AI/i',$t['keyword'])) $cat='IT·트렌드';
 if(preg_match('/날씨|로또|올림픽|연예/i',$t['keyword'])) $cat='생활·연예';
?>
<div class="trend-card" data-cat="<?php echo $cat;?>" data-allcat="<?php echo $t['cat']??'';?> <?php echo $cat;?>" onclick="location.href='<?php echo $t['url'];?>'">
<div style="display:flex;justify-content:space-between"><div style="width:28px;height:28px;border-radius:50%;background:#0f172a;color:#fff;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700"><?php echo $t['rank'];?></div><?php if(!empty($t['badge'])):?><div style="font-size:11px;padding:4px 8px;border-radius:20px;background:#fef2f2;color:#dc2626;font-weight:700"><?php echo $t['badge'];?></div><?php endif;?></div>
<div class="trend-kw"><?php echo $t['keyword'];?></div>
<div class="trend-change"><?php echo $t['change'];?></div>
<div class="trend-src"><?php echo $t['source'];?> · 클릭하면 관련 글</div>
<div style="margin-top:8px;display:flex;gap:6px">
<button onclick="event.stopPropagation();navigator.clipboard.writeText('<?php echo $t['keyword'];?>');this.innerText='복사됨!';setTimeout(()=>this.innerText='📋 복사',1000)" style="font-size:11px;padding:4px 10px;border-radius:20px;border:1px solid #e5e7eb;background:#fff;cursor:pointer">📋 복사</button>
<button onclick="event.stopPropagation();location.href='<?php echo $t['url'];?>'" style="font-size:11px;padding:4px 10px;border-radius:20px;border:0;background:#0f172a;color:#fff;cursor:pointer">글쓰기</button>
</div>
</div>
<?php endforeach;?>
</div>
</div>
<script>
document.querySelectorAll('.filter-bar button').forEach(btn=>{
 btn.addEventListener('click',()=>{
document.querySelectorAll('.filter-bar button').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  const f=btn.dataset.filter;
  document.querySelectorAll('.trend-card').forEach(c=>{
    const cats=(c.getAttribute('data-allcat')||'')+' '+(c.getAttribute('data-cat')||'');
    if(f==='전체' || cats.includes(f) || c.getAttribute('data-cat')===f){
      c.style.display='block';
    } else {
      c.style.display='none';
    }
  });
 });
});
</script>
<?php get_footer();?>
