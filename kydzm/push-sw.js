// 운영판 크롬 알림 (사용자 요청 261105) — Claude가 운영판을 바꾸면 cupas board-notify 액션이 웹 푸시를 보냄
// 내용은 브라우저까지 암호화돼서 옴(Web Push). 눌러서 운영판 열기.
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));

self.addEventListener('push', e => {
  let d = {};
  try { d = e.data ? e.data.json() : {}; } catch (_) { d = { body: e.data ? e.data.text() : '' }; }
  e.waitUntil(self.registration.showNotification(d.title || '운영판', {
    body: d.body || '',
    tag: d.tag || 'board',
    renotify: true,
    data: { url: d.url || '/kydzm/board.html' },
  }));
});

self.addEventListener('notificationclick', e => {
  e.notification.close();
  const url = new URL((e.notification.data && e.notification.data.url) || '/kydzm/board.html', self.location.origin).href;
  e.waitUntil(self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then(cs => {
    for (const c of cs) if (c.url.split('?')[0] === url.split('?')[0] && 'focus' in c) return c.focus();
    return self.clients.openWindow(url);
  }));
});
