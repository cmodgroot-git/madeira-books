const {chromium,devices}=require('playwright');(async()=>{const b=await chromium.launch();const c=await b.newContext({...devices['Pixel 7']});const p=await c.newPage();
p.on('pageerror',e=>console.log('ERR',e.message,e.stack.slice(0,200)));p.on('console',m=>{if(m.type()!=='log')console.log('CON',m.type(),m.text().slice(0,200))});
p.on('requestfailed',r=>console.log('FAIL',r.url()));
await p.goto('http://localhost:8765/_t.html');await p.waitForTimeout(3000);
console.log(await p.evaluate(()=>[document.querySelectorAll('#shelf .cover').length,document.body.scrollHeight]));
await p.screenshot({path:'/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/mob.png',fullPage:true});await b.close()})();
