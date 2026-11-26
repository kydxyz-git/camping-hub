/* 관리 화면 공통 메뉴 (사용자 261126 '메뉴 흐름 통일, 어느 메뉴든 쉽게 이동, 모바일 중요' → '왼쪽 고정 메뉴 + 위에 대메뉴 > 소메뉴 > 소메뉴')
 * 모든 관리 화면(대시보드 index.html 포함)이 <script src="lib/nav.js"></script> 한 줄로 씀.
 *  - 760px 이상(PC·태블릿·노트북 확대 화면): 왼쪽 고정 메뉴(항상 보임, 사용자 261126 '왼쪽 메뉴는 고정') · 폰(760 미만): ☰ 누르면 왼쪽에서 밀려 나옴 · 위 줄은 보조 메뉴
 *  - 맨 위 한 줄: 대메뉴 › 소메뉴 › (그 화면의 탭) — 칸을 누르면 같은 단계의 다른 것 고르기
 *  - 화면 탭(3단계)은 각 화면이 kydzNav.setSub([{key,label}], 지금 key, 고르면 부를 함수)로 알려 줌
 * 메뉴를 바꾸면 여기 MENU와 index.html 대시보드 grp 두 곳. iframe·?embed=1에선 안 보임.
 */
(function () {
  // 뒤로 가기 공통 (사용자 261126 '뒤로가기는 전체 다 있어야지'):
  //  - kydzNav.openLayer(close): 창(시트·모달)을 열 때 — 뒤로 가기를 누르면 페이지를 떠나지 않고 close()만 부름
  //  - kydzNav.closeLayer(): 창을 버튼으로 닫았을 때 — 남겨 둔 기록 한 칸을 같이 지움
  //  - kydzNav.onView(fn, 처음 view) + kydzNav.pushView(view): 탭·화면 바꿀 때 기록 — 뒤로 가기면 fn(전 view)
  //  iframe·?embed=1에선 기록을 안 남기고 그냥 닫기만
  const api = { setSub() {}, openLayer() {}, closeLayer() {}, pushView() {}, onView() {} };
  window.kydzNav = api;
  // 로딩 표시 (사용자 261126 '로딩 아이콘 — 막 빨리 누를 거 같아' → '정중앙에 눈에 잘 보이게, 로딩 중엔 다른 거 클릭 못 하게')
  //  - 버튼을 누르자마자 시작된 요청(읽고→쓰는 연달은 요청 포함)이 끝날 때까지: 화면 가운데 빙글 + 화면 전체 클릭 막음
  //  - 화면이 알아서 하는 요청(처음 불러오기·주기적 새로고침)은 막지 않음 — 맨 위 얇은 줄만
  (function () {
    const css = `.kn-load{position:fixed;left:0;right:0;top:0;height:3px;z-index:9500;pointer-events:none;opacity:0;transition:opacity .2s;background:linear-gradient(90deg,transparent,var(--brand,#FFE873),transparent) no-repeat;background-size:40% 100%;animation:knl 1s linear infinite}
    .kn-load.on{opacity:1}
    @keyframes knl{from{background-position:-60% 0}to{background-position:160% 0}}
    .kn-wait{position:fixed;inset:0;z-index:9800;display:none;align-items:center;justify-content:center;background:transparent;cursor:progress}
    .kn-wait.on{display:flex}
    .kn-wait.show{background:rgba(0,0,0,.28)}
    .kn-wait .box{display:none;flex-direction:column;align-items:center;gap:10px;padding:20px 26px;border-radius:16px;background:var(--card,#fff);color:var(--text,#1a1a1a);box-shadow:0 10px 30px rgba(0,0,0,.3);font-size:14px;font-weight:700}
    .kn-wait.show .box{display:flex}
    .kn-wait .sp{width:38px;height:38px;border:4px solid var(--line,#e5e5e5);border-top-color:var(--brand,#FFE873);border-radius:50%;animation:knspin .7s linear infinite}
    @keyframes knspin{to{transform:rotate(360deg)}}`;
    const stl = document.createElement('style'); stl.textContent = css; document.head.appendChild(stl);
    const line = document.createElement('div'); line.className = 'kn-load';
    const wait = document.createElement('div'); wait.className = 'kn-wait';
    wait.innerHTML = '<div class="box"><div class="sp"></div><div class="tx">불러오는 중…</div></div>';
    let n = 0, nb = 0, lastBtn = null, lastAt = 0, tShow = 0, tWait = 0, tSafe = 0, saving = false;
    const mountUi = () => { if (document.body) { if (!line.isConnected) document.body.appendChild(line); if (!wait.isConnected) document.body.appendChild(wait); } };
    const upd = () => {
      mountUi();
      clearTimeout(tShow);
      if (n > nb) tShow = setTimeout(() => line.classList.add('on'), 150); else line.classList.remove('on');
      if (nb > 0) {
        if (!wait.classList.contains('on')) {
          wait.classList.add('on');   // 클릭은 바로 막고, 보이는 건 0.15초 뒤(깜빡임 방지)
          clearTimeout(tWait); tWait = setTimeout(() => wait.classList.add('show'), 150);
          clearTimeout(tSafe); tSafe = setTimeout(() => { nb = 0; upd(); }, 25000);   // 응답이 안 와도 25초 뒤엔 풀어 줌
        }
        wait.querySelector('.tx').textContent = saving ? '저장 중…' : '불러오는 중…';
      } else { clearTimeout(tWait); clearTimeout(tSafe); wait.classList.remove('on', 'show'); saving = false; }
    };
    document.addEventListener('click', e => {
      const b = e.target.closest && e.target.closest('button,.btn,[role=button]');
      if (b && !b.closest('.kn-side,.kn-dd,.kn-wait')) { lastBtn = b; lastAt = performance.now(); }
    }, true);
    const of = window.fetch;
    if (!of) return;
    window.fetch = function (...a) {
      const byBtn = lastBtn && performance.now() - lastAt < 500 && !(a[1] && a[1].knQuiet);   // knQuiet: 사진 같은 뒤에서 받는 것은 화면을 막지 않음
      const m = ((a[1] && a[1].method) || (a[0] && a[0].method) || 'GET').toUpperCase();
      n++; if (byBtn) { nb++; if (m !== 'GET') saving = true; }
      upd();
      const done = () => {
        n = Math.max(0, n - 1);
        if (byBtn) { lastAt = performance.now();   // 바로 이어지는 요청(읽고→쓰기)도 같은 동작으로
          setTimeout(() => { nb = Math.max(0, nb - 1); upd(); }, 200); }
        upd();
      };
      return of.apply(this, a).then(r => { done(); return r; }, e => { done(); throw e; });
    };
  })();
  if (window.top !== window || /[?&]embed=1/.test(location.search)) return;
  (function () {
    const stack = []; let seq = 0, skip = 0, viewFn = null;
    let pend = null;   // 닫고 바로 다른 창을 여는 경우(닫기→열기)엔 기록 한 칸을 그대로 다시 씀
    api.openLayer = close => {
      const id = ++seq; stack.push({ id, close });
      if (pend) { clearTimeout(pend); pend = null; history.replaceState({ ...(history.state || {}), knPage: id }, ''); return; }
      history.pushState({ ...(history.state || {}), knPage: id, knView: (history.state || {}).knView }, '');
    };
    api.closeLayer = () => {
      const top = stack.pop();
      if (top && history.state && history.state.knPage === top.id) { clearTimeout(pend); pend = setTimeout(() => { pend = null; skip++; history.back(); }, 0); }
    };
    api.pushView = view => { if (JSON.stringify((history.state || {}).knView) !== JSON.stringify(view)) history.pushState({ knView: view }, ''); };
    api.onView = (fn, init) => { viewFn = fn; if (!history.state || history.state.knView === undefined) history.replaceState({ ...(history.state || {}), knView: init }, ''); };
    addEventListener('popstate', () => {
      if (skip) { skip--; return; }
      const st = history.state || {};
      if (stack.length && st.knPage !== stack[stack.length - 1].id) { const top = stack.pop(); try { top.close(); } catch (e) {} return; }
      if (viewFn && !st.knLayer && !st.knPage && st.knView !== undefined) viewFn(st.knView);
    });
  })();
  const MENU = [
    ['📌', '업무 관리', [['board.html', '📋', '운영판'], ['board.html?tab=posts', '📅', '올린 글 달력'], ['board.html?tab=autos', '⏰', '자동화'], ['board.html?tab=conns', '🔌', '연결']]],
    ['🎬', '콘텐츠 관리', [['./#series', '🎬', '시리즈 EP'], ['./#camps', '🏕', '캠핑장'], ['./#foods', '🍖', '음식'], ['./#items', '🛠', '장비']]],
    ['📱', 'SNS 관리', [['mutuals.html', '📸', '인스타'], ['threads.html', '🧵', '스레드'], ['youtube.html', '📺', '유튜브']]],
    ['🔥', '딜보드 관리', [['deals.html', '🔥', '딜 보드']]],
    ['📈', '성과 분석', [['./#stats', '📊', '홈페이지 통계'], ['./#coupang', '🛒', '쿠팡'], ['./#naver', '🟢', '네이버'], ['insights.html', '📈', '분석 카드']]],   // 순서 (사용자 261126)
    ['🧰', '기타', [['pipeline.html', '🗺️', '운영 지도'], ['camp-live.html', '🏕️', '캠핑사이트'], ['conti.html', '🎞', '콘티 보드']]],
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
  /* 틀 (사용자 261126 '화면에 따라 메뉴가 왼쪽에 붙어 불편'): 메뉴+내용을 한 덩어리(최대 1440px)로 창 가운데 */
  :root{--kn-shell:1680px;--kn-gut:0px}   /* 261126 사용자 "모든 페이지 가로폭 넓게" — 1440 → 1680 */
  @media (min-width:760px){:root{--kn-w:200px;--kn-gut:max(0px,calc((100vw - var(--kn-shell)) / 2))}
    body{padding-left:calc(var(--kn-gut) + var(--kn-w))!important;padding-right:var(--kn-gut)!important;box-sizing:border-box}
    .kn-side{left:var(--kn-gut)!important}}
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
  .kn-bar{position:sticky;top:0;z-index:9000;display:flex;align-items:center;gap:2px;min-height:44px;padding:0 8px;padding-top:env(safe-area-inset-top);background:var(--kn-bg);border-bottom:1px solid var(--kn-line);overflow-x:auto;scrollbar-width:none;box-sizing:border-box}
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
  .kn-dd a:hover,.kn-dd button:hover{background:var(--kn-soft)} .kn-ic{font-style:normal;width:20px;flex:none;text-align:center;font-size:15px;line-height:1} .kn-dd .cur{background:var(--kn-hi);font-weight:700}
  /* 위 줄 하나로 (사용자 261126 '2번도 해'): 각 화면의 제목 줄은 숨기고 그 버튼은 위 줄 오른쪽으로. 위 줄은 늘 고정 → 각 화면의 붙는 줄은 그 아래 */
  .kn-act{margin-left:auto;display:flex;align-items:center;gap:6px;flex:none;padding-left:8px}
  .kn-act>*{flex:none}
  .kn-side-foot{display:flex;gap:8px;margin:18px 4px 0;padding-top:12px;border-top:1px solid var(--kn-line)} .kn-side-foot>*{flex:1;padding:9px 10px;border:1px solid var(--kn-line);border-radius:8px;background:transparent;color:var(--kn-text);font:inherit;font-size:14px;cursor:pointer}
  .kn-page-act{display:flex;align-items:center;gap:6px}
  @media (max-width:759px){.kn-act{position:sticky;right:-8px;margin-right:-8px;padding-right:8px;background:transparent}}   /* 폰: 왼쪽 그림자(빛 비치는 느낌) 뺌 (사용자 261126) */
  .kn-page-act .sel{font-size:13px;font-weight:700;white-space:nowrap}
  .kn-act .btn.pri,.kn-act button.pri{background:var(--brand,#FFE873)!important;color:#1a1a1a!important;border-color:var(--brand,#FFE873)!important;font-weight:700}
  .kn-act .topbar-btn,.kn-act .topbar-link,.kn-act button{padding:5px 10px!important;font-size:12.5px!important;border:1px solid var(--kn-line)!important;border-radius:8px!important;background:transparent!important;color:var(--kn-text)!important}
  .kn-topbar-gone{display:none!important}
  .dash-nav,.tabs,.content-tabs,.save-bar,.savebar,.topbar{top:44px!important}
  /* 대시보드 가운데 메뉴 카드는 왼쪽 메뉴와 같아서 PC에선 뺌 (폰은 왼쪽 메뉴가 숨어 있어서 둠) */
  @media (min-width:760px){.dash-groups{display:none!important}}
  .kn-hide{display:none!important}`;
  const st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

  let sub = null;   // {items:[{key,label}], cur, on}
  const side = document.createElement('nav'); side.className = 'kn-side';
  const shade = document.createElement('div'); shade.className = 'kn-shade';
  const bar = document.createElement('div'); bar.className = 'kn-bar';
  // 뒤로 가기 = 열린 서랍·드롭다운만 닫기 (사용자 261126 '뒤로가기가 전체 메뉴를 뒤로 가서 불편')
  let layer = null;   // 'drawer' | 'dd'
  function pushLayer(k) { if (!layer) history.pushState({ knLayer: k }, ''); layer = k; }
  function popLayer() { if (layer) { layer = null; if (history.state && history.state.knLayer) history.back(); } }
  addEventListener('popstate', () => { if (layer) { layer = null; side.classList.remove('on'); shade.classList.remove('on'); if (dd) { dd.remove(); dd = null; bar.querySelectorAll('.open').forEach(x => x.classList.remove('open')); } } });
  const drawer = v => { if (v) pushLayer('drawer'); else if (side.classList.contains('on')) popLayer(); side.classList.toggle('on', v); shade.classList.toggle('on', v); };
  shade.onclick = () => drawer(false);

  function renderSide() {
    const w = where();
    side.innerHTML = `<a class="kn-home ${w ? '' : 'cur'}" href="./"><span class="ic">🏠</span>대시보드</a>` +
      MENU.map(([gi, g, items], i) => `<div class="kn-g">${esc(g)}</div><div class="kn-grp">` + items.map(it =>
        `<a href="${esc(it[0])}" class="${w && w[1] === it ? 'cur' : ''}"><span class="ic">${it[1]}</span>${esc(it[2])}</a>`).join('') + '</div>').join('');
    side.querySelectorAll('a').forEach(a => a.addEventListener('click', () => { layer = null; side.classList.remove('on'); shade.classList.remove('on'); }));
    if (foot.children.length) side.appendChild(foot);
  }
  // 폰: '← 사이트'·'로그아웃'은 위 줄 대신 ☰ 메뉴 맨 아래로 (사용자 261126 '오른쪽 위 사이트·로그아웃 버튼 이상해')
  const foot = document.createElement('div'); foot.className = 'kn-side-foot';
  const phoneQ = matchMedia('(max-width: 759px)');
  function placeFoot() {
    const act = bar.querySelector('.kn-act');
    const els = [...document.querySelectorAll('#topbar-back, #topbar-logout')];
    if (!els.length) return;
    if (phoneQ.matches) { els.forEach(x => foot.appendChild(x)); side.appendChild(foot); }
    else if (act) { els.forEach(x => act.appendChild(x)); foot.remove(); }
    if (act) act.style.display = act.children.length ? '' : 'none';
  }
  phoneQ.addEventListener && phoneQ.addEventListener('change', placeFoot);
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
    const keep = bar.querySelector('.kn-act');
    bar.innerHTML = h;
    if (keep) bar.appendChild(keep);
    bar.querySelector('[data-burger]').onclick = () => drawer(true);
    bar.querySelectorAll('[data-lv]').forEach(b => b.onclick = e => { e.stopPropagation(); dropdown(b, +b.dataset.lv); });
  }
  let dd = null;
  function closeDD(fromNav) { if (dd) { dd.remove(); dd = null; bar.querySelectorAll('.open').forEach(x => x.classList.remove('open')); if (!fromNav && layer === 'dd') popLayer(); } }
  function dropdown(btn, lv) {
    const was = btn.classList.contains('open'); closeDD(); if (was) return;
    const w = where(); let html = '';
    if (lv === 0 || lv === 1) html = MENU.map((g, i) => `<a href="${esc(g[2][0][0])}" class="${w && w[0] === i ? 'cur' : ''}"><i class="kn-ic">${g[0]}</i>${esc(g[1])}</a>`).join('') + (lv === 1 ? '<a href="./"><i class="kn-ic">🏠</i>대시보드</a>' : '');
    else if (lv === 2) html = MENU[w[0]][2].map(it => `<a href="${esc(it[0])}" class="${w[1] === it ? 'cur' : ''}"><i class="kn-ic">${it[1]}</i>${esc(it[2])}</a>`).join('');
    else if (lv === 3 && sub) html = sub.items.map(x => `<button data-k="${esc(x.key)}" class="${x.key === sub.cur ? 'cur' : ''}">${esc(x.label)}</button>`).join('');
    dd = document.createElement('div'); dd.className = 'kn-dd'; dd.innerHTML = html; pushLayer('dd');
    document.body.appendChild(dd); btn.classList.add('open');
    const r = btn.getBoundingClientRect();
    dd.style.top = (r.bottom + 4) + 'px';
    dd.style.left = Math.max(8, Math.min(r.left, innerWidth - dd.offsetWidth - 8)) + 'px';
    dd.querySelectorAll('[data-k]').forEach(b => b.onclick = () => { closeDD(); setTimeout(() => sub.on(b.dataset.k), 30); });
    dd.querySelectorAll('a').forEach(a => a.addEventListener('click', () => { layer = null; closeDD(true); }));
  }
  addEventListener('click', e => { if (dd && !dd.contains(e.target)) closeDD(); });
  addEventListener('scroll', () => closeDD(), { passive: true });
  addEventListener('keydown', e => { if (e.key === 'Escape') { closeDD(); drawer(false); } });
  addEventListener('hashchange', () => { const f = location.pathname.split('/').pop(); if (f === '' || f === 'index.html') { sub = null; renderSide(); renderBar(); } });

  api.setSub = (items, cur, on) => { sub = items && items.length ? { items, cur, on } : null; renderBar(); };
  // 화면별 버튼을 위 줄 오른쪽 끝에 (사용자 261126 '버튼은 오른쪽 상단에') — node 하나 또는 null
  api.setActions = node => {
    let slot = bar.querySelector('.kn-act');
    if (!slot) { slot = document.createElement('div'); slot.className = 'kn-act'; bar.appendChild(slot); }
    let page = slot.querySelector('.kn-page-act');
    if (!page) { page = document.createElement('span'); page.className = 'kn-page-act'; slot.prepend(page); }
    page.replaceChildren(...(node ? [node] : []));
  };

  function absorbTopbar() {   // 각 화면 제목 줄의 버튼을 위 줄로 옮기고 제목 줄은 숨김
    const tb = document.querySelector('body > .topbar, .app > .topbar, #app > .topbar, body > div > .topbar');
    if (!tb || tb.dataset.knDone) return;
    tb.dataset.knDone = '1';
    const act = document.createElement('div'); act.className = 'kn-act';
    const dot = tb.querySelector('.save-dot'); if (dot) act.appendChild(dot);
    [...tb.children].forEach(ch => {
      if (ch.matches('.topbar-title, h1, h2') || ch.classList.contains('kn-hide')) return;
      if (ch.matches('a, button')) { if (!ch.classList.contains('kn-hide')) act.appendChild(ch); return; }
      [...ch.children].forEach(x => { if (!x.classList.contains('kn-hide')) act.appendChild(x); });
    });
    if (act.children.length) bar.appendChild(act);
    tb.classList.add('kn-topbar-gone');
  }
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
    absorbTopbar(); placeFoot();
  };
  if (document.body) mount(); else document.addEventListener('DOMContentLoaded', mount);
  // 안드로이드에서 인스타 링크는 인스타 앱으로 (사용자 261126 '링크 누르면 인스타 앱으로 연결이 안 되네') — 메인 홈페이지와 같은 intent:// 방식, 앱 없으면 웹
  if (/Android/i.test(navigator.userAgent)) document.addEventListener('click', e => {
    const a = e.target.closest && e.target.closest('a[href]'); if (!a) return;
    const href = a.getAttribute('href') || '';
    if (!/^https?:\/\/(www\.)?instagram\.com\//i.test(href)) return;
    const url = href.split('?')[0].replace(/\/(reel|tv)\//, '/p/');
    e.preventDefault();
    location.href = 'intent://' + url.replace(/^https?:\/\//, '') + '#Intent;scheme=https;action=android.intent.action.VIEW;category=android.intent.category.BROWSABLE;package=com.instagram.android;S.browser_fallback_url=' + encodeURIComponent(url) + ';end';
  }, true);
})();
