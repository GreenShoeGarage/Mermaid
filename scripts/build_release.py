#!/usr/bin/env python3
"""Build a self-contained offline HTML edition from the checked-in static app.
Python 3.9+ standard library only. Runtime use and static hosting need no build.
"""
from pathlib import Path
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[1]
def inline_script(match):
    path=ROOT/match.group(1)
    code=path.read_text(encoding='utf-8').replace('</script','<\\/script').replace('</SCRIPT','<\\/SCRIPT')
    return '<script>\n'+code+'\n</script>'
def main():
    renderer=(ROOT/'renderer.html').read_text()
    renderer=re.sub(r'<script src="([^"]+)"></script>',inline_script,renderer)
    html=(ROOT/'index.html').read_text()
    html=html.replace('<link rel="manifest" href="manifest.webmanifest">','')
    html=re.sub(r'<link rel="icon"[^>]+>','',html)
    html=re.sub(r'<link rel="stylesheet" href="([^"]+)">',lambda m:'<style>\n'+(ROOT/m.group(1)).read_text()+'\n</style>',html)
    env='<script>globalThis.MERMAID_PORTABLE=true;globalThis.MERMAID_RENDERER_HTML='+json.dumps(renderer,ensure_ascii=False).replace('<','\\u003c')+';</script>\n'
    html=html.replace('<script src="vendor/codemirror.js"></script>',env+'<script src="vendor/codemirror.js"></script>')
    html=re.sub(r'<script src="([^"]+)"></script>',inline_script,html)
    notices=(ROOT/'licenses/THIRD-PARTY-NOTICES.txt').read_text(encoding='utf-8')
    html=html.rsplit('</body>',1)[0]+'<script type="text/plain" id="third-party-notices">'+notices.replace('</script','<\\/script')+'</script>\n</body>'+html.rsplit('</body>',1)[1]
    out=ROOT/'MERMAID-Workbench-v1.0.0.html'
    out.write_text(html,encoding='utf-8')
    print(f'Built {out.name}: {out.stat().st_size:,} bytes')
    hashes={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.rglob('*') if p.is_file() and p.name not in {'checksums.json'} and 'tests' not in p.parts and '.git' not in p.parts}
    (ROOT/'checksums.json').write_text(json.dumps(hashes,indent=2)+'\n')
if __name__=='__main__':main()
