const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1200,height:800}});
const bad=[],errs=[];p.on('response',r=>{if(r.status()>=400)bad.push(r.status()+' '+r.url())});p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
await p.goto('http://localhost:8765/_t.html');await p.waitForTimeout(1500);
const r=await p.evaluate(()=>{const o={books:STORIES.length,pages:0,noNarr:[],narrMismatch:[],noGloss:[],glossShort:[],noClip:[],actNoPlate:[],keysNoRegion:[]};
 const forms=new Set();
 STORIES.forEach((st,s)=>st.pages.forEach((pg,pi)=>{o.pages++;const key=st.id+':'+pi;if(!NARR[key])o.noNarr.push(key);
   for(const m of pg.matchAll(RX)){forms.add(m[1].toLowerCase());const g=GLOSS[m[2]];if(!g)o.noGloss.push(m[2]);else if(g.length<6||g.some(x=>!x))o.glossShort.push(m[2])}}));
 for(const f of forms)if(!WCLIP[f.trim()])o.noClip.push(f);
 o.noGloss=[...new Set(o.noGloss)];o.glossShort=[...new Set(o.glossShort)];
 o.actKeys=Object.keys(ACT).length;return o});
// narration element count check and region check per page
const r2=await p.evaluate(async()=>{const mm=[],nr=[];for(let s=0;s<STORIES.length;s++)for(let pi=0;pi<STORIES[s].pages.length;pi++){go(s,pi);await new Promise(r=>setTimeout(r,60));
  const els=$('text').querySelectorAll('[data-s]').length,T=NARR[STORIES[s].id+':'+pi];if(T&&T.length!==els)mm.push(STORIES[s].id+':'+pi+' '+T.length+'/'+els);
  const svg=$('pic').querySelector('svg:last-of-type');for(const w of $('text').querySelectorAll('.w[data-k]')){if(svg&&!svg.querySelector('.k-'+w.dataset.k))nr.push(STORIES[s].id+':'+(pi+1)+':'+w.dataset.k)}}
  return {mm,nr:[...new Set(nr)]}});
await p.waitForTimeout(1500);
console.log(JSON.stringify({...r,...r2,bad:[...new Set(bad)].slice(0,20),errs:errs.slice(0,10)},null,1));await b.close()})();
