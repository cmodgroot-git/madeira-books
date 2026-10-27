const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();
p.on('pageerror',e=>console.log('ERR',e.message,e.stack.slice(0,300)));p.on('console',m=>{if(m.type()==='error')console.log('CON',m.text())});
await p.goto('http://localhost:8765/_t.html');await p.waitForTimeout(1500);await b.close()})();
