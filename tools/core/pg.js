const {chromium}=require('playwright');(async()=>{const b=await chromium.launch({args:['--autoplay-policy=no-user-gesture-required']});const p=await b.newPage();
await p.goto('http://localhost:8765/_t.html');await p.waitForTimeout(1200);await p.click('[data-open="0"]');await p.waitForTimeout(1200);
await p.click('#say');await p.waitForTimeout(800);const L=()=>p.evaluate(()=>[$('saylbl').textContent,$('say').classList.contains('reading'),cur]);
console.log('playing',await L());await p.click('#next');await p.waitForTimeout(800);console.log('after next',await L());
await p.evaluate(()=>{state.auto=true});await p.click('#say');await p.waitForTimeout(500);await p.evaluate(()=>{narrA.pause();narrA.onended()});await p.waitForTimeout(2500);console.log('whole book continues',await L());
await b.close()})();
