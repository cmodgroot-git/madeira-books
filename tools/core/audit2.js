const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();
await p.goto('http://localhost:8765/_t.html');await p.waitForTimeout(1500);
console.log(JSON.stringify(await p.evaluate(()=>{const nr=[];STORIES.forEach((st,s)=>st.pages.forEach((pg,pi)=>{const svg=photoOf(st.id,pi)||'';for(const m of pg.matchAll(RX)){if(!svg.includes('k-'+m[2]))nr.push(st.id+':'+(pi+1)+':'+m[2])}}));return nr})));await b.close()})();
