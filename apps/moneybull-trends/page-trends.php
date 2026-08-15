<?php
/* Template Name: MoneyBull 대고객 인기검색어 */
get_header();
$json_path='/home/hogh0608/htdocs/moneybull.co.kr/wp-content/uploads/moneybull/trends.json';
if(!file_exists($json_path)) $json_path='/var/www/moneybull/wp-content/uploads/moneybull/trends.json';
$raw=json_decode(@file_get_contents($json_path), true);
if(!$raw || !isset($raw['trends']) || count($raw['trends'])<5){
 $trends=[
  ["rank"=>1,"keyword"=>"삼성전자","description"=>"2분기 실적 기대감","change"=>"+2.43%","cat"=>"경제·금융","source"=>"KRX","url"=>"/?s=삼성전자"],
 ];
} else {
 $trends=$raw['trends'];
}
function tdesc($kw){
 $m=["삼성전자"=>"외국인 매수세 유입","DL우"=>"우선주 거래량 급증","비트코인"=>"9만 달러 돌파","ISA 계좌"=>"비과세 한도 상향 이슈","예금 금리"=>"5% 특판 출시","금값"=>"사상 최고치 경신","챗GPT"=>"GPT-5 루머","아이폰 16"=>"9월 출시 스펙 유출","날씨"=>"주말 폭우 예보","올림픽"=>"메달 소식","로또 당첨번호"=>"1087회 발표","오징어게임2"=>"시즌2 공개일 확정","로제 아파트"=>"빌보드 1위","트럼프"=>"관세 정책 발표"];
 return $m[$kw]??"$kw 관련 검색 급증";
}
?>
<style>
.trends-wrap{max-width:800px;margin:0 auto;padding:40px 20px 140px}
.trends-title{font-size:30px;font-weight:800;color:#0f172a;text-align:center}
.trends-sub{text-align:center;color:#64748b;font-size:13px;margin:8px 0 24px}
.filter-bar{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin:0 0 24px}
.filter-bar button{padding:9px 16px;border-radius:999px;border:1px solid #e5e7eb;background:#fff!important;color:#0f172a!important;font-weight:700!important;font-size:13px!important;cursor:pointer}
.filter-bar button.active{background:#0f172a!important;color:#fff!important}
.trends-list{display:flex;flex-direction:column;gap:10px}
.trend-row{display:flex;align-items:center;gap:14px;background:#fff;border:1px solid #eef0f3;border-radius:16px;padding:14px 18px;transition:.15s}
.trend-row:hover{border-color:#0f172a;transform:translateY(-1px)}
.trend-rank{width:28px;height:28px;border-radius:50%;background:#0f172a;color:#fff;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;flex-shrink:0}
.trend-kw{font-weight:800;color:#0f172a;min-width:110px;font-size:15px}
.trend-desc{flex:1;color:#475569;font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.trend-change{font-size:12px;font-weight:700;padding:4px 8px;border-radius:20px;background:#f0fdf4;color:#16a34a;flex-shrink:0}
.trend-change.down{background:#fef2f2;color:#dc2626}
.trend-actions{display:flex;gap:6px;flex-shrink:0}
.btn-search{font-size:11px;padding:6px 10px;border-radius:20px;border:1px solid #e5e7eb;background:#fff;cursor:pointer;text-decoration:none;color:#0f172a}
.btn-search:hover{background:#f8fafc}
@media(max-width:768px){.trend-desc{display:none}.trend-kw{min-width:80px}}
</style>
<div class="trends-wrap">
<h1 class="trends-title">지금 가장 많이 보는 키워드 <span style="font-size:11px;background:#fee2e2;color:#dc2626;padding:5px 10px;border-radius:20px">● LIVE</span></h1>
<p class="trends-sub">마지막 업데이트: <?php echo date('H:i:s');?> · <?php echo count($trends);?>개 · 대고객 인기검색어</p>
<div class="filter-bar">
<button class="active" data-filter="전체">전체</button>
<button data-filter="경제·금융">경제·금융</button>
<button data-filter="IT·트렌드">IT·트렌드</button>
<button data-filter="생활·연예">생활·연예</button>
<button data-filter="밈·이슈">밈·이슈</button>
</div>
<div class="trends-list" id="trendsList">
<?php foreach($trends as $t):
 $cat=$t['cat']??'전체'; $kw=$t['keyword']; $src=$t['source']??'';
 if(in_array($src,['base','Naver','Google','Reddit','X']) || empty($cat) || $cat==='전체'){
   if(in_array($kw,["삼성전자","DL우","비트코인","ISA 계좌","예금 금리","금값","공모주","달러 환율","SK하이닉스","KODEX 200","주택담보대출","IRP","청년 ISA"])) $cat="경제·금융";
   elseif(in_array($kw,["챗GPT","아이폰 16","갤럭시 S25","AI 반도체","엔비디아","테슬라","구글 제미나이","네이버페이","카카오페이","유튜브 프리미엄"])) $cat="IT·트렌드";
   elseif(in_array($kw,["날씨","로또 당첨번호","올림픽","KBO","오징어게임2","로제 아파트","나는 솔로","유재석","뉴진스","아이브"])) $cat="생활·연예";
   elseif(in_array($kw,["트럼프","환율 급등","공모주 청약","비트코인 폭등","삼성전자 급등","AI 버블","기후 위기"])) $cat="밈·이슈";
 }
 $desc=$t['description']??tdesc($kw);
 $isDown=strpos($t['change'],'-')!==false;
 $q=urlencode($kw);
?>
<div class="trend-row" data-cat="<?php echo $cat;?>" data-keyword="<?php echo $kw;?>" onclick="if(!event.target.closest('a') && !event.target.closest('button')) location.href='<?php echo $t['url']??'/?s='.$q;?>'">
<div class="trend-rank"><?php echo $t['rank'];?></div>
<div class="trend-kw"><?php echo $kw;?></div>
<div style="color:#cbd5e1">:</div>
<div class="trend-desc"><?php echo $desc;?></div>
<div class="trend-change <?php echo $isDown?'down':'';?>"><?php echo $t['change'];?></div>
<div class="trend-actions">
<a class="btn-search" href="https://search.google.com/search?q=<?php echo $q;?>" target="_blank" rel="noopener" onclick="event.stopPropagation();">Google</a>
<a class="btn-search" href="https://search.naver.com/search.naver?query=<?php echo $q;?>" target="_blank" rel="noopener" onclick="event.stopPropagation();">Naver</a>
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
  let cnt=0;
  document.querySelectorAll('.trend-row').forEach(r=>{
    const show = f==='전체' || r.dataset.cat===f || r.dataset.cat.includes(f);
    r.style.display=show?'flex':'none';
    if(show) cnt++;
  });
 });
});
</script>
<?php get_footer();?>
