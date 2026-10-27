const {chromium}=require('playwright');(async()=>{const b=await chromium.launch({args:['--autoplay-policy=no-user-gesture-required']});const p=await b.newPage();
await p.goto('http://localhost:8765/_t.html');await p.waitForTimeout(1000);
await p.evaluate(()=>go(0,4));await p.waitForTimeout(800);
console.log(await p.evaluate(()=>Object.keys(ACT).filter(k=>k.startsWith(STORIES[0].id+':4:'))));
await p.click('#say');let prev='';
for(let i=0;i<140;i++){await p.waitForTimeout(100);const r=await p.evaluate(()=>{const e=document.querySelector('.say-on');return [narrA.currentTime.toFixed(1),narrA.playbackRate,narrA.paused?'PAUSED':'',e?e.textContent:''].join(' ')});const key=r.split(' ').slice(1).join(' ');if(key!==prev){console.log(r);prev=key}if(!(await p.evaluate(()=>$('say').classList.contains('reading'))))break}
await b.close()})();
