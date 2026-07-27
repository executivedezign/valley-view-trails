const C='vvtrails-v3',F=['.','index.html','map.enc','manifest.json'];
self.addEventListener('install',e=>{self.skipWaiting();
  e.waitUntil(caches.open(C).then(c=>c.addAll(F)).catch(()=>{}))});
self.addEventListener('activate',e=>{e.waitUntil(Promise.all([clients.claim(),
  caches.keys().then(k=>Promise.all(k.filter(x=>x!==C).map(x=>caches.delete(x))))]))});

/* The app shell must be network-first, or a published update never reaches a
   phone that already installed the old one. The encrypted map is large and
   changes rarely, so it stays cache-first. Both fall back to the other side
   when offline, which is the normal state out on the trail. */
function isShell(req,u){
  return req.mode==='navigate' || u.pathname.endsWith('/') ||
         /\.(html|json|js)$/.test(u.pathname);
}
self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET') return;
  const u=new URL(e.request.url);
  if(u.origin!==location.origin) return;
  if(isShell(e.request,u)){
    e.respondWith(fetch(e.request).then(n=>{
      const cp=n.clone(); caches.open(C).then(c=>c.put(e.request,cp)); return n;
    }).catch(()=>caches.match(e.request,{ignoreSearch:true})
      .then(r=>r||caches.match('index.html'))));
  }else{
    e.respondWith(caches.match(e.request,{ignoreSearch:true}).then(r=>r||
      fetch(e.request).then(n=>{
        const cp=n.clone(); caches.open(C).then(c=>c.put(e.request,cp)); return n;
      })));
  }
});
