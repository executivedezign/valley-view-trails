const C='camwx-v1',F=['.','index.html','manifest.json'];
self.addEventListener('install',e=>{self.skipWaiting();
  e.waitUntil(caches.open(C).then(c=>c.addAll(F)).catch(()=>{}))});
self.addEventListener('activate',e=>{e.waitUntil(Promise.all([clients.claim(),
  caches.keys().then(k=>Promise.all(k.filter(x=>x!==C).map(x=>caches.delete(x))))]))});

/* Network-first on the shell so a published update actually reaches a phone
   that already installed the app. Weather itself is cross-origin and is left
   alone deliberately — a cached forecast is worse than no forecast, and the
   page already keeps the last reading in localStorage to show while loading. */
self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET') return;
  const u=new URL(e.request.url);
  if(u.origin!==location.origin) return;
  e.respondWith(fetch(e.request).then(n=>{
    const cp=n.clone(); caches.open(C).then(c=>c.put(e.request,cp)); return n;
  }).catch(()=>caches.match(e.request,{ignoreSearch:true})
    .then(r=>r||caches.match('index.html'))));
});
