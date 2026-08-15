<?php
/* Template Name: MoneyBull 실시간 인기검색어 - 대고객 */
get_header();
$json_path='/home/hogh0608/htdocs/moneybull.co.kr/wp-content/uploads/moneybull/trends.json';
if(!file_exists($json_path)) $json_path='/var/www/moneybull/wp-content/uploads/moneybull/trends.json';
$raw=json_decode(@file_get_contents($json_path), true);
if(isset($raw['all'])) $trends=$raw['all'];
elseif(isset($raw['overall'])) $trends=$raw['overall'];
else $trends=$raw;
if(!$trends) $trends=[];
$updated=$raw['updated']??date('Y-m-d H:i:s');
?>
<style>
.trends-wrap{max-width:850px;margin:0 auto;padding:40px 20px 120px}
.trends-title{font-size:30px;font-weight:800;color:#0f172a;text-align:center}
.trends-sub{text-align:center;color:#64748b;font-size:13px;margin:8px 0 24px}
.filter-bar{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin:0 0 20px}
.filter-bar button{padding:9px 16px;border-radius:999px;border:1px solid #e5e7eb;background:#fff!important;color:#0f172a!important;font-weight:700!important;font-size:13px!important;cursor:pointer}
.filter-bar button.active{background:#0f172a!important;color:#fff!important}
.trends-list{display:flex;flex-direction:column;gap:10px}
.trend-row{display:flex;align-items:center;gap:12px;background:#fff;border:1px solid #eef0f3;border-radius:16px;padding:14px 18px;transition:.15s}
.trend-row:hover{border-color:#cbd5e1}
.trend-rank{width:26px;height:26px;border-radius:50%;background:#0f172a;color:#fff;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;flex-shrink:0}
.trend-kw{font-weight:800;color:#0f172a;min-width:110px;font-size:14px}
.trend-desc{flex:1;color:#475569;font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.trend-change{font-size:11px;font-weight:700;padding:4px 8px;border-radius:20px;background:#f0fdf4;color:#16a34a;flex-shrink:0}
.trend-change.down{background:#fef2f2;color:#dc2626}
.trend-actions{display:flex;gap:6px;flex-shrink:0}
.btn-g{font-size:11px;padding:6px 10px;border-radius:20px;border:1px solid #e5e7eb;background:#fff;color:#0f172a;cursor:pointer;text-decoration:none}
.btn-n{font-size:11px;padding:6px 10px;border-radius:20px;border:0;background:#03c75a;color:#fff;cursor:pointer;text-decoration:none}
@media(max-width:768px){.trend-desc{display:none}.trend-kw{min-width:70px}}
/* 티커용 */
.ticker-wrap{overflow:hidden;white-space:nowrap;background:#0f172a;color:#fff;padding:8px 0;font-size:13px}
.ticker-track{display:inline-flex;animation:ticker 60s linear infinite;gap:32px}
@keyframes ticker{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
.ticker-item{display:flex;align-items:center;gap:6px}
</style>
<div class="trends-wrap">
<h1 class="trends-title">지금 가장 많이 보는 키워드 <span style="font-size:11px;background:#fee2e2;color:#dc2626;padding:5px 10px;border-radius:20px;vertical-align:middle">● LIVE</span></h1>
<p class="trends-sub">마지막 업데이트: <?php echo $updated;?> · 실시간 인기검색어 · <?php echo count($trends);?>개</p>
<div class="filter-bar">
<button class="active" data-filter="전체" data-count="15">전체 15</button>
<button data-filter="경제·금융" data-count="10">경제·금융 10</button>
<button data-filter="IT·트렌드" data-count="10">IT·트렌드 10</button>
<button data-filter="생활·연예" data-count="10">생활·연예 10</button>
<button data-filter="밈·이슈" data-count="10">밈·이슈 10</button>
</div>
<div class="trends-list" id="trendsList">
<?php foreach($trends as $idx=>$t):
 $cat=$t['cat']??'전체';
 $kw=$t['keyword'];
 $desc=$t['description']??$t['desc']??'';
 $change=$t['change']??'';
 $rank=$t['rank']??$idx+1;
 $gurl=$t['google_url']??'https://www.google.com/search?q='.urlencode($kw);
 $nurl=$t['naver_url']??'https://search.naver.com/search.naver?query='.urlencode($kw);
 $isDown=strpos($change,'-')!==false;
?>
<div class="trend-row" data-cat="<?php echo $cat;?>" data-index="<?php echo $idx;?>" data-overall="<?php echo $idx<15?'1':'0';?>">
<div class="trend-rank"><?php echo $rank;?></div>
<div class="trend-kw"><?php echo $kw;?></div>
<div style="color:#e2e8f0">:</div>
<div class="trend-desc"><?php echo $desc;?></div>
<div class="trend-change <?php echo $isDown?'down':'';?>"><?php echo $change;?></div>
<div class="trend-actions">
<a class="btn-g" href="<?php echo $gurl;?>" target="_blank" rel="noopener">구글에서 검색</a>
<a class="btn-n" href="<?php echo $nurl;?>" target="_blank" rel="noopener">네이버에서 검색</a>
</div>
</div>
<?php endforeach;?>
</div>
</div>

<!-- 홈페이지 티커 재사용용 -->
<div id="moneybullTicker" class="ticker-wrap" style="display:none">
<div class="ticker-track" id="tickerTrack"></div>
</div>

<script>
function applyFilter(f){
 let shown=0;
 let limit = f==='전체'?15:10;
 document.querySelectorAll('.trend-row').forEach(row=>{
   const cat=row.dataset.cat;
   const overall=row.dataset.overall==='1';
   let match=false;
   if(f==='전체') match=overall;
   else match=(cat===f);
   if(match && shown<limit){
     row.style.display='flex';
     shown++;
   } else {
     row.style.display='none';
   }
 });
}
document.querySelectorAll('.filter-bar button').forEach(btn=>{
 btn.addEventListener('click',()=>{
  document.querySelectorAll('.filter-bar button').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  applyFilter(btn.dataset.filter);
 });
});
applyFilter('전체');

// 티커 생성 - 홈페이지에서 재사용
(function(){
 const rows=document.querySelectorAll('.trend-row');
 const track=document.getElementById('tickerTrack');
 if(!track) return;
 let html='';
 rows.forEach(r=>{
   const kw=r.querySelector('.trend-kw').innerText;
   const ch=r.querySelector('.trend-change').innerText;
   html+='<span class="ticker-item"><b>'+kw+'</b> <span style="color:#22c55e">'+ch+'</span></span> • ';
 });
 track.innerHTML=html+html;
 window.MONEYBULL_TICKER_HTML=document.getElementById('moneybullTicker').outerHTML;
})();

window.renderMoneybullTicker=function(targetId){
 const t=document.getElementById('moneybullTicker');
 const target=document.getElementById(targetId);
 if(t && target){
   target.innerHTML=t.innerHTML;
   target.style.display='block';
 }
}
</script>
<?php get_footer();?>
