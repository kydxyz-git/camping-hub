/* 관리 화면 공통 메뉴 (사용자 261126 '메뉴 흐름 통일, 어느 메뉴든 쉽게 이동, 모바일 중요' → '왼쪽 고정 메뉴 + 위에 대메뉴 > 소메뉴 > 소메뉴')
 * 모든 관리 화면(대시보드 index.html 포함)이 <script src="lib/nav.js"></script> 한 줄로 씀.
 *  - 760px 이상(PC·태블릿·노트북 확대 화면): 왼쪽 고정 메뉴(항상 보임, 사용자 261126 '왼쪽 메뉴는 고정') · 폰(760 미만): ☰ 누르면 왼쪽에서 밀려 나옴 · 위 줄은 보조 메뉴
 *  - 맨 위 한 줄: 대메뉴 › 소메뉴 › (그 화면의 탭) — 칸을 누르면 같은 단계의 다른 것 고르기
 *  - 화면 탭(3단계)은 각 화면이 kydzNav.setSub([{key,label}], 지금 key, 고르면 부를 함수)로 알려 줌
 * 메뉴를 바꾸면 여기 MENU와 index.html 대시보드 grp 두 곳. iframe·?embed=1에선 안 보임.
 */
(function () {
  const api = { setSub() {} };
  window.kydzNav = api;
  if (window.top !== window || /[?&]embed=1/.test(location.search)) return;
  const MENU = [
    ['📌', '업무 관리', [['board.html', '📋', '운영판'], ['board.html?tab=posts', '📅', '올린 글 달력'], ['board.html?tab=autos', '⏰', '자동화'], ['board.html?tab=conns', '🔌', '연결']]],
    ['🎬', '콘텐츠 관리', [['./#series', '🎬', '시리즈 EP'], ['./#camps', '🏕', '캠핑장'], ['./#foods', '🍖', '음식'], ['./#items', '🛠', '장비']]],
    ['📱', 'SNS 관리', [['mutuals.html', '📸', '인스타'], ['threads.html', '🧵', '스레드']]],
    ['🔥', '딜보드 관리', [['deals.html', '🔥', '딜 보드']]],
    ['📈', '성과 분석', [['insights.html', '📈', '성과 분석'], ['./#coupang', '🛒', '쿠팡 실적'], ['./#stats', '📊', '홈페이지 통계']]],
    ['🗂', '기타', [['pipeline.html', '🗺️', '운영 지도'], ['camp-live.html', '🏕️', '캠핑사이트'], ['conti.html', '🎞', '콘티 보드']]],
  ];
  const norm = h => h.replace(/^\.\//, '').replace(/^index\.html/, '');
  function where() {   // [그룹 index, 항목] 또는 null(대시보드)
    const file = location.pathname.split('/').pop() || '';
    const isIndex = file === '' || file === 'index.html';
    const hash = (location.hash || '').split('/')[0];
    const tab = new URLSearchParams(location.search).get('tab');
    let hit = null;
    MENU.forEach((g, gi) => g[2].forEach(it => {
      const [f, q] = norm(it[0]).split('?');
      if (isIndex) { if (f.startsWith('#') && f === hash) hit = [gi, it]; return; }
      if (f === file && (q ? q === 'tab=' + tab : !hit)) hit = [gi, it];
    }));
    return hit;
  }
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  const css = `
  :root{--kn-w:0px;--kn-bg:#fff;--kn-side:#f7f7f5;--kn-text:#1a1a1a;--kn-muted:#6e6e6e;--kn-line:#e5e5e5;--kn-soft:#ececea;--kn-hi:#fff3b0;--kn-card:#fff}
  @media (prefers-color-scheme: dark){:root{--kn-bg:#1d1f1d;--kn-side:#181a18;--kn-text:#ececea;--kn-muted:#9a9e98;--kn-line:#343834;--kn-soft:#2c302c;--kn-hi:#3d3816;--kn-card:#262926}}
  @media (min-width:760px){:root{--kn-w:200px} body{padding-left:var(--kn-w)!important}}
  .kn-side,.kn-bar,.kn-dd{font:14px/1.3 -apple-system,BlinkMacSystemFont,'Apple SD Gothic Neo','Noto Sans KR',sans-serif;color:var(--kn-text)}
  .kn-side{position:fixed;top:0;bottom:0;left:0;width:200px;z-index:9100;background:var(--kn-side);border-right:1px solid var(--kn-line);overflow-y:auto;padding:10px 8px 24px;padding-top:calc(10px + env(safe-area-inset-top));box-sizing:border-box}
  .kn-side a{display:flex;align-items:center;gap:8px;padding:7px 10px;border-radius:8px;color:inherit;text-decoration:none}
  .kn-side a:hover{background:var(--kn-soft)} .kn-side a.cur{background:var(--kn-hi);font-weight:700}
  .kn-side .kn-home{font-weight:700;margin-bottom:6px}
  .kn-side .kn-g{font-size:11px;color:var(--kn-muted);font-weight:700;margin:14px 6px 4px;padding-top:12px;border-top:1px solid var(--kn-line);letter-spacing:.04em}
  .kn-side .kn-grp{margin-left:12px;padding-left:6px;border-left:2px solid var(--kn-line)}
  .kn-side .kn-grp a{padding:6px 8px;font-size:14px}
  .kn-side .kn-grp .ic{width:18px;font-size:14px}
  .kn-side .kn-home{font-size:15px}
  .kn-side .ic{width:20px;text-align:center;flex:none}
  .kn-shade{position:fixed;inset:0;z-index:9099;background:rgba(0,0,0,.35);display:none}
  @media (max-width:759px){.kn-side{transform:translateX(-105%);transition:transform .2s;width:260px;visibility:hidden} .kn-side.on{transform:none;visibility:visible;box-shadow:4px 0 20px rgba(0,0,0,.25)} .kn-shade.on{display:block}}
  .kn-bar{position:relative;z-index:9000;display:flex;align-items:center;gap:2px;min-height:44px;padding:0 8px;padding-top:env(safe-area-inset-top);background:var(--kn-bg);border-bottom:1px solid var(--kn-line);overflow-x:auto;scrollbar-width:none;box-sizing:border-box}
  .kn-bar::-webkit-scrollbar{display:none}
  .kn-bar button{flex:none;background:none;border:0;color:inherit;font:inherit;cursor:pointer;padding:6px 8px;border-radius:8px;white-space:nowrap}
  .kn-bar button:hover,.kn-bar button.open{background:var(--kn-soft)}
  .kn-bar .kn-burger{font-size:18px;padding:6px 10px}
  @media (min-width:760px){.kn-bar .kn-burger{display:none}}
  .kn-bar .sep{color:var(--kn-muted);flex:none}
  .kn-bar .lv1{color:var(--kn-muted)} .kn-bar .lv-last{font-weight:700}
  .kn-bar .car{font-size:10px;color:var(--kn-muted);margin-left:3px}
  .kn-dd{position:fixed;z-index:9200;min-width:170px;max-width:calc(100vw - 16px);max-height:70vh;overflow:auto;background:var(--kn-card);border:1px solid var(--kn-line);border-radius:10px;box-shadow:0 8px 24px rgba(0,0,0,.18);padding:4px}
  .kn-dd a,.kn-dd button{display:flex;gap:8px;align-items:center;width:100%;text-align:left;padding:9px 10px;border-radius:7px;border:0;background:none;color:inherit;font:inherit;text-decoration:none;cursor:pointer;box-sizing:border-box}
  .kn-dd a:hover,.kn-dd button:hover{background:var(--kn-soft)} .kn-dd .cur{background:var(--kn-hi);font-weight:700}
  .kn-hide{display:none!important}`;
  const st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

  let sub = null;   // {items:[{key,label}], cur, on}
  const side = document.createElement('nav'); side.className = 'kn-side';
  const shade = document.createElement('div'); shade.className = 'kn-shade';
  const bar = document.createElement('div'); bar.className = 'kn-bar';
  const drawer = v => { side.classList.toggle('on', v); shade.classList.toggle('on', v); };
  shade.onclick = () => drawer(false);

  function renderSide() {
    const w = where();
    side.innerHTML = `<a class="kn-home ${w ? '' : 'cur'}" href="./"><span class="ic">🏠</span>대시보드</a>` +
      MENU.map(([gi, g, items], i) => `<div class="kn-g">${esc(g)}</div><div class="kn-grp">` + items.map(it =>
        `<a href="${esc(it[0])}" class="${w && w[1] === it ? 'cur' : ''}"><span class="ic">${it[1]}</span>${esc(it[2])}</a>`).join('') + '</div>').join('');
    side.querySelectorAll('a').forEach(a => a.addEventListener('click', () => drawer(false)));
  }
  function renderBar() {
    const w = where();
    let h = `<button class="kn-burger" data-burger aria-label="메뉴">☰</button>`;
    if (!w) h += `<button class="lv-last" data-lv="0">🏠 대시보드<span class="car">▾</span></button>`;
    else {
      const g = MENU[w[0]];
      h += `<button class="lv1" data-lv="1">${g[0]} ${esc(g[1])}<span class="car">▾</span></button><span class="sep">›</span>`;
      h += `<button class="${sub ? '' : 'lv-last'}" data-lv="2">${esc(w[1][2])}<span class="car">▾</span></button>`;
      if (sub) { const c = sub.items.find(x => x.key === sub.cur); h += `<span class="sep">›</span><button class="lv-last" data-lv="3">${esc(c ? c.label : '')}<span class="car">▾</span></button>`; }
    }
    bar.innerHTML = h;
    bar.querySelector('[data-burger]').onclick = () => drawer(true);
    bar.querySelectorAll('[data-lv]').forEach(b => b.onclick = e => { e.stopPropagation(); dropdown(b, +b.dataset.lv); });
  }
  let dd = null;
  function closeDD() { if (dd) { dd.remove(); dd = null; bar.querySelectorAll('.open').forEach(x => x.classList.remove('open')); } }
  function dropdown(btn, lv) {
    const was = btn.classList.contains('open'); closeDD(); if (was) return;
    const w = where(); let html = '';
    if (lv === 0 || lv === 1) html = MENU.map((g, i) => `<a href="${esc(g[2][0][0])}" class="${w && w[0] === i ? 'cur' : ''}">${g[0]} ${esc(g[1])}</a>`).join('') + (lv === 1 ? '<a href="./">🏠 대시보드</a>' : '');
    else if (lv === 2) html = MENU[w[0]][2].map(it => `<a href="${esc(it[0])}" class="${w[1] === it ? 'cur' : ''}">${it[1]} ${esc(it[2])}</a>`).join('');
    else if (lv === 3 && sub) html = sub.items.map(x => `<button data-k="${esc(x.key)}" class="${x.key === sub.cur ? 'cur' : ''}">${esc(x.label)}</button>`).join('');
    dd = document.createElement('div'); dd.className = 'kn-dd'; dd.innerHTML = html;
    document.body.appendChild(dd); btn.classList.add('open');
    const r = btn.getBoundingClientRect();
    dd.style.top = (r.bottom + 4) + 'px';
    dd.style.left = Math.max(8, Math.min(r.left, innerWidth - dd.offsetWidth - 8)) + 'px';
    dd.querySelectorAll('[data-k]').forEach(b => b.onclick = () => { closeDD(); sub.on(b.dataset.k); });
    dd.querySelectorAll('a').forEach(a => a.addEventListener('click', closeDD));
  }
  addEventListener('click', e => { if (dd && !dd.contains(e.target)) closeDD(); });
  addEventListener('scroll', closeDD, { passive: true });
  addEventListener('keydown', e => { if (e.key === 'Escape') { closeDD(); drawer(false); } });
  addEventListener('hashchange', () => { sub = null; renderSide(); renderBar(); });

  api.setSub = (items, cur, on) => { sub = items && items.length ? { items, cur, on } : null; renderBar(); };

  const mount = () => {
    renderSide(); renderBar();
    document.body.prepend(bar); document.body.appendChild(shade); document.body.appendChild(side);
    // 예전 '← 관리자 홈'·'대시보드' 링크 숨김 (🏠·왼쪽 메뉴가 같은 일)
    document.querySelectorAll('a').forEach(a => {
      if (a.closest('.kn-bar,.kn-side')) return;
      const h = a.getAttribute('href') || '', t = a.textContent.trim();
      if ((h === './' || h === 'index.html' || h === '/kydzm/') && /관리자|대시보드/.test(t) && t.length < 12) a.classList.add('kn-hide');
    });
    document.querySelectorAll('button[onclick*="index.html"]').forEach(b => { if (/관리자|대시보드/.test(b.textContent) && b.textContent.trim().length < 12) b.classList.add('kn-hide'); });
  };
  if (document.body) mount(); else document.addEventListener('DOMContentLoaded', mount);
})();
