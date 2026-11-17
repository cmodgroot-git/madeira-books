const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1366,height:800}});
const errs=[],bad=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});p.on('response',r=>{if(r.status()>=400)bad.push(r.status()+' '+r.url())});
await p.goto('http://localhost:8765/_t.html');await p.waitForTimeout(1500);
const ids=await p.evaluate(()=>STORIES.map(s=>s.id));const out=[];
for(const id of ids){const si=ids.indexOf(id);const n=await p.evaluate(i=>STORIES[i].pages.length,si);
  for(const pg of [0,n-1]){await p.evaluate(([s,pg])=>go(s,pg),[si,pg]);await p.waitForTimeout(900);
    const r=await p.evaluate(()=>{const s=$('pic').querySelector('svg:last-of-type');const im=s&&s.querySelector('svg[id$="ph"] image, image[id$="ph"]');if(!im)return 'noimg';const bb=im.getBoundingClientRect();return im.getAttribute('href').split('/').pop()+' '+(im.complete===undefined?'':'')+Math.round(bb.width)+'x'+Math.round(bb.height)});
    out.push(id+':'+pg+' '+r)}
  if(['manha','jogo','sabado','casa3'].includes(id)){await p.evaluate(([s])=>go(s,0),[si]);await p.waitForTimeout(800);await p.locator('#pic').screenshot({path:`/home/claude/work/pack_${id}.png`})}}
console.log(out.join('\n'));
// study view word crops for book 1 and 22
for(const id of ['manha','jogo']){const si=ids.indexOf(id);await p.evaluate(s=>{si=s;renderStudy('w')},si);await p.waitForTimeout(2500);await p.screenshot({path:`/home/claude/work/study_${id}.png`,fullPage:false})}
console.log(JSON.stringify({errs,bad:[...new Set(bad)]}));await b.close()})();
