/* Offline shell: the app opens without data. Answers wait in a queue on the phone and are sent when a connection returns. */
const V = "salama-v4";
const SHELL = ["./", "index.html", "config.js", "manifest.webmanifest", "icon.svg", "lang.js", "lang_sw.js", "portal.html", "qrcode.js"];
self.addEventListener("install", e => { e.waitUntil(caches.open(V).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener("fetch", e => {
  const u = new URL(e.request.url);
  if (e.request.method !== "GET" || u.origin !== location.origin) return;                // never touch database calls
  if (u.pathname.endsWith("content.json")) return;                                       // living content is always fetched fresh
  e.respondWith(fetch(e.request).then(r => { const c = r.clone(); caches.open(V).then(x => x.put(e.request, c)); return r; }).catch(() => caches.match(e.request).then(m => m || caches.match("index.html"))));
});
