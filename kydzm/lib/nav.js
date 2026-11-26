/* 관리 화면 공통 상단 메뉴 (사용자 261126 '메뉴 흐름 통일해서 어느 메뉴든 쉽게 이동, 모바일도 중요')
 * 모든 관리 화면(kydzm/*.html, 대시보드 index.html 제외)이 <script src="lib/nav.js"></script> 한 줄로 씀.
 * 메뉴 묶음은 대시보드 메뉴(index.html grp)와 같게 — 메뉴를 바꾸면 여기와 index.html 두 곳.
 * 대시보드 안 iframe(?embed=1)에서는 안 보임. 각 화면의 예전 '← 관리자 홈' 링크는 숨김(중복).
 */
(function () {
  if (window.top !== window || /[?&]embed=1/.test(location.search)) return;
  const MENU = [
    ['📌 업무 관리', [['board.html', '📋', '운영판'], ['board.html?tab=posts', '📅', '올린 글 달력'], ['board.html?tab=autos', '⏰', '자동화'], ['board.html?tab=conns', '🔌', '연결']]],
    ['🎬 콘텐츠 관리', [['./#series', '🎬', '시리즈 EP'], ['./#camps', '🏕', '캠핑장'], ['./#foods', '🍖', '음식'], ['./#items', '🛠', '장비']]],
    ['📱 SNS 관리', [['mutuals.html', '📸', '인스타'], ['threads.html', '🧵', '스레드']]],
    ['🔥 딜보드 관리', [['deals.html', '🔥', '딜 보드']]],
    ['📈 성과 분석', [['insights.html', '📈', '성과 분석'], ['./#coupang', '🛒', '쿠팡 실적'], ['./#stats', '📊', '홈페이지 통계']]],
    ['🗂 기타', [['pipeline.html', '🗺️', '운영 지도'], ['camp-live.html', '🏕️', '캠핑사이트'], ['conti.html', '🎞', '콘티 보드']]],
  ];
  const file = (location.pathname.split('/').pop() || 'index.html');
  const tab = new URLSearchParams(location.search).get('tab');
  let cur = null;
  for (const [g, items] of MENU) for (const it of items) {
    const [f, q] = it[0].split('?');
    if (f === file && (!q || q === 'tab=' + tab)) cur = cur && !q ? cur : [g, it];
  }
  if (!cur) for (const [g, items] of MENU) for (const it of items) if (it[0].split('?')[0] === file && !cur) cur = [g, it];

  const css = `
  .kn-bar{position:relative;z-index:9000;display:flex;align-items:center;gap:6px;height:44px;padding:0 10px;padding-top:env(safe-area-inset-top);
    background:var(--kn-bg);border-bottom:1px solid var(--kn-line);font:14px/1.2 -apple-system,BlinkMacSystemFont,'Apple SD Gothic Neo','Noto Sans KR',sans-serif;color:var(--kn-text)}
  .kn-bar a,.kn-bar button{color:inherit;text-decoration:none;background:none;border:0;font:inherit;cursor:pointer}
  .kn-home,.kn-btn{flex:none;display:flex;align-items:center;justify-content:center;min-width:36px;height:36px;border-radius:9px;font-size:18px}
  .kn-home:active,.kn-btn:active{background:var(--kn-soft)}
  .kn-crumb{flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .kn-crumb .g{color:var(--kn-muted)} .kn-crumb b{font-weight:700}
  .kn-sheet{position:fixed;inset:0;z-index:9001;background:var(--kn-bg);overflow:auto;padding:0 12px 24px;padding-top:env(safe-area-inset-top);display:none;color:var(--kn-text);
    font:14px/1.3 -apple-system,BlinkMacSystemFont,'Apple SD Gothic Neo','Noto Sans KR',sans-serif}
  .kn-sheet.on{display:block}
  .kn-sh{position:sticky;top:0;display:flex;align-items:center;justify-content:space-between;height:48px;background:var(--kn-bg)}
  .kn-sh b{font-size:16px}
  .kn-g{margin:10px 0 6px;font-size:12px;color:var(--kn-muted);font-weight:700}
  .kn-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:6px}
  .kn-it{display:flex;align-items:center;gap:8px;padding:11px 10px;border:1px solid var(--kn-line);border-radius:10px;color:inherit;text-decoration:none;background:var(--kn-card)}
  .kn-it.cur{border-color:var(--kn-accent);background:var(--kn-accent-soft);font-weight:700}
  .kn-it span{font-size:18px}
  .kn-dash{display:flex;align-items:center;gap:8px;padding:12px 10px;border-radius:10px;background:var(--kn-soft);color:inherit;text-decoration:none;font-weight:700;margin-top:4px}
  :root{--kn-bg:#fff;--kn-card:#fff;--kn-text:#1a1a1a;--kn-muted:#6e6e6e;--kn-line:#e5e5e5;--kn-soft:#f2f2ef;--kn-accent:#e5c400;--kn-accent-soft:#fff8cf}
  @media (prefers-color-scheme: dark){:root{--kn-bg:#1d1f1d;--kn-card:#262926;--kn-text:#ececea;--kn-muted:#9a9e98;--kn-line:#343834;--kn-soft:#2c302c;--kn-accent:#e5c400;--kn-accent-soft:#3a3618}}
  .kn-fab{position:fixed;left:12px;bottom:calc(14px + env(safe-area-inset-bottom));z-index:8999;width:44px;height:44px;border-radius:50%;border:1px solid var(--kn-line);
    background:var(--kn-card);color:var(--kn-text);font-size:20px;box-shadow:0 2px 10px rgba(0,0,0,.18);display:none;cursor:pointer}
  .kn-fab.on{display:block}
  .kn-hide{display:none!important}`;
  const st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const bar = document.createElement('div'); bar.className = 'kn-bar';
  bar.innerHTML = `<a class="kn-home" href="./" title="대시보드">🏠</a>
    <div class="kn-crumb">${cur ? `<span class="g">${esc(cur[0].replace(/^\S+\s/, ''))} › </span><b>${esc(cur[1][2])}</b>` : '<b>관리자</b>'}</div>
    <button class="kn-btn" type="button" aria-label="전체 메뉴">☰</button>`;
  const sheet = document.createElement('div'); sheet.className = 'kn-sheet';
  sheet.innerHTML = `<div class="kn-sh"><b>전체 메뉴</b><button class="kn-btn" type="button" aria-label="닫기">✕</button></div>
    <a class="kn-dash" href="./">🏠 대시보드</a>` +
    MENU.map(([g, items]) => `<div class="kn-g">${esc(g)}</div><div class="kn-grid">${items.map(it =>
      `<a class="kn-it ${cur && cur[1] === it ? 'cur' : ''}" href="${esc(it[0])}"><span>${it[1]}</span>${esc(it[2])}</a>`).join('')}</div>`).join('');
  const open = v => { sheet.classList.toggle('on', v); document.documentElement.style.overflow = v ? 'hidden' : ''; };
  bar.querySelector('.kn-btn').onclick = () => open(true);
  sheet.querySelector('.kn-sh .kn-btn').onclick = () => open(false);
  sheet.addEventListener('click', e => { if (e.target.closest('a')) open(false); });
  addEventListener('keydown', e => { if (e.key === 'Escape') open(false); });

  // 아래로 내리면 왼쪽 아래 둥근 ☰ (각 화면 위쪽 고정 줄과 겹치지 않게 맨 위 줄은 같이 스크롤됨)
  const fab = document.createElement('button'); fab.className = 'kn-fab'; fab.type = 'button'; fab.textContent = '☰'; fab.setAttribute('aria-label', '전체 메뉴');
  fab.onclick = () => open(true);
  addEventListener('scroll', () => fab.classList.toggle('on', scrollY > 120), { passive: true });
  const mount = () => {
    document.body.prepend(sheet); document.body.prepend(bar); document.body.appendChild(fab);
    // 예전 '← 관리자 홈'·'대시보드' 링크 숨김 (같은 일을 위 🏠가 함)
    document.querySelectorAll('a').forEach(a => {
      if (a.closest('.kn-bar,.kn-sheet')) return;
      const h = a.getAttribute('href') || '', t = a.textContent.trim();
      if ((h === './' || h === 'index.html' || h === '/kydzm/') && /관리자|대시보드/.test(t) && t.length < 12) a.classList.add('kn-hide');
    });
  };
  if (document.body) mount(); else document.addEventListener('DOMContentLoaded', mount);
})();
