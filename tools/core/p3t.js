const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1366,height:650}});const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('response',r=>{if(r.status()>=400)errs.push(r.status()+' '+r.url())});
await p.goto('http://localhost:8765/_t.html');await p.waitForTimeout(1000);
const si=await p.evaluate(()=>STORIES.findIndex(s=>s.id==='veleiro'));await p.evaluate(s=>go(s,2),si);await p.waitForTimeout(1000);
for(const k of ['ica','corda','inclina']){await p.evaluate(k=>light(k),k);await p.waitForTimeout(700);await p.locator('#pic').screenshot({path:`/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/b13/t3_${k}.png`})}
console.log('errs',errs);await b.close()})();
