#!/usr/bin/env python3
"""Portable UI regression suite. Requires Python Playwright + Chromium.
Runs from an about:blank document with explicit localStorage and download shims.
These shims test storage logic, not actual origin persistence or OS save dialogs.
No enterprise browser policies are modified. No network is required by the app.
Set CHROMIUM to an installed Chromium path, or leave unset for Playwright's browser.
"""
from pathlib import Path
import json, os, base64, time
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT/'MERMAID-Workbench-v1.0.0.html').read_text()
RESULTS=[]
SHIM = r'''<script>
const testStore=SEED;
Object.defineProperty(window,'localStorage',{value:{getItem:k=>testStore[k]??null,setItem:(k,v)=>{testStore[k]=String(v)},removeItem:k=>delete testStore[k],clear:()=>Object.keys(testStore).forEach(k=>delete testStore[k]),key:i=>Object.keys(testStore)[i]||null,get length(){return Object.keys(testStore).length}}});
globalThis.TEST_STORE=testStore;
globalThis.TEST_DOWNLOADS=[];globalThis.TEST_BLOBS=new Map();
const originalCreateURL=URL.createObjectURL.bind(URL);URL.createObjectURL=b=>{const u=originalCreateURL(b);TEST_BLOBS.set(u,b);return u};
HTMLAnchorElement.prototype.click=function(){if(this.download)TEST_DOWNLOADS.push({name:this.download,blob:TEST_BLOBS.get(this.href)})};
</script>'''

def check(name, condition=True):
    assert condition, name
    RESULTS.append({'test':name,'result':'pass'})
    print('PASS',name,flush=True)

def prepared(seed=None):
    return HTML.replace('<head>','<head>'+SHIM.replace('SEED',json.dumps(seed or {})).replace('</script>','</script>'),1)

def wait(p, expression, timeout=10000):
    end=time.monotonic()+timeout/1000
    while time.monotonic()<end:
        if p.evaluate(expression):return
        p.wait_for_timeout(50)
    raise AssertionError('Timed out: '+expression)

def valid(p):
    wait(p,"MERMAID_WORKBENCH.currentPreview && MERMAID_WORKBENCH.currentPreview.source===MERMAID_WORKBENCH.workspace.docs.find(d=>d.id===MERMAID_WORKBENCH.workspace.active).source && document.querySelector('#render-badge').textContent==='Valid'",timeout=10000)

def source(p,text):
    p.evaluate("s=>document.querySelector('.CodeMirror').CodeMirror.setValue(s)",text)

def active(p):
    return p.evaluate("MERMAID_WORKBENCH.workspace.docs.find(d=>d.id===MERMAID_WORKBENCH.workspace.active)")

def close(p):
    if p.locator('#modal').evaluate('(e)=>e.open'):p.locator('#modal [data-action=close-modal]').first.click()

def launchpage(b,seed=None,size=None,emulate_storage=True):
    p=b.new_page(viewport=size or {'width':1512,'height':982})
    p.set_default_timeout(5000)
    p.set_content(prepared(seed) if emulate_storage else HTML,wait_until='load',timeout=20000)
    return p

with sync_playwright() as pw:
    kwargs={'headless':True,'args':['--no-sandbox']}
    if os.environ.get('CHROMIUM'):kwargs['executable_path']=os.environ['CHROMIUM']
    b=pw.chromium.launch(**kwargs)
    p=launchpage(b);errors=[];requests=[]
    p.on('pageerror',lambda e: errors.append(str(e)))
    p.on('request',lambda r: requests.append(r.url))
    try:
        valid(p);p.wait_for_timeout(800)
        check('initial source renders in isolated iframe',p.locator('#diagram-image').evaluate('(e)=>e.naturalWidth>0'))
        check('initial autosave reaches saved state',p.locator('#save-state').inner_text()=='Saved locally')
        check('renderer sandbox lacks same-origin permission',p.locator('#renderer-host iframe').get_attribute('sandbox')=='allow-scripts')
        p.screenshot(path=str(ROOT/'docs/workbench-desktop.png'),full_page=True)
        p.click('[data-action=templates]');check('24 template choices',p.locator('.template-card').count()==24)
        p.fill('#template-search','sequence');check('template search narrows choices',p.locator('.template-card').count()>=1 and p.locator('.template-card').count()<24);p.fill('#template-search','')
        p.screenshot(path=str(ROOT/'docs/templates.png'));close(p)
        original=active(p)['source']
        source(p,'flowchart TD\n    A["Broken" --> B');wait(p,'MERMAID_WORKBENCH.lastError !== null')
        check('syntax error preserves last valid preview',p.evaluate('MERMAID_WORKBENCH.currentPreview.source')==original)
        check('syntax error is visible with last-valid warning',p.locator('#problems').is_visible() and p.locator('#stale-banner').is_visible())
        p.screenshot(path=str(ROOT/'docs/error-recovery.png'))
        p.click('[data-action=export]');check('stale image exports blocked by default',p.locator('[data-action=export-svg]').is_disabled())
        p.check('#export-stale');p.click('[data-action=export-svg]')
        check('explicit stale SVG filename is marked',p.evaluate('TEST_DOWNLOADS.at(-1).name.endsWith("-last-valid.svg")'))
        check('stale SVG embeds correct prior source',p.evaluate("async()=>{const s=await TEST_DOWNLOADS.at(-1).blob.text();return JSON.parse(new DOMParser().parseFromString(s,'image/svg+xml').querySelector('metadata').textContent).source}")==original)
        close(p);source(p,original);valid(p);check('correcting source clears error',p.evaluate('MERMAID_WORKBENCH.lastError===null'))
        p.click('label.live-toggle');source(p,'flowchart LR\n A["Manual"] --> B["Render"]');p.wait_for_timeout(600)
        check('manual mode does not render until requested',p.evaluate('MERMAID_WORKBENCH.currentPreview.source')==original)
        p.click('[data-action=render]');valid(p);p.click('label.live-toggle')
        p.click('[data-action=new]');p.wait_for_timeout(100);p.fill('#document-title','Regression diagram');source(p,'flowchart LR\n    A["First"] --> B["Next"]');valid(p)
        check('new editable document created',len(p.evaluate('MERMAID_WORKBENCH.workspace.docs'))==4)
        p.click('[data-action=inspector]');p.fill('#node-label','Say "hello"');p.select_option('#node-shape','decision');p.click('[data-action=add-node]');valid(p)
        check('guided node writes valid escaped source','N1{"Say #quot;hello#quot;"}' in active(p)['source'])
        p.select_option('#edge-from','B');p.select_option('#edge-to','N1');p.fill('#edge-label','Yes');p.click('[data-action=add-edge]');valid(p)
        check('guided connection changes source','B -->|Yes| N1' in active(p)['source'])
        p.click('[data-inspector=history]');p.fill('#snapshot-name','Known good');p.click('[data-action=snapshot]')
        snap=active(p)['snapshots'][-1];p.locator(f'[data-baseline="{snap["id"]}"]').click()
        check('named snapshot can become baseline',active(p)['baseline']==snap['id'])
        source(p,active(p)['source']+'\n    N1 --> C["A change"]');valid(p)
        p.locator(f'[data-compare="{snap["id"]}"]').click();check('comparison contains added source',p.locator('.diff-line.add').count()>0);close(p)
        p.locator(f'#inspector [data-restore="{snap["id"]}"]').click();valid(p)
        check('restore preserves prior version in snapshot',active(p)['source']==snap['source'] and active(p)['snapshots'][-1]['title'].startswith('Before restoring'))
        p.click('[data-action=mode]');p.click('[data-inspector=notes]')
        p.fill('#doc-notes','These are test notes.');p.fill('#doc-assumptions','A1: Sample context.');p.fill('#doc-evidence','E1: A test record.');p.fill('#doc-tags','test, draft');p.fill('#finding-text','Test finding');p.select_option('#finding-severity','high');p.select_option('#finding-confidence','low');p.click('[data-action=add-finding]')
        check('advanced registers and findings stored',active(p)['findings'][0]['severity']=='high' and active(p)['evidence']=='E1: A test record.')
        p.click('[data-finding-status]');check('finding can be resolved',active(p)['findings'][0]['status']=='resolved')
        p.click('[data-inspector=appearance]');p.select_option('#diagram-look','handDrawn');valid(p)
        p.select_option('#inspector-theme','night');valid(p);check('appearance changes render',p.evaluate('MERMAID_WORKBENCH.currentPreview.visual.theme')=='night')
        p.fill('#advanced-config','{"securityLevel":"loose"}');p.click('[data-action=apply-config]');wait(p,'MERMAID_WORKBENCH.lastError !== null')
        check('unsupported security override rejected','Unsupported configuration key' in p.evaluate('MERMAID_WORKBENCH.lastError.message'))
        p.click('[data-action=reset-config]');valid(p);p.select_option('#inspector-theme','paper');p.select_option('#diagram-look','classic');valid(p)
        p.screenshot(path=str(ROOT/'docs/inspector.png'))
        svg=p.evaluate('MERMAID_WORKBENCH.exportSVG(MERMAID_WORKBENCH.currentPreview,false,true)')
        check('SVG export contains editable metadata','gsg-mermaid-source' in svg and 'viewBox' in svg)
        check('quoted labels are rendered as characters, not entity names',p.evaluate("new DOMParser().parseFromString(MERMAID_WORKBENCH.currentPreview.svg,'image/svg+xml').documentElement.textContent.includes('Say \"hello\"')"))
        data=p.evaluate('''async()=>{const b=await MERMAID_WORKBENCH.exportPNG(MERMAID_WORKBENCH.currentPreview,2,false);const a=new Uint8Array(await b.arrayBuffer());return {signature:Array.from(a.slice(0,8)),base64:btoa(String.fromCharCode(...a))}}''')
        check('PNG export is actual raster image',data['signature']==[137,80,78,71,13,10,26,10])
        (ROOT/'tests/export-test.png').write_bytes(base64.b64decode(data['base64']))
        check('PNG safety limit rejects oversize canvas',p.evaluate('''async()=>{try{await MERMAID_WORKBENCH.exportPNG({...MERMAID_WORKBENCH.currentPreview,width:100000},4);return false}catch(e){return /safe canvas limit/.test(e.message)}}'''))
        report=p.evaluate('MERMAID_WORKBENCH.exportReport(MERMAID_WORKBENCH.workspace.docs.find(d=>d.id===MERMAID_WORKBENCH.workspace.active),true)')
        check('standalone report carries context and source',all(x in report for x in ['Assumptions register','Evidence register','high severity','low confidence','Current editable source','Baseline comparison']))
        rp=b.new_page();rp.set_content(report);check('report embedded image decodes',rp.locator('.report-diagram').evaluate('(e)=>e.decode().then(()=>e.naturalWidth>0)'));rp.close()
        p.click('#inspector [data-action=inspector]')
        p.click('[data-action=export]')
        for action,extension in [('export-source','.mmd'),('export-markdown','.md'),('export-document','.json'),('export-html','.html')]:
            p.click(f'[data-action={action}]');check(action+' prepares a download',p.evaluate(f'TEST_DOWNLOADS.at(-1).name.endsWith("{extension}")'))
        p.click('[data-action=workspace-zip]');wait(p,'TEST_DOWNLOADS.at(-1).name.endsWith(".zip")')
        ziptest=p.evaluate('''async()=>{const z=await JSZip.loadAsync(await TEST_DOWNLOADS.at(-1).blob.arrayBuffer());const w=JSON.parse(await z.file('workspace.json').async('string'));return {docs:w.docs.length,sources:Object.keys(z.files).filter(x=>x.endsWith('.mmd')).length}}''')
        check('workspace ZIP contains backup and every source',ziptest['docs']==ziptest['sources']==4)
        p.click('[data-action=copy-source]');check('clipboard fallback offers exact editable source',p.locator('#copy-fallback').input_value()==active(p)['source']);close(p)
        # Import exported editable SVG as a non-destructive copy.
        before=len(p.evaluate('MERMAID_WORKBENCH.workspace.docs'))
        p.set_input_files('#file-input',{'name':'round-trip.svg','mimeType':'image/svg+xml','buffer':svg.encode()});wait(p,f'MERMAID_WORKBENCH.workspace.docs.length==={before+1}');valid(p)
        check('SVG embedded-source import round trips without replacing documents',len(p.evaluate('MERMAID_WORKBENCH.workspace.docs'))==before+1 and active(p)['source']==snap['source'])
        p.set_input_files('#file-input',{'name':'two.md','mimeType':'text/markdown','buffer':b'# One\n```mermaid\nflowchart TD\nA-->B\n```\n# Two\n```mermaid\nsequenceDiagram\nA->>B: Hello\n```'});wait(p,'MERMAID_WORKBENCH.workspace.docs.length===7');valid(p)
        check('Markdown import extracts two diagrams',len(p.evaluate('MERMAID_WORKBENCH.workspace.docs'))==7)
        p.set_input_files('#file-input',{'name':'bad.json','mimeType':'application/json','buffer':b'{bad'});p.wait_for_selector('#modal[open]')
        check('invalid import leaves existing documents intact',len(p.evaluate('MERMAID_WORKBENCH.workspace.docs'))==7);close(p)
        p.click('[data-action=document-menu]');p.click('#context-menu [data-action=duplicate]');valid(p)
        check('duplicate creates independent document',len(p.evaluate('MERMAID_WORKBENCH.workspace.docs'))==8)
        p.click('[data-action=document-menu]');p.click('#context-menu [data-action=delete-doc]');p.click('[data-delete-confirm]')
        check('confirmed delete removes only selected diagram',len(p.evaluate('MERMAID_WORKBENCH.workspace.docs'))==7)
        p.click('#toast [data-action=undo-delete]');valid(p);check('session undo restores deleted document',len(p.evaluate('MERMAID_WORKBENCH.workspace.docs'))==8)
        p.evaluate('MERMAID_WORKBENCH.save()');p.wait_for_timeout(700)
        seed=p.evaluate('TEST_STORE');reloaded=launchpage(b,seed);valid(reloaded)
        check('stored JSON rehydrates documents and settings',len(reloaded.evaluate('MERMAID_WORKBENCH.workspace.docs'))==8 and reloaded.evaluate('MERMAID_WORKBENCH.workspace.settings.mode')=='advanced');reloaded.close()
        # Force quota error; then restore the backend and ensure a retry clears alert.
        p.evaluate("()=>{globalThis.TEST_SET=localStorage.setItem;localStorage.setItem=()=>{throw new DOMException('quota','QuotaExceededError')}}")
        p.fill('#document-title','Quota test');check('quota failure returns false',p.evaluate('MERMAID_WORKBENCH.save()') is False)
        check('quota failure keeps work and displays backup warning',p.locator('#global-alert').is_visible() and active(p)['title']=='Quota test')
        p.evaluate('localStorage.setItem=TEST_SET;MERMAID_WORKBENCH.save()');check('retry succeeds and clears stale save warning',p.locator('#global-alert').is_hidden())
        # Simulate external tab revision; no lost changes are allowed.
        p.evaluate("(()=>{const w=MERMAID_WORKBENCH.workspace;w.revision='other-tab';w.docs[0].title='Other tab edit';const value=JSON.stringify(w);localStorage.setItem('gsg-mermaid-workbench-v1',value);dispatchEvent(new StorageEvent('storage',{key:'gsg-mermaid-workbench-v1',newValue:value}));})()")
        check('cross-tab update pauses saves',p.locator('#save-state').inner_text()=='Save conflict')
        p.click('[data-action=conflict]');p.click('[data-action=conflict-merge]');valid(p)
        check('conflict merge retains both sets',len(p.evaluate('MERMAID_WORKBENCH.workspace.docs'))==16)
        # Workspace import is explicit and starts in non-destructive selection dialog.
        backup=p.evaluate('JSON.stringify(MERMAID_WORKBENCH.workspace)')
        p.set_input_files('#file-input',{'name':'workspace.json','mimeType':'application/json','buffer':backup.encode()});p.wait_for_selector('#modal[open]')
        check('workspace import waits for user choice',p.locator('[data-action=import-merge]').is_visible() and len(p.evaluate('MERMAID_WORKBENCH.workspace.docs'))==16)
        p.click('[data-action=import-replace-confirm]');p.click('[data-action=import-replace]');valid(p)
        check('explicit workspace restore succeeds',len(p.evaluate('MERMAID_WORKBENCH.workspace.docs'))==16)
        # UI presentation and themes.
        p.click('[data-action=theme]');check('light UI theme applied',p.locator('html').get_attribute('data-theme')=='light');p.screenshot(path=str(ROOT/'docs/workbench-light.png'))
        p.click('[data-action=theme]');check('high-contrast UI theme applied',p.locator('html').get_attribute('data-theme')=='contrast');p.screenshot(path=str(ROOT/'docs/workbench-contrast.png'))
        p.click('[data-action=theme]');p.click('[data-action=present]');check('presentation mode opens',p.locator('#app').evaluate('(e)=>e.classList.contains("presenting")'));p.keyboard.press('Escape')
        p.click('[data-action=settings]');p.click('[data-action=fresh-start]');check('Fresh Start requires typed confirmation',p.locator('#reset-execute').is_disabled())
        p.fill('#reset-confirm','RESET');p.click('#reset-execute');check('Fresh Start is truly empty',p.evaluate('MERMAID_WORKBENCH.workspace.docs.length')==0 and p.locator('#document-title').is_disabled())
        p.click('[data-action=new]');valid(p);check('creating after Fresh Start works',p.evaluate('MERMAID_WORKBENCH.workspace.docs.length')==1)
        check('main page has no uncaught runtime errors',not errors)
        check('no HTTP runtime requests observed',not [r for r in requests if r.startswith(('http:','https:'))])
        p.close()
        # Actual storage-denial path: no shim.
        denied=launchpage(b,emulate_storage=False);valid(denied)
        check('storage denial does not stop rendering',denied.locator('#global-alert').is_visible() and 'export JSON before closing' in denied.locator('#global-alert').inner_text())
        denied.close()
        # A corrupted saved JSON is not overwritten by startup autosave.
        corrupt=launchpage(b,{'gsg-mermaid-workbench-v1':'{corrupt'});valid(corrupt)
        check('corrupt stored payload remains recoverable',corrupt.evaluate('TEST_STORE["gsg-mermaid-workbench-v1"]')=='{corrupt' and corrupt.locator('[data-action=recover-storage]').is_visible());corrupt.close()
        mobile=launchpage(b,size={'width':390,'height':844});valid(mobile)
        check('mobile viewport has no horizontal page overflow',mobile.evaluate('document.documentElement.scrollWidth<=innerWidth'))
        check('mobile opens on source with preview tab',mobile.locator('#source-region').is_visible() and mobile.locator('[data-action=mobile-preview]').is_visible())
        mobile.screenshot(path=str(ROOT/'docs/mobile-source.png'))
        mobile.click('[data-action=mobile-preview]');mobile.wait_for_timeout(100)
        check('mobile preview tab reveals readable diagram',mobile.locator('#canvas').is_visible() and mobile.locator('#source-region').is_hidden())
        mobile.screenshot(path=str(ROOT/'docs/mobile-preview.png'))
        mobile.click('[data-action=inspector]');check('mobile inspector fits viewport',mobile.locator('#inspector').bounding_box()['x']>=0);mobile.close()
    except Exception:
        if not p.is_closed():p.screenshot(path=str(ROOT/'tests/failure.png'),full_page=True)
        raise
    finally:
        (ROOT/'tests/browser-results.json').write_text(json.dumps({'environment':'Chromium / about:blank / explicit storage and download shims','tests':RESULTS,'uncaughtErrors':errors},indent=2))
        b.close()
print(f'{len(RESULTS)} browser assertions passed.')
