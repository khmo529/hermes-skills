<?php
/* Template Name: MoneyBull 실시간 금융 트렌드 */
get_header();
$json_path = '/home/hogh0608/htdocs/moneybull.co.kr/wp-content/uploads/moneybull/trends.json';
if(!file_exists($json_path)) $json_path = '/var/www/moneybull/wp-content/uploads/moneybull/trends.json';
$trends = json_decode(@file_get_contents($json_path), true);
if(!$trends || count($trends)<5){
 $trends = [
  ["rank"=>1,"keyword"=>"ISA 계좌","change"=>"+2.3%","badge"=>"🔥 급상승","cat"=>"ISA","source"=>"KRX","url"=>"/covered-call-etf-guide/"],
  ["rank"=>2,"keyword"=>"예금 금리","change"=>"+0.8%","badge"=>"NEW","cat"=>"예금·적금","source"=>"KRX","url"=>"/korean-bank-recommendations-how-to-split-deposits-for-100-million-deposit-insurance-era/"],
  ["rank"=>3,"keyword"=>"금값","change"=>"+1.2%","badge"=>"LIVE","cat"=>"금리·금값","source"=>"KRX","url"=>"/gold-price-decline-outlook/"],
 ];
}
?>
<style>
.trends-wrap{max-width:1100px;margin:0 auto;padding:40px 20px 140px}
.trends-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:24px}
.trend-card{background:#fff;border:1px solid #eef0f3;border-radius:20px;padding:20px;cursor:pointer}
.trend-top{display:flex;justify-content:space-between}
.trend-rank{width:28px;height:28px;border-radius:50%;background:#0f172a;color:#fff;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700}
.trend-badge{font-size:11px;padding:4px 8px;border-radius:20px;background:#fef2f2;color:#dc2626;font-weight:700}
.trend-kw{font-size:17px;font-weight:800;color:#0f172a;margin:12px 0 6px}
.trend-change{font-size:13px;font-weight:600}.trend-change.up{color:#16a34a}.trend-change.down{color:#dc2626}
.trend-src{font-size:10px;color:#94a3b8;margin-top:6px}
.filter-bar{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin:24px 0}
.filter-bar button{padding:10px 18px;border-radius:999px;border:1px solid #e5e7eb;background:#fff!important;color:#0f172a!important;font-weight:700!important;font-size:13px!important}
.filter-bar button.active{background:#0f172a!important;color:#fff!important}
@media(max-width:768px){.trends-grid{grid-template-columns:1fr}}
</style>
<div class="trends-wrap">
<h1 style="text-align:center;font-size:32px;font-weight:800">지금 가장 많이 보는 금융 키워드 <span style="font-size:12px;background:#fee2e2;color:#dc2626;padding:6px 12px;border-radius:20px">● LIVE</span></h1>
<p style="text-align:center;color:#64748b;font-size:13px;margin-top:8px">마지막 업데이트: <?php echo date('H:i:s');?> · 소스: <?php echo $trends[0]['source']??'KRX+Reddit';?></p>
<div class="filter-bar"><button class="active" data-filter="전체">전체</button><button data-filter="ISA">ISA</button><button data-filter="예금·적금">예금·적금</button><button data-filter="금리·금값">금리·금값</button><button data-filter="달러·주식">달러·주식</button></div>
<div class="trends-grid" id="trendsGrid">
<?php foreach($trends as $t):
 $isDown = strpos($t['change'],'-')!==false;
 $url = $t['url']??('/covered-call-etf-guide/');
?>
<div class="trend-card" data-cat="<?php echo $t['cat']??'전체';?>" onclick="location.href='<?php echo $url;?>'">
<div class="trend-top"><div class="trend-rank"><?php echo $t['rank'];?></div><?php if(!empty($t['badge'])):?><div class="trend-badge"><?php echo $t['badge'];?></div><?php endif;?></div>
<div class="trend-kw"><?php echo $t['keyword'];?></div>
<div class="trend-change <?php echo $isDown?'down':'up';?>"><?php echo $t['change'];?></div>
<div class="trend-src"><?php echo $t['source']??'KRX';?><?php if(isset($t['translated'])) echo ' · 번역';?></div>
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
c.style.display=(f==='전체'||c.dataset.cat===f)?'block':'none';
  });
 });
});
</script>
<?php get_footer();?>
