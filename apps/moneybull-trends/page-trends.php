<?php
/**
 * Template Name: MoneyBull 실시간 금융 트렌드
 * Description: 토스급 프리미엄 실시간 검색어 페이지.
 * Version: 1.0.0
 */

if (!defined('ABSPATH')) {
    exit;
}

get_header();
?>

<style>
<?php
$css = file_get_contents(__DIR__ . '/trends.css');
echo '/* trends.css */' . "\n" . $css . "\n";
?>
</style>

<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>

<div class="trends-page" x-data="moneybullTrends()" x-init="init()">
  <div class="trends-container">
    <header class="trends-header">
      <h1 class="trends-title">지금 가장 많이 보는 금융 키워드</h1>
      <span class="live-pill" aria-live="polite">
        <span class="live-dot" aria-hidden="true"></span>
        LIVE
      </span>
    </header>

    <nav class="filters" aria-label="카테고리 필터">
      <template x-for="cat in categories" :key="cat">
        <button class="chip" :class="{ active: activeCategory === cat }" @click="activeCategory = cat" type="button">
          <span x-text="cat"></span>
        </button>
      </template>
    </nav>

    <section class="card-list" aria-label="트렌드 리스트">
      <!-- Loading skeleton -->
      <template x-if="loading" key="skeleton">
        <div>
          <div class="card shimmer" aria-hidden="true">
            <div class="skeleton w60 h12"></div>
            <div class="skeleton w40 h12"></div>
          </div>
          <div class="card shimmer" aria-hidden="true">
            <div class="skeleton w60 h12"></div>
            <div class="skeleton w40 h12"></div>
          </div>
          <div class="card shimmer" aria-hidden="true">
            <div class="skeleton w60 h12"></div>
            <div class="skeleton w40 h12"></div>
          </div>
        </div>
      </template>

      <!-- Empty state -->
      <template x-if="!loading && (!trends || !trends.length)">
        <p style="color:#6b6b6b;">잠시 후 다시 확인해 주세요.</p>
      </template>

      <!-- Trend cards -->
      <template x-for="item in filtered, index" :key="item.keyword + item.rank + index">
        <a class="card" :href="item.url" :style="`animation-delay: ${index * 40}ms`">
          <div class="card-rank" aria-label="순위" x-text="item.rank"></div>
          <div class="card-body">
            <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap;">
              <p class="card-title" x-text="item.keyword"></p>
              <span class="badge" :class="item.label" x-text="badgeLabel(item)"></span>
            </div>
            <div class="card-meta">
              <span x-text="item.updated_at ? new Date(item.updated_at).toLocaleTimeString('ko-KR') : ''"></span>
              <span aria-hidden="true">·</span>
              <span x-text="`관련글 ${(item.related_posts || []).length}개`"></span>
            </div>
            <div class="card-related" aria-label="관련글">
              <template x-for="post in item.related_posts || []" :key="post.url">
                <span class="related-link" x-text="post.title" tabindex="0"></span>
              </template>
            </div>
          </div>
          <div style="text-align:right;">
            <div class="change" style="color: var(--fire);" x-show="item.meta && item.meta.fire" x-text="'🔥 +20% 이상'"></div>
            <div class="change" style="color: var(--text-secondary);" x-show="!(item.meta && item.meta.fire)" x-text="item.change_pct > 0 ? `▲ ${item.change_pct.toFixed(1)}%` : (item.change_pct < 0 ? `▼ ${Math.abs(item.change_pct).toFixed(1)}%` : '-')"></div>
          </div>
        </a>
      </template>
    </section>

    <div style="margin-top: 16px; display:flex; align-items:center; justify-content:space-between; color:#6b6b6b; font-size:12px;">
      <span x-text="`마지막 업데이트: ${lastUpdated ? new Date(lastUpdated).toLocaleTimeString('ko-KR') : '-'}`"></span>
      <span>폴링 주기 10초</span>
    </div>
  </div>

  <nav class="tab-bar" aria-label="카테고리 탭">
    <button class="tab" :class="{active: activeCategory === '전체'}" @click="activeCategory = '전체'" type="button">전체</button>
    <button class="tab" :class="{active: activeCategory === 'ISA'}" @click="activeCategory = 'ISA'" type="button">ISA</button>
    <button class="tab" :class="{active: activeCategory === '예금·적금'}" @click="activeCategory = '예금·적금'" type="button">예금·적금</button>
    <button class="tab" :class="{active: activeCategory === '금리·금값'}" @click="activeCategory = '금리·금값'" type="button">금리·금값</button>
    <button class="tab" :class="{active: activeCategory === '달러·주식'}" @click="activeCategory = '달러·주식'" type="button">달러·주식</button>
  </nav>
</div>

<script>
(function () {
  const JSON_URL = '/wp-json/moneybull/v1/trends';

  function moneybullTrends() {
    return {
      trends: [],
      loading: true,
      lastUpdated: null,
      activeCategory: '전체',
      categories: ['전체', 'ISA', '예금·적금', '금리·금값', '달러·주식'],
      intervalId: null,

      init() {
        this.fetchTrends();
        this.intervalId = setInterval(() => this.fetchTrends(), 10000);
      },

      async fetchTrends() {
        this.loading = true;
        try {
          const res = await fetch(JSON_URL, { headers: { 'Accept': 'application/json' } });
          if (!res.ok) throw new Error(res.status);
          const data = await res.json();
          if (Array.isArray(data.trends)) {
            this.trends = data.trends;
            this.lastUpdated = data.updated_at;
          }
        } catch (e) {
          console.error('[MoneyBull Trends] fetch error:', e);
        } finally {
          this.loading = false;
        }
      },

      badgeLabel(item) {
        if (!item || !item.label) return '';
        if (item.meta && item.meta.fire && item.label === 'up') return '🔥 급상승';
        return item.label === 'new' ? 'NEW' : (item.label === 'up' ? '상승' : (item.label === 'down' ? '하락' : '유지'));
      },

      get filtered() {
        const cat = this.activeCategory;
        if (!Array.isArray(this.trends)) return [];
        if (cat === '전체') return this.trends;
        return this.trends.filter((item) => {
          const k = String(item.keyword || '');
          if (cat === 'ISA') return k.includes('ISA') || k.includes('계좌');
          if (cat === '예금·적금') return k.includes('예금') || k.includes('적금');
          if (cat === '금리·금값') return k.includes('금리') || k.includes('금값') || k.includes('금 ') || k === '금';
          if (cat === '달러·주식') return k.includes('달러') || k.includes('주식') || k.includes('코인') || k.includes('비트코인') || k.includes('환율');
          return true;
        });
      }
    };
  }

  window.moneybullTrends = moneybullTrends;
})();
</script>

<?php
get_footer();
