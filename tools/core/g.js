const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1000,height:800}});
await p.goto('http://localhost:8765/_t.html');await p.waitForTimeout(1200);await p.click('#howbtn');await p.waitForTimeout(800);
await p.screenshot({path:'/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/gs.png'});
await p.click('.gostart button');await p.waitForTimeout(1000);console.log(await p.evaluate(()=>document.querySelector('h1,h2')&&[...document.querySelectorAll('h1')].map(h=>h.offsetParent?h.textContent:'').join('|')));await b.close()})();
