const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1100,height:700}});
await p.goto('http://localhost:8765/_t.html');await p.waitForTimeout(1000);await p.evaluate(()=>go(0,1));await p.waitForTimeout(800);
console.log(await p.evaluate(()=>[[...document.querySelectorAll('.tools .btn')].map(b=>b.id+':'+b.getAttribute('aria-pressed')).join(' '),state.slow]));
await p.screenshot({path:'/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/ra.png',clip:{x:760,y:280,width:340,height:160}});await b.close()})();
