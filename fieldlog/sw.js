const C='fieldlog-v1',F=['.','index.html','manifest.json',
  'icon-180.png','icon-192.png','icon-512.png','favicon-32.png'];
self.addEventListener('install',e=>{self.skipWaiting();
  e.waitUntil(caches.open(C).then(c=>c.addAll(F)).catch(()=>{}))});
self.addEventListener('activate',e=>{e.waitUntil(Promise.all([clients.claim(),
  caches.keys().then(k=>Promise.all(k.filter(x=>x!==C).map(x=>caches.delete(x))))]))});

/* Network-first so a published update reaches an installed app, cache as the
   fallback. The log itself lives in IndexedDB, not here; this only keeps the
   app shell available out of signal. The weather lookup is cross-origin and
   passes straight through. */
self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET') return;
  const u=new URL(e.request.url);
  if(u.origin!==location.origin) return;
  e.respondWith(fetch(e.request).then(n=>{
    const cp=n.clone(); caches.open(C).then(c=>c.put(e.request,cp)); return n;
  }).catch(()=>caches.match(e.request,{ignoreSearch:true})
    .then(r=>r||caches.match('index.html'))));
});
