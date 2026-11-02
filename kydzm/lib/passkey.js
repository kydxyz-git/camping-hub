// 관리자 지문(패스키) 로그인 — 사용자 요청 261103
// 비밀번호를 한 번 친 뒤 '지문 등록'을 하면, 다음부터 로그인 화면에서 지문(또는 얼굴·화면 잠금)으로 들어간다. 비밀번호도 계속 된다.
// 서버가 없어서 비밀번호 확인과 같은 수준(브라우저 안 확인) — 이 기기 잠금을 한 번 더 확인하는 용도. 실제 보호는 이 기기에만 있는 GitHub 토큰.
// 쓰는 곳: index·board·threads·insights.html 로그인 화면. 저장: localStorage에 패스키 id만(비밀 아님).
(function () {
  const KEY = 'kydz_admin_passkey', SKIP = 'kydz_admin_passkey_skip', BAD = 'kydz_admin_passkey_bad';
  const ls = {
    get: k => { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: (k, v) => { try { localStorage.setItem(k, v); } catch (e) {} },
    del: k => { try { localStorage.removeItem(k); } catch (e) {} },
  };
  const rnd = n => crypto.getRandomValues(new Uint8Array(n));
  const b64u = buf => btoa(String.fromCharCode(...new Uint8Array(buf))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  const unb64u = s => { s = s.replace(/-/g, '+').replace(/_/g, '/'); s += '='.repeat((4 - s.length % 4) % 4); return Uint8Array.from(atob(s), c => c.charCodeAt(0)); };

  // 폰에서만 (PC는 지문 필요 없음, 사용자 결정 261103)
  const isPhone = () => /Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent) || (window.matchMedia && matchMedia('(pointer: coarse)').matches && !matchMedia('(hover: hover)').matches);
  let _sup = null;
  function supported() {
    if (!isPhone()) return Promise.resolve(false);
    if (_sup) return _sup;
    const ok = window.isSecureContext && location.hostname && window.PublicKeyCredential && navigator.credentials
      && PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable;
    _sup = ok ? PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable().catch(() => false) : Promise.resolve(false);
    return _sup;
  }
  const has = () => !!ls.get(KEY);

  async function register() {
    const cred = await navigator.credentials.create({ publicKey: {
      challenge: rnd(32),
      rp: { name: 'kydz.kr 관리자', id: location.hostname },
      user: { id: rnd(16), name: 'kydz-admin', displayName: '공대남자 관리자' },
      pubKeyCredParams: [{ type: 'public-key', alg: -7 }, { type: 'public-key', alg: -257 }],
      authenticatorSelection: { authenticatorAttachment: 'platform', userVerification: 'required', residentKey: 'preferred' },
      timeout: 60000, attestation: 'none',
    } });
    ls.set(KEY, b64u(cred.rawId)); ls.del(BAD); ls.del(SKIP);
    return true;
  }
  async function verify() {
    const id = ls.get(KEY);
    if (!id) return false;
    const a = await navigator.credentials.get({ publicKey: {
      challenge: rnd(32), rpId: location.hostname, userVerification: 'required', timeout: 60000,
      allowCredentials: [{ type: 'public-key', id: unb64u(id) }],
    } });
    // authenticatorData: rpIdHash(32바이트) 다음 1바이트가 flags — 0x04 = 지문·얼굴 등으로 본인 확인함
    return !!(a && a.response && (new Uint8Array(a.response.authenticatorData)[32] & 0x04));
  }

  // 로그인 화면에 '👆 지문으로 열기' 버튼 — 등록돼 있으면 화면이 뜰 때 한 번 바로 물어봄
  async function mountLogin(onOk) {
    if (isPhone() && !(await supported())) {   // 네이버 앱 같은 앱 안 브라우저는 지문(패스키)을 막아 둠 → 안내만
      const sub = document.getElementById('login-submit');
      if (sub && !document.getElementById('login-passkey-note')) {
        const n = document.createElement('div'); n.id = 'login-passkey-note';
        n.style.cssText = 'margin-top:10px;font-size:12.5px;line-height:1.5;color:#888;text-align:center';
        n.textContent = '👆 지문 로그인은 이 브라우저에서 안 돼요 — 크롬이나 삼성 인터넷에서 열면 쓸 수 있어요';
        (sub.parentElement && sub.parentElement.id !== 'login-screen' && sub.parentElement.children.length === 1 ? sub.parentElement : sub).insertAdjacentElement('afterend', n);
      }
      return;
    }
    if (!has() || !(await supported())) return;
    const submit = document.getElementById('login-submit');
    if (!submit || document.getElementById('login-passkey')) return;
    const btn = document.createElement('button');
    btn.id = 'login-passkey'; btn.type = 'button';
    btn.textContent = '👆 지문으로 열기';
    btn.style.cssText = 'display:block;width:100%;margin-top:10px;min-height:46px;border-radius:10px;border:0;background:#1a1a1a;color:#fff;font-size:16px;font-weight:700;cursor:pointer';
    const anchor = submit.parentElement && submit.parentElement.id !== 'login-screen' && submit.parentElement.children.length === 1 ? submit.parentElement : submit;
    anchor.insertAdjacentElement('afterend', btn);
    const pw = document.getElementById('login-password');
    if (pw) pw.placeholder = '또는 비밀번호';
    const go = async () => {
      btn.disabled = true;
      try {
        if (await verify()) { try { sessionStorage.setItem('kydz_admin_authed', '1'); } catch (e) {} onOk(); return; }
      } catch (e) {
        if (e && e.name !== 'NotAllowedError' && e.name !== 'AbortError') ls.set(BAD, '1');
      }
      btn.disabled = false;
    };
    btn.onclick = go;
    setTimeout(() => { if (pw) pw.blur(); go(); }, 150);   // 바로 물어봄 (브라우저가 막으면 버튼으로)
  }

  // 비밀번호로 들어온 뒤: 아직 등록 안 했으면 아래에 '지문 등록' 제안 (안 함을 누르면 다시 안 물음)
  async function offer() {
    if ((has() && !ls.get(BAD)) || ls.get(SKIP) || !(await supported())) return;
    if (document.getElementById('passkey-offer')) return;
    const box = document.createElement('div');
    box.id = 'passkey-offer';
    box.style.cssText = 'position:fixed;left:12px;right:12px;bottom:calc(12px + env(safe-area-inset-bottom));z-index:9999;max-width:420px;margin:0 auto;background:#1a1a1a;color:#fff;border-radius:14px;padding:14px;box-shadow:0 6px 24px rgba(0,0,0,.25);font-size:14px;line-height:1.45';
    box.innerHTML = `<div style="font-weight:700;margin-bottom:4px">👆 다음부터 지문으로 열까요?</div>
      <div style="opacity:.75;font-size:12.5px;margin-bottom:10px">이 기기에서만 · 비밀번호도 계속 쓸 수 있어요</div>
      <div style="display:flex;gap:8px"><button data-a="reg" style="flex:1;min-height:40px;border:0;border-radius:9px;background:#ffd400;color:#1a1a1a;font-weight:700;font-size:14px">지문 등록</button>
      <button data-a="later" style="min-height:40px;padding:0 12px;border:1px solid #555;border-radius:9px;background:none;color:#fff;font-size:13px">다음에</button>
      <button data-a="never" style="min-height:40px;padding:0 12px;border:1px solid #555;border-radius:9px;background:none;color:#fff;font-size:13px">안 함</button></div>`;
    box.onclick = async e => {
      const a = e.target.closest('button') && e.target.closest('button').dataset.a;
      if (!a) return;
      if (a === 'never') ls.set(SKIP, '1');
      if (a === 'reg') {
        try { await register(); box.innerHTML = '<div style="font-weight:700">✓ 등록했어요. 다음부터 지문으로 열려요.</div>'; setTimeout(() => box.remove(), 2200); }
        catch (err) { box.querySelector('div').textContent = '등록이 안 됐어요 (' + (err && err.name || '오류') + ') — 다시 눌러 보세요'; }
        return;
      }
      box.remove();
    };
    document.body.appendChild(box);
  }

  window.kydzPasskey = { supported, has, register, verify, mountLogin, offer, isPhone,
    forget() { ls.del(KEY); ls.del(SKIP); ls.del(BAD); } };
})();
