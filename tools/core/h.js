const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();
for(const [w,h,n] of [[1000,700,'d'],[390,800,'m']]){const p=await b.newPage({viewport:{width:w,height:h}});
await p.goto('http://localhost:8765/_t.html');await p.waitForTimeout(1200);await p.screenshot({path:`/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/how_${n}.png`});
await p.click('#howbtn');await p.waitForTimeout(900);console.log(n,await p.evaluate(()=>[document.getElementById('howbox').open,Math.round(document.getElementById('howbox').getBoundingClientRect().top)]));}
await b.close()})();
