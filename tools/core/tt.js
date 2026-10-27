const {chromium}=require('playwright');(async()=>{const b=await chromium.launch({args:['--autoplay-policy=no-user-gesture-required']});const p=await b.newPage();
await p.goto('http://localhost:8765/_t.html');await p.waitForTimeout(1200);
await p.click('[data-open="10"]');const out=[];for(let i=0;i<25;i++){await p.waitForTimeout(100);out.push(await p.evaluate(()=>tA?(tA.paused?'P':'')+tA.currentTime.toFixed(2):'-'))}
console.log(out.join(' '));console.log(await p.evaluate(()=>[cur,STORIES[si].id]));
await p.click('[data-open]').catch(()=>{});await b.close()})();
