const {chromium}=require('playwright');(async()=>{const b=await chromium.launch({args:['--autoplay-policy=no-user-gesture-required']});const p=await b.newPage();
await p.goto('http://localhost:8765/_t.html');await p.waitForTimeout(1000);
for(const slow of [false,true]){await p.evaluate(s=>{state.slow=s;setSlowBtn();go(0,4)},slow);await p.waitForTimeout(800);await p.evaluate(()=>readPage());
 let acts=0,minRate=9;for(let i=0;i<70;i++){await p.waitForTimeout(100);const r=await p.evaluate(()=>[document.querySelectorAll('#pic [class*="act-"]').length,narrA.playbackRate]);if(r[0])acts++;minRate=Math.min(minRate,r[1])}
 console.log('slow',slow,'frames with action',acts,'min rate',minRate);await p.evaluate(()=>{readTok++;narrStop();readClear()})}
// tap still shows action with slow off
await p.evaluate(()=>{state.slow=false;go(0,4)});await p.waitForTimeout(800);await p.evaluate(()=>light('sai'));await p.waitForTimeout(200);console.log('tap action',await p.evaluate(()=>document.querySelectorAll('#pic [class*="act-"]').length));
await b.close()})();
