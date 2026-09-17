/* Same-scope, versioned application cache. Never caches user diagrams or exports. */
'use strict';
const PREFIX='gsg-mermaid-workbench:'+new URL(self.registration.scope).pathname+':';
const CACHE=PREFIX+'1.0.0';
const FILES=['./','index.html','renderer.html','manifest.webmanifest','assets/app.css','assets/icon.svg','assets/icon-192.png','assets/icon-512.png','vendor/codemirror.js','vendor/codemirror-addons.js','vendor/codemirror.css','vendor/jszip.min.js','vendor/mermaid.bundle.js','src/core.js','src/templates.js','src/app.js','src/renderer.js'];
const URLS=new Set(FILES.map(file=>new URL(file,self.registration.scope).href));
self.addEventListener('install',event=>event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(FILES.map(file=>new Request(new URL(file,self.registration.scope),{cache:'reload'}))))));
self.addEventListener('activate',event=>event.waitUntil((async()=>{for(const key of await caches.keys())if(key.startsWith(PREFIX)&&key!==CACHE)await caches.delete(key);await self.clients.claim()})()));
self.addEventListener('fetch',event=>{if(event.request.method!=='GET'||!URLS.has(event.request.url))return;event.respondWith(caches.open(CACHE).then(async cache=>(await cache.match(event.request))||fetch(event.request)));});
