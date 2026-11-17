const {chromium}=require('playwright');(async()=>{const b=await chromium.launch({args:['--autoplay-policy=no-user-gesture-required']});const p=await b.newPage({viewport:{width:1366,height:650}});
const errs=[],bad=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});p.on('response',r=>{if(r.status()>=400)bad.push(r.status()+' '+r.url())});
await p.goto('http://localhost:8765/_t.html');await p.waitForTimeout(1500);
const si=await p.evaluate(()=>STORIES.findIndex(s=>s.id==='cao3'));const out=[];
for(let pg=0;pg<8;pg++){await p.evaluate(([s,pg])=>go(s,pg),[si,pg]);await p.waitForTimeout(2000);
  const ks=await p.evaluate(()=>[...document.querySelectorAll('#text .w[data-k]')].map(e=>e.dataset.k));
  for(const k of [...new Set(ks)]){await p.evaluate(k=>light(k),k);await p.waitForTimeout(600);
    const n=await p.evaluate(k=>{const svg=$('pic').querySelector('svg:last-of-type');return svg?svg.querySelectorAll('.k-'+k).length:-1},k);
    await p.locator('#pic').screenshot({path:`/home/claude/work/b3b/tap/${pg}_${k}.png`});out.push(`${pg+1}:${k}:${n}`)}}
console.log(out.join(' '));console.log(JSON.stringify({errs,bad:[...new Set(bad)]}));await b.close()})();
