const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1366,height:650}});
const bad=[];p.on('response',r=>{if(r.status()>=400)bad.push(r.url())});
await p.goto('http://localhost:8765/_t.html');await p.waitForTimeout(1200);
const si=await p.evaluate(()=>STORIES.findIndex(s=>s.id==='carro'));await p.evaluate(s=>go(s,0),si);await p.waitForTimeout(1500);
for(const k of ['esplanada','tiago','cafe']){await p.evaluate(k=>light(k),k);await p.waitForTimeout(500);await p.locator('#pic').screenshot({path:`/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/b12/n_${k}.png`})}
console.log('bad',bad);await b.close()})();
