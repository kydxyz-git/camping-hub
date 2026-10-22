#!/usr/bin/env node
/*
 * 공대남자 캠핑사이트 — 내 컴퓨터의 Claude Code 작업을 실시간으로 캠핑장에 보여주는 프로그램
 *
 * Claude Code가 남기는 작업 기록(~/.claude/projects/**.jsonl)을 지켜보다가
 * 새 작업이 생기면 캠핑장 화면(kydzm/camp-live.html)에 바로 보낸다. 훅·Worker·토큰 없음, 컴퓨터 안에서만 돈다.
 *
 * 실행:  node camp-watch.js PC        → http://localhost:4321  (같은 와이파이 폰: http://컴퓨터IP:4321)
 *        node camp-watch.js 노트북    ← 이름은 캠핑장에 '공대남자·PC'처럼 표시 (컴퓨터가 2대 이상일 때)
 * 컴퓨터 여러 대: 각자 켜 두면 같은 와이파이 안에서 서로 찾아(UDP 4322) 작업·사용량을 합쳐 보여준다.
 *        못 찾으면 CAMP_PEERS=http://192.168.0.12:4321 처럼 직접 지정 (쉼표로 여러 개)
 * 설정:  PORT=4321  CLAUDE_CONFIG_DIR=…(기본 ~/.claude)  CAMP_TOKEN_BUDGET=…(5시간 장작 총량, 없으면 지난 기록 중 최대치로 추정)
 * Node 18 이상, 설치할 패키지 없음.
 */
'use strict';
const fs = require('fs'), path = require('path'), http = require('http'), os = require('os'), dgram = require('dgram');

const PORT = +process.env.PORT || 4321;
const ROOT = path.join(process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), '.claude'), 'projects');
const PAGE_URL = 'https://kydz.kr/kydzm/camp-live.html';
const LOCAL_PAGE = path.join(__dirname, '..', 'kydzm', 'camp-live.html');
const ACTIVE_MS = 30 * 60e3;   // 최근 30분 안에 바뀐 기록만 지켜봄
const BLOCK_MS = 5 * 3600e3;   // 사용량 초기화 주기 (5시간)
const MACHINE = (process.argv[2] || process.env.CAMP_NAME || os.hostname()).slice(0, 12);
const ME = Math.random().toString(36).slice(2, 10);   // 이 프로그램 구분용 (서로 찾기)
const DISCO_PORT = 4322;

// ── 화면으로 보내기 (Server-Sent Events) ──
const clients = new Set();    // 캠핑장 화면들 (/events: 모든 컴퓨터 작업)
const feeds = new Set();      // 다른 컴퓨터의 camp-watch (/feed: 이 컴퓨터 작업만)
const recent = [];            // 새로 연 화면에 보여줄 최근 이벤트
const sse = (set, ev) => { const line = `data: ${JSON.stringify(ev)}\n\n`; for (const res of set) res.write(line); };
function send(ev, fromPeer) {
  ev.at = ev.at || Date.now();
  if (!fromPeer) { ev.machine = MACHINE; sse(feeds, ev); }
  if (ev.kind) console.log(`  ${new Date(ev.at + 9 * 3600e3).toISOString().slice(11, 19)} ${fromPeer ? ev.machine + ' ' : ''}${ev.name} · ${ev.text || ''}  (화면 ${clients.size}개)`);
  recent.push(ev); if (recent.length > 40) recent.shift();
  sse(clients, ev);
}

// ── 기록 파일 지켜보기 ──
const files = new Map();      // 파일 → { pos, session, agent, name, lastAt }
function listJsonl(dir, out = []) {
  let ents = [];
  try { ents = fs.readdirSync(dir, { withFileTypes: true }); } catch (e) { return out; }
  for (const e of ents) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) { if (e.name !== 'tool-results') listJsonl(p, out); }
    else if (e.name.endsWith('.jsonl')) out.push(p);
  }
  return out;
}
const base = p => path.basename(String(p || '')).slice(0, 40);
function describe(name, input = {}) {
  switch (name) {
    case 'Read': case 'NotebookRead': return `${base(input.file_path || input.notebook_path)} 읽기`;
    case 'Edit': case 'MultiEdit': case 'NotebookEdit': return `${base(input.file_path || input.notebook_path)} 고치기`;
    case 'Write': return `${base(input.file_path)} 쓰기`;
    case 'Grep': return `'${String(input.pattern || '').slice(0, 30)}' 찾기`;
    case 'Glob': return `${String(input.pattern || '').slice(0, 30)} 파일 찾기`;
    case 'Bash': return String(input.description || input.command || '').split('\n')[0].slice(0, 50);
    case 'WebSearch': return `'${String(input.query || '').slice(0, 30)}' 검색`;
    case 'WebFetch': try { return `${new URL(input.url).host} 읽기`; } catch (e) { return '웹 페이지 읽기'; }
    case 'Agent': case 'Task': return `동료에게: ${String(input.description || input.prompt || '').slice(0, 40)}`;
    case 'TodoWrite': case 'TaskCreate': case 'TaskUpdate': return '할 일 정리';
    default: return name.startsWith('mcp__') ? `${name.split('__')[1]} 쓰기` : name;
  }
}
// 사용량: 5시간 단위 블록별 토큰 합 (같은 응답이 블록마다 여러 줄로 나뉘어 기록되므로 message.id로 한 번만)
// 같은 계정이니 다른 컴퓨터 사용량도 합친다
const seenMsg = new Set(), usage = [];   // [{id, at, tokens, local}]
function addUsageRec(r, local) {
  if (!r.id || seenMsg.has(r.id)) return;
  seenMsg.add(r.id); usage.push({ id: r.id, at: r.at, tokens: r.tokens, local });
  if (local) sse(feeds, { type: 'usage', id: r.id, at: r.at, tokens: r.tokens });
}
function addUsage(j) {
  const m = j.message || {}, u = m.usage;
  if (!u || !m.id) return;
  addUsageRec({ id: m.id, at: Date.parse(j.timestamp) || Date.now(),
    tokens: (u.input_tokens || 0) + (u.cache_creation_input_tokens || 0) + (u.output_tokens || 0) }, true);
}
function woodStatus() {
  usage.sort((a, b) => a.at - b.at);
  const blocks = [];
  for (const u of usage) {
    const b = blocks[blocks.length - 1];
    if (!b || u.at >= b.start + BLOCK_MS) blocks.push({ start: Math.floor(u.at / 3600e3) * 3600e3, tokens: u.tokens });
    else b.tokens += u.tokens;
  }
  const now = Date.now(), cur = blocks.length && now < blocks[blocks.length - 1].start + BLOCK_MS ? blocks[blocks.length - 1] : null;
  const budget = +process.env.CAMP_TOKEN_BUDGET || Math.max(0, ...blocks.slice(0, cur ? -1 : undefined).map(b => b.tokens));
  const used = cur ? cur.tokens : 0;
  return { type: 'wood', used, budget, estimated: !process.env.CAMP_TOKEN_BUDGET,
    level: budget ? Math.max(0, 1 - used / budget) : null, resetAt: cur ? cur.start + BLOCK_MS : null };
}

function handleLine(f, info, line, live) {
  let j; try { j = JSON.parse(line); } catch (e) { return; }
  if (j.type === 'assistant') addUsage(j);
  if (!live) return;
  const side = j.isSidechain || /agent-/.test(path.basename(f));
  const agent = side ? 'sub:' + (j.agentId || path.basename(f, '.jsonl')) : 'main:' + (j.sessionId || info.session);
  const name = side ? '동료' : '공대남자';
  const project = path.basename(path.dirname(side ? path.dirname(path.dirname(f)) : f)).replace(/^-/, '').split('-').slice(-2).join('-');
  info.agent = agent; info.lastAt = Date.now(); info.side = side;
  const ev = { agent, name, project, side };
  if (j.type === 'assistant') {
    const c = (j.message && j.message.content) || [];
    for (const b of c) if (b.type === 'tool_use') send({ ...ev, kind: 'tool', tool: b.name, text: describe(b.name, b.input) });
    if (j.message && j.message.stop_reason === 'end_turn' && !c.some(b => b.type === 'tool_use') && !side) send({ ...ev, kind: 'idle', text: '다음 지시 기다리는 중' });
  } else if (j.type === 'user' && !j.toolUseResult && !side) {
    const c = j.message && j.message.content;
    const txt = typeof c === 'string' ? c : Array.isArray(c) ? (c.find(b => b.type === 'text') || {}).text : '';
    if (txt && !/^<|^\[Request interrupted/.test(txt)) send({ ...ev, kind: 'think', text: '새 지시 받음 — 계획 세우는 중' });
  } else if (j.type === 'queue-operation' && j.operation === 'enqueue' && !side) {
    send({ ...ev, kind: 'think', text: '추가 지시 받음' });
  }
}
function scan(first) {
  const now = Date.now();
  for (const f of listJsonl(ROOT)) {
    let st; try { st = fs.statSync(f); } catch (e) { continue; }
    let info = files.get(f);
    if (!info) {
      // 처음 보는 파일: 사용량 계산을 위해 7일 안 기록은 읽되, 화면에는 최근 30분 이후 새 줄만
      if (now - st.mtimeMs > 7 * 864e5) continue;
      info = { pos: 0, session: path.basename(f, '.jsonl'), lastAt: 0 };
      files.set(f, info);
      const live = !first && now - st.mtimeMs < ACTIVE_MS;
      readNew(f, info, st.size, live);
      continue;
    }
    if (st.size > info.pos) readNew(f, info, st.size, true);
    // 동료 기록이 20초 넘게 조용하면 일 끝낸 걸로
    if (info.side && info.lastAt && now - info.lastAt > 20e3 && !info.doneSent) { info.doneSent = true; send({ agent: info.agent, name: '동료', kind: 'done', text: '보고하고 돌아감' }); }
    if (st.size > info.pos) info.doneSent = false;
  }
}
function readNew(f, info, size, live) {
  try {
    const fd = fs.openSync(f, 'r'), len = size - info.pos, buf = Buffer.alloc(len);
    fs.readSync(fd, buf, 0, len, info.pos); fs.closeSync(fd);
    const txt = buf.toString('utf8'), cut = txt.lastIndexOf('\n');
    if (cut < 0) return;
    info.pos += Buffer.byteLength(txt.slice(0, cut + 1));
    for (const line of txt.slice(0, cut).split('\n')) if (line.trim()) handleLine(f, info, line, live);
    if (live) info.doneSent = false;
  } catch (e) { /* 쓰는 중이면 다음에 다시 */ }
}

// ── 웹 서버 ──
let pageCache = null;
async function page() {
  if (fs.existsSync(LOCAL_PAGE)) return fs.readFileSync(LOCAL_PAGE, 'utf8');
  if (pageCache && Date.now() - pageCache.at < 10 * 60e3) return pageCache.html;
  const r = await fetch(PAGE_URL); const html = await r.text();
  pageCache = { at: Date.now(), html }; return html;
}
http.createServer(async (req, res) => {
  if (req.url.startsWith('/feed')) {
    // 다른 컴퓨터가 가져가는 이 컴퓨터 기록: 최근 10시간 사용량부터
    res.writeHead(200, { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', Connection: 'keep-alive' });
    res.write(`data: ${JSON.stringify({ type: 'peer', id: ME, machine: MACHINE })}\n\n`);
    const since = Date.now() - 2 * BLOCK_MS;
    for (const u of usage) if (u.local && u.at > since) res.write(`data: ${JSON.stringify({ type: 'usage', id: u.id, at: u.at, tokens: u.tokens })}\n\n`);
    feeds.add(res); req.on('close', () => feeds.delete(res));
    return;
  }
  if (req.url.startsWith('/events')) {
    res.writeHead(200, { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', Connection: 'keep-alive', 'Access-Control-Allow-Origin': '*' });
    res.write(`data: ${JSON.stringify(hello())}\n\n`);
    for (const ev of recent.slice(-15)) res.write(`data: ${JSON.stringify(ev)}\n\n`);
    res.write(`data: ${JSON.stringify(woodStatus())}\n\n`);
    clients.add(res); console.log(`  캠핑장 화면 연결됨 (${clients.size}개)`);
    req.on('close', () => { clients.delete(res); console.log(`  캠핑장 화면 닫힘 (${clients.size}개)`); });
    return;
  }
  try {
    const html = (await page()).replace('<head>', '<head><script>window.CAMP_LIVE = "/events";</script>');
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' }); res.end(html);
  } catch (e) { res.writeHead(502); res.end('화면을 불러오지 못했어요: ' + e.message); }
}).listen(PORT, '0.0.0.0', () => {
  const ips = Object.values(os.networkInterfaces()).flat().filter(i => i && i.family === 'IPv4' && !i.internal).map(i => i.address);
  console.log(`\n  공대남자 캠핑사이트 켜짐`);
  console.log(`  이 컴퓨터:  http://localhost:${PORT}`);
  for (const ip of ips) console.log(`  같은 와이파이 폰: http://${ip}:${PORT}`);
  console.log(`  이 컴퓨터 이름: ${MACHINE}   (바꾸려면 node camp-watch.js PC)`);
  console.log(`  지켜보는 기록: ${ROOT}`);
  if (!fs.existsSync(ROOT)) console.log(`  ⚠ 기록 폴더가 아직 없어요 — 이 컴퓨터에서 Claude Code를 한 번 쓰면 생기고, 그때부터 자동으로 보여요.\n    (클라우드 세션만 쓰면 이 컴퓨터엔 기록이 안 남아요)`);
  console.log(`  끄려면 이 창에서 Ctrl+C\n`);
  {
    const list = [...files.keys()].map(f => { try { return [f, fs.statSync(f).mtimeMs]; } catch (e) { return [f, 0]; } }).sort((a, b) => b[1] - a[1]);
    console.log(`  찾은 기록 파일 ${list.length}개 (최근 7일)` + (list[0] ? ` · 가장 최근: ${path.relative(ROOT, list[0][0]).slice(0, 70)} (${Math.round((Date.now() - list[0][1]) / 60e3)}분 전)` : ''));
    console.log('  이제 claude로 일을 시키면 아래에 한 줄씩 찍혀요.\n');
  }
});

scan(true);
setInterval(() => scan(false), 1000);
setInterval(() => { const w = woodStatus(); const line = `data: ${JSON.stringify(w)}\n\n`; for (const r of clients) r.write(line); }, 30e3);
setInterval(() => { for (const r of clients) r.write(': ping\n\n'); }, 20e3);   // 연결 유지

// ── 다른 컴퓨터(PC·노트북) 찾아서 합치기 ──
const peers = new Map();      // 주소 → { id, machine }
const hello = () => ({ type: 'hello', at: Date.now(), machines: [MACHINE, ...[...peers.values()].map(p => p.machine).filter(Boolean)] });
function connectPeer(url) {
  if (peers.has(url)) return;
  const info = { machine: '' }; peers.set(url, info);
  const req = http.get(url + '/feed', res => {
    let buf = '';
    res.setEncoding('utf8');
    res.on('data', d => {
      buf += d; let i;
      while ((i = buf.indexOf('\n\n')) >= 0) {
        const chunk = buf.slice(0, i); buf = buf.slice(i + 2);
        const line = chunk.split('\n').find(l => l.startsWith('data: '));
        if (!line) continue;
        let ev; try { ev = JSON.parse(line.slice(6)); } catch (e) { continue; }
        if (ev.type === 'peer') {
          // 나 자신이거나, 같은 컴퓨터를 다른 주소로 이미 연결한 경우
          if (ev.id === ME || [...peers.values()].some(p => p !== info && p.id === ev.id)) { peers.delete(url); req.destroy(); return; }
          info.id = ev.id; info.machine = ev.machine;
          console.log(`  ${ev.machine} 연결됨 (${url})`); sse(clients, hello());
        } else if (ev.type === 'usage') addUsageRec(ev, false);
        else send(ev, true);
      }
    });
    res.on('end', () => drop(url, info));
  });
  req.on('error', () => drop(url, info));
  req.setTimeout(60e3, () => req.destroy());   // 20초마다 ping이 오니 1분 조용하면 끊긴 것
}
function drop(url, info) {
  const p = peers.get(url); if (!p || p !== info) return;
  peers.delete(url);
  if (p.machine) { console.log(`  ${p.machine} 연결 끊김`); sse(clients, hello()); }
}
// 같은 와이파이에 "나 여기 있어" 알리기 / 듣기
const disco = dgram.createSocket({ type: 'udp4', reuseAddr: true });
disco.on('message', (msg, rinfo) => {
  let m; try { m = JSON.parse(msg); } catch (e) { return; }
  if (m.camp === 'kydz' && m.id !== ME && m.port) connectPeer(`http://${rinfo.address}:${m.port}`);
});
disco.on('error', () => {});
disco.bind(DISCO_PORT, () => {
  try { disco.setBroadcast(true); } catch (e) {}
  const shout = () => {
    const msg = Buffer.from(JSON.stringify({ camp: 'kydz', id: ME, port: PORT, machine: MACHINE }));
    // 255.255.255.255 + 네트워크별 브로드캐스트 주소 (윈도우는 한쪽으로만 나가는 경우가 있어서)
    const addrs = new Set(['255.255.255.255']);
    for (const i of Object.values(os.networkInterfaces()).flat()) {
      if (!i || i.family !== 'IPv4' || i.internal) continue;
      const a = i.address.split('.').map(Number), n = i.netmask.split('.').map(Number);
      addrs.add(a.map((x, k) => (x & n[k]) | (~n[k] & 255)).join('.'));
    }
    for (const a of addrs) disco.send(msg, DISCO_PORT, a, () => {});
  };
  shout(); setInterval(shout, 5000);
});
const manual = (process.env.CAMP_PEERS || '').split(',').map(s => s.trim().replace(/\/$/, '')).filter(Boolean);
if (manual.length) { const tryAll = () => manual.forEach(connectPeer); tryAll(); setInterval(tryAll, 10e3); }
