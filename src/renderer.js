/* Runs only inside a sandbox without same-origin access to the application. */
(()=>{'use strict';
const palette={
 paper:{theme:'base',background:'#f7f7f2',themeVariables:{primaryColor:'#e5eafa',primaryTextColor:'#24354e',primaryBorderColor:'#8596b1',lineColor:'#687981',secondaryColor:'#e8efdc',tertiaryColor:'#f3ead6',fontFamily:'Arial, sans-serif',fontSize:'16px'}},
 forest:{theme:'forest',background:'#f4f7ed'},
 ocean:{theme:'base',background:'#eef5fb',themeVariables:{primaryColor:'#d8eaf8',primaryTextColor:'#173c5c',primaryBorderColor:'#5c90b3',lineColor:'#477c9a',secondaryColor:'#dbf1ed',tertiaryColor:'#e8e1f8',fontFamily:'Arial, sans-serif'}},
 night:{theme:'dark',background:'#18212b'},
 mono:{theme:'neutral',background:'#ffffff'}
};
function checkObject(o,depth=0){if(depth>12)throw new Error('Configuration is nested too deeply.');if(!o||typeof o!=='object')return;for(const key of Object.keys(o)){if(['__proto__','constructor','prototype'].includes(key))throw new Error('Unsafe configuration key.');checkObject(o[key],depth+1);}}
function errorData(error){const message=String(error?.message||error||'Could not render this diagram.').slice(0,4500);const line=Number(error?.hash?.loc?.first_line)||Number(message.match(/(?:on |at )?line\s+(\d+)/i)?.[1])||null;return{message,line};}
function clean(svgText){
 if(svgText.includes('xlink:')&&!svgText.includes('xmlns:xlink='))svgText=svgText.replace('<svg ','<svg xmlns:xlink="http://www.w3.org/1999/xlink" ');
 const doc=new DOMParser().parseFromString(svgText,'image/svg+xml');const svg=doc.documentElement;
 if(svg.localName!=='svg')throw new Error('The renderer did not produce a valid SVG.');
 svg.querySelectorAll('script,iframe,object,embed,link,animate,set,animateTransform').forEach(n=>n.remove());
 for(const node of [svg,...svg.querySelectorAll('*')]){
  for(const attr of [...node.attributes]){
   const name=attr.name.toLowerCase(),value=attr.value.trim();
   const safeRaster=node.localName==='image'&&/^data:image\/(png|jpeg|gif|webp);base64,[A-Za-z0-9+/=]+$/.test(value)&&value.length<300000;
   if(name.startsWith('on')||(['href','xlink:href','src'].includes(name)&&!value.startsWith('#')&&!safeRaster)||((name==='style')&&/javascript:|@import|url\(\s*['"]?(?!#)/i.test(value)))node.removeAttribute(attr.name);
  }
 }
 // Only locally embedded raster icons survive. External images never load.
 svg.querySelectorAll('image').forEach(n=>{if(!n.getAttribute('href')&&!n.getAttribute('xlink:href'))n.remove()});
 svg.querySelectorAll('style').forEach(n=>{n.textContent=n.textContent.replace(/@import[^;]+;/gi,'').replace(/url\(\s*['"]?(?!#)[^)]*\)/gi,'none');});
 // Pure SVG text makes previews portable and PNG exports independent of HTML.
 for(const foreign of svg.querySelectorAll('foreignObject')){
  const tx=doc.createElementNS('http://www.w3.org/2000/svg','text');
  tx.setAttribute('x',String(Number(foreign.getAttribute('x')||0)+Number(foreign.getAttribute('width')||0)/2));
  tx.setAttribute('y',String(Number(foreign.getAttribute('y')||0)+Number(foreign.getAttribute('height')||0)/2));
  tx.setAttribute('text-anchor','middle');tx.setAttribute('dominant-baseline','middle');tx.setAttribute('font-family','Arial, sans-serif');tx.setAttribute('font-size','16');
  tx.textContent=foreign.textContent?.trim()||'';foreign.replaceWith(tx);
 }
 // Mermaid's strict SVG text path can leave one entity-encoding layer.
 // Decode character references into TEXT nodes only; never parse label markup.
 const textWalker=doc.createTreeWalker(svg,4),decoder=document.createElement('textarea');
 let textNode;while((textNode=textWalker.nextNode())){if(!textNode.parentElement?.closest('text,title,desc'))continue;textNode.nodeValue=textNode.nodeValue.replace(/&(?:#[0-9]+|#x[0-9a-f]+|[a-z][a-z0-9]+);/gi,entity=>{decoder.innerHTML=entity;return decoder.value;});}
 const vb=(svg.getAttribute('viewBox')||'').trim().split(/[ ,]+/).map(Number);
 let width=vb.length===4?vb[2]:parseFloat(svg.getAttribute('width'));
 let height=vb.length===4?vb[3]:parseFloat(svg.getAttribute('height'));
 if(!Number.isFinite(width)||width<=0)width=1000;if(!Number.isFinite(height)||height<=0)height=600;
 svg.setAttribute('xmlns','http://www.w3.org/2000/svg');svg.setAttribute('width',String(width));svg.setAttribute('height',String(height));
 if(vb.length!==4)svg.setAttribute('viewBox',`0 0 ${width} ${height}`);
 svg.style.maxWidth='none';svg.style.backgroundColor='transparent';
 return{svg:new XMLSerializer().serializeToString(svg),width,height};
}
async function render(job){
 const started=performance.now();
 try{
  if(typeof job.source!=='string'||job.source.length>120000)throw new Error('Source exceeds the 120,000-character safety limit.');
  if(!job.source.trim())throw new Error('The source is empty. Choose a template or start with “flowchart TD”.');
  const visual=job.visual||{},p=palette[visual.theme]||palette.paper;
  let advanced;try{advanced=JSON.parse(visual.config||'{}')}catch{throw new Error('Advanced configuration is not valid JSON. Open Appearance → Configuration to correct it.');}
  if(!advanced||Array.isArray(advanced)||typeof advanced!=='object')throw new Error('Advanced configuration must be a JSON object.');checkObject(advanced);
  const allowed=new Set(['themeVariables','flowchart','sequence','gantt','er','class','state','pie','journey','mindmap','timeline','quadrantChart','xyChart','gitGraph','packet','sankey','block','architecture','radar','treemap']);
  for(const key of Object.keys(advanced))if(!allowed.has(key))throw new Error('Unsupported configuration key: '+key+'. Security, layout-engine, and network settings are intentionally locked.');
  const config={...p,...advanced,themeVariables:{...p.themeVariables,...advanced.themeVariables,fontFamily:'Arial, sans-serif'},look:visual.look==='handDrawn'?'handDrawn':'classic',layout:'dagre',startOnLoad:false,securityLevel:'strict',suppressErrorRendering:true,maxTextSize:120000,maxEdges:1200,logLevel:5,htmlLabels:false,fontFamily:'Arial, sans-serif',legacyMathML:false,forceLegacyMathML:false,secure:['layout','secure','securityLevel','startOnLoad','maxTextSize','maxEdges','suppressErrorRendering','dompurifyConfig','fontFamily','htmlLabels','forceLegacyMathML','legacyMathML'],flowchart:{...advanced.flowchart,htmlLabels:false,useMaxWidth:false,curve:visual.curve||'basis'},sequence:{...advanced.sequence,useMaxWidth:false},er:{...advanced.er,useMaxWidth:false}};
  mermaid.initialize(config);
  const parsed=await mermaid.parse(job.source);
  const result=await mermaid.render('gsg_'+job.id.replace(/[^a-zA-Z0-9_]/g,'_'),job.source);
  const output=clean(result.svg);
  parent.postMessage({kind:'rendered',id:job.id,...output,type:parsed.diagramType,background:p.background,elapsed:Math.round(performance.now()-started)},'*');
 }catch(error){parent.postMessage({kind:'render-error',id:job.id,...errorData(error)},'*');}
 finally{document.querySelectorAll('body > div,body > svg').forEach(n=>n.remove());}
}
addEventListener('message',event=>{if(event.source!==parent||event.data?.kind!=='render'||typeof event.data.id!=='string')return;render(event.data);});
if(typeof mermaid!=='undefined'){mermaid.initialize({startOnLoad:false,securityLevel:'strict'});parent.postMessage({kind:'renderer-ready',version:globalThis.MERMAID_VERSION||'11.12.2'},'*');}
else parent.postMessage({kind:'renderer-failed',message:'Mermaid is missing. Keep the vendor folder beside index.html, or use the portable HTML edition.'},'*');
})();
