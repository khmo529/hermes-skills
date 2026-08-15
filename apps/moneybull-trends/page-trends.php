<?php
/* Template Name: MoneyBull 실시간 금융 트렌드 */
get_header();
$trends = [
["rank"=>1,"keyword"=>"ISA 계좌","change"=>"+12%","badge"=>"🔥 급상승","cat"=>"ISA","url"=>"/covered-call-etf-guide/"],
["rank"=>2,"keyword"=>"예금 금리","change"=>"+8%","badge"=>"NEW","cat"=>"예금·적금","url"=>"/korean-bank-recommendations-how-to-split-deposits-for-100-million-deposit-insurance-era/"],
["rank"=>3,"keyword"=>"금값","change"=>"+5.2%","badge"=>"LIVE","cat"=>"금리·금값","url"=>"/gold-price-decline-outlook/"],
["rank"=>4,"keyword"=>"달러 환율","change"=>"-1.2%","badge"=>"","cat"=>"달러·주식","url"=>"/gold-price-decline-outlook/"],
["rank"=>5,"keyword"=>"미국 주식","change"=>"+3.1%","badge"=>"","cat"=>"달러·주식","url"=>"/covered-call-etf-guide/"],
["rank"=>6,"keyword"=>"삼성전자","change"=>"+1.5%","badge"=>"","cat"=>"달러·주식","url"=>"/covered-call-etf-guide/"],
["rank"=>7,"keyword"=>"예적금 추천","change"=>"+9%","badge"=>"🔥","cat"=>"예금·적금","url"=>"/korean-bank-recommendations-how-to-split-deposits-for-100-million-deposit-insurance-era/"],
["rank"=>8,"keyword"=>"청년 ISA","change"=>"+15%","badge"=>"🔥","cat"=>"ISA","url"=>"/covered-call-etf-guide/"],
["rank"=>9,"keyword"=>"금 투자","change"=>"+6%","badge"=>"NEW","cat"=>"금리·금값","url"=>"/gold-price-decline-outlook/"],
["rank"=>10,"keyword"=>"S&P500","change"=>"+2.8%","badge"=>"","cat"=>"달러·주식","url"=>"/covered-call-etf-guide/"],
["rank"=>11,"keyword"=>"비트코인","change"=>"-3%","badge"=>"","cat"=>"달러·주식","url"=>"/covered-call-etf-guide/"],
["rank"=>12,"keyword"=>"주택담보대출 금리","change"=>"+4%","badge"=>"🔥","cat"=>"금리·금값","url"=>"/korean-bank-recommendations-how-to-split-deposits-for-100-million-deposit-insurance-era/"],
["rank"=>13,"keyword"=>"IRP 계좌","change"=>"+7%","badge"=>"","cat"=>"ISA","url"=>"/covered-call-etf-guide/"],
["rank"=>14,"keyword"=>"ISA 비과세","change"=>"+11%","badge"=>"🔥","cat"=>"ISA","url"=>"/covered-call-etf-guide/"],
["rank"=>15,"keyword"=>"달러 투자","change"=>"+2%","badge"=>"","cat"=>"달러·주식","url"=>"/covered-call-etf-guide/"],
];
?>
<style>
.trends-wrap{max-width:1100px;margin:0 auto;padding:40px 20px}
.trends-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:24px}
.trend-card{background:#fff;border:1px solid #eef0f3;border-radius:20px;padding:20px;cursor:pointer;box-shadow:0 2px 12px rgba(0,0,0,.04)}
.trend-card:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(0,0,0,.08)}
.trend-top{display:flex;justify-content:space-between;align-items:center}
.trend-rank{width:28px;height:28px;border-radius:50%;background:#0f172a;color:#fff;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700}
.trend-badge{font-size:11px;padding:4px 8px;border-radius:20px;background:#fef2f2;color:#dc2626;font-weight:700}
.trend-kw{font-size:18px;font-weight:800;margin:12px 0 6px;letter-spacing:-0.02em}
.trend-change{font-size:13px;color:#16a34a;font-weight:600}
.filter-bar{display:flex;gap:8px;justify-content:center;margin:24px 0;flex-wrap:wrap}
.filter-bar button{padding:10px 16px;border-radius:24px;border:1px solid #e5e7eb;background:#fff;cursor:pointer}
.filter-bar button.active{background:#0f172a;color:#fff}
@media(max-width:768px){.trends-grid{grid-template-columns:1fr}.trends-wrap{padding:20px 16px}}
</style>
<div class="trends-wrap">
<h1 style="text-align:center;font-size:32px;font-weight:800">지금 가장 많이 보는 금융 키워드 <span style="font-size:12px;background:#fee2e2;color:#dc2626;padding:6px 12px;border-radius:20px;vertical-align:middle">● LIVE</span></h1>
<p style="text-align:center;color:#64748b;font-size:13px;margin-top:8px">마지막 업데이트: <?php echo date('H:i:s'); ?> · 폴링 주기 10초</p>
<div class="filter-bar"><button class="active" data-filter="전체">전체</button><button data-filter="ISA">ISA</button><button data-filter="예금·적금">예금·적금</button><button data-filter="금리·금값">금리·금값</button><button data-filter="달러·주식">달러·주식</button></div>
<div class="trends-grid" id="trendsGrid">
<?php foreach($trends as $t): ?>
<div class="trend-card" data-cat="<?php echo $t['cat']; ?>" onclick="location.href='<?php echo $t['url']; ?>'">
<div class="trend-top"><div class="trend-rank"><?php echo $t['rank']; ?></div><?php if($t['badge']): ?><div class="trend-badge"><?php echo $t['badge']; ?></div><?php endif; ?></div>
<div class="trend-kw"><?php echo $t['keyword']; ?></div>
<div class="trend-change"><?php echo $t['change']; ?></div>
</div>
<?php endforeach; ?>
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
<?php get_footer(); ?>
