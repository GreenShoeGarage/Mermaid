/* Build-time-only recovery of installed Mermaid ES modules into a standalone
   registry bundle. No Gradio application code or network behavior is retained. */
const ts = require(process.env.TYPESCRIPT_PATH || 'typescript');
const fs = require('fs'); const path = require('path');
const from = process.argv[2];
if (!from) throw new Error('Usage: node scripts/prepare-local-vendor.cjs /path/to/gradio-6.5.1/frontend/assets');
const root = path.resolve(__dirname, '..');
const entry = 'mermaid.core-nQedeAL4.js';
const files = new Map();
const shims = {
 'index-B5Zu_GVg.js':'export const _ = (loader) => loader();',
 'i18n-B4hKvn1K.js':'export function k(e){return e&&e.__esModule&&Object.prototype.hasOwnProperty.call(e,"default")?e.default:e;}'
};
function visit(name) {
 if (files.has(name)) return;
 let text = shims[name] ?? fs.readFileSync(path.join(from,name),'utf8');
 text = text.replace(/import\s*["']\.\/svelte\/[^"']+["'];?/g,'');
 // Only native MathML is used; URL resolves to the local app, never a CDN.
 text = text.replace(/import\.meta\.url/g,'globalThis.location.href');
 files.set(name,text);
 const ast = ts.createSourceFile(name,text,ts.ScriptTarget.Latest,true,ts.ScriptKind.JS);
 function walk(n) {
   let dep;
   if ((ts.isImportDeclaration(n)||ts.isExportDeclaration(n)) && n.moduleSpecifier && ts.isStringLiteral(n.moduleSpecifier)) dep=n.moduleSpecifier.text;
   if (ts.isCallExpression(n) && n.expression.kind===ts.SyntaxKind.ImportKeyword && ts.isStringLiteral(n.arguments[0])) dep=n.arguments[0].text;
   if(dep) {
    if (!dep.startsWith('.')) throw new Error('Unexpected dependency '+dep);
    visit(path.posix.normalize(path.posix.join(path.posix.dirname(name),dep)));
   }
   ts.forEachChild(n,walk);
 }
 walk(ast);
}
visit(entry);
let out='/*! Mermaid 11.12.2 and dependencies. MIT and third-party licenses in /licenses. */\n(function(global){"use strict"; const factories = Object.create(null), cache = Object.create(null);\n';
for(const [name,source] of files){
 const code=ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022,removeComments:false}}).outputText;
 out+='factories['+JSON.stringify(name)+']=function(module,exports,require){\n'+code+'\n};\n';
}
out+=`function load(name) { if(cache[name]) return cache[name].exports; if(!factories[name]) throw new Error('Missing bundled module: '+name); const module={exports:{}}; cache[name]=module; const local=(dep)=>{const parts=name.split('/');parts.pop();for(const p of dep.split('/')){if(p==='.'||!p)continue;if(p==='..')parts.pop();else parts.push(p)}return load(parts.join('/'))}; factories[name](module,module.exports,local); return module.exports; }\nglobal.mermaid=load(${JSON.stringify(entry)}).b5.default; global.MERMAID_VERSION=load(${JSON.stringify(entry)}).K.version;\n})(globalThis);\n`;
fs.writeFileSync(path.join(root,'vendor/mermaid.bundle.js'),out);
fs.writeFileSync(path.join(root,'vendor/provenance.json'),JSON.stringify({mermaid:'11.12.2',source:'Installed Gradio 6.5.1 frontend distribution; upstream Mermaid.js',modules:[...files.keys()],changes:['Replace Vite preload helper with a direct local loader','Strip unrelated Svelte side-effect imports','Keep only the commonJS default-export helper from shared i18n module','Transpile ESM to local registry with TypeScript ES2022; no external imports','Resolve import.meta.url locally; use native MathML without font downloads']},null,2));
console.log('Bundled',files.size,'modules,',out.length,'bytes');
