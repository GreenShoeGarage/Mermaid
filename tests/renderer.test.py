#!/usr/bin/env python3
"""Exercise the real vendored rendering engine; no CDN and no server required.
Requires Python Playwright. CHROMIUM may select an installed Chromium binary.
Tests use an about:blank harness, not a real hosted service-worker origin.
"""
from playwright.sync_api import sync_playwright
from pathlib import Path
import os,json
ROOT=Path(__file__).resolve().parents[1]
with sync_playwright() as pw:
    kwargs={'headless':True,'args':['--no-sandbox']}
    if os.environ.get('CHROMIUM'):kwargs['executable_path']=os.environ['CHROMIUM']
    browser=pw.chromium.launch(**kwargs)
    page=browser.new_page(viewport={'width':1440,'height':1000});errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content('<html><body></body></html>')
    for filename in ['vendor/mermaid.bundle.js','src/templates.js','src/renderer.js']:page.add_script_tag(content=(ROOT/filename).read_text())
    results=page.evaluate('''async()=>{
    const out=[];let counter=0;
    async function run(name,source,theme='paper',config='{}',expected='rendered'){
      const id='test_'+counter++;
      const r=await new Promise(resolve=>{const handle=e=>{if(e.data.id!==id||!['rendered','render-error'].includes(e.data.kind))return;removeEventListener('message',handle);clearTimeout(timer);resolve(e.data)};addEventListener('message',handle);const timer=setTimeout(()=>{removeEventListener('message',handle);resolve({kind:'timeout',message:'8 seconds elapsed'})},8000);postMessage({kind:'render',id,source,visual:{theme,look:'classic',curve:'basis',config}},'*')});
      let decodes=false,safe=true;
      if(r.kind==='rendered'){
        const doc=new DOMParser().parseFromString(r.svg,'image/svg+xml');safe=doc.documentElement.localName==='svg'&&!doc.querySelector('script,foreignObject,iframe,object');
        for(const el of doc.querySelectorAll('*'))for(const a of el.attributes){if(a.name.startsWith('on')||(['href','xlink:href','src'].includes(a.name)&&/^(https?:|javascript:)/i.test(a.value)))safe=false;}
        const url=URL.createObjectURL(new Blob([r.svg],{type:'image/svg+xml'}));const image=new Image();image.src=url;try{await image.decode();decodes=image.naturalWidth>0}catch{}URL.revokeObjectURL(url);
      }
      out.push({name,theme,kind:r.kind,expected,pass:r.kind===expected&&(r.kind!=='rendered'||(decodes&&safe)),width:r.width,height:r.height,elapsed:r.elapsed,message:r.message});return r;
    }
    for(const theme of ['paper','forest','ocean','night','mono'])for(const t of WORKBENCH_TEMPLATES)await run(t.id,t.source,theme);
    await run('invalid-source','flowchart TD\\n A["Broken" --> B','paper','{}','render-error');
    await run('oversize-source','a'.repeat(120001),'paper','{}','render-error');
    await run('unsafe-config','flowchart TD\\nA-->B','paper','{"securityLevel":"loose"}','render-error');
    await run('prototype-config','flowchart TD\\nA-->B','paper','{"__proto__":{"polluted":true}}','render-error');
    await run('unsafe-link','flowchart TD\\n A["Hello"]-->B["World"]\\nclick A "javascript:alert(1)"');
    await run('html-in-label','flowchart TD\\n A["<img src=x onerror=alert(1)>"]-->B["<script>alert(1)</script>"]');
    await run('source-security-directive','%%{init: {"securityLevel":"loose"}}%%\\nflowchart TD\\nA-->B\\nclick A "https://example.invalid"');
    await run('unicode-labels','flowchart LR\\nA["Café · ΔV · こんにちは"]-->B["مرحبا"]');
    await run('200-node-chain','flowchart TD\\n'+Array.from({length:199},(_,i)=>'N'+i+'["Step '+i+'"]-->N'+(i+1)).join('\\n'));
    return out;
    }''')
    (ROOT/'tests/renderer-results.json').write_text(json.dumps({'engine':'11.12.2','tests':results,'uncaughtErrors':errors},indent=2))
    failed=[r for r in results if not r['pass']]
    print('Renderer matrix:',len(results)-len(failed),'/',len(results),'passed. Errors:',errors)
    for r in failed:print(r)
    browser.close()
    assert not failed and not errors
