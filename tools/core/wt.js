const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1200,height:900}});
await p.goto('http://localhost:8765/_t.html');await p.waitForTimeout(1000);await p.evaluate(()=>{si=0;renderStudy('w')});await p.waitForTimeout(1500);
await p.screenshot({path:'/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/w1.png',fullPage:true});await b.close()})();
