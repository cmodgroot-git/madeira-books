const {chromium}=require('playwright');(async()=>{const b=await chromium.launch({args:['--autoplay-policy=no-user-gesture-required']});const p=await b.newPage();
await p.goto('http://localhost:8765/_t.html');await p.waitForTimeout(1200);
async function run(s,pg,slow,label){await p.evaluate(([s,pg,slow])=>{state.slow=slow;setSlowBtn();go(s,pg)},[s,pg,slow]);await p.waitForTimeout(800);await p.evaluate(()=>readPage());
 const seen=new Set();for(let i=0;i<90;i++){await p.waitForTimeout(100);const r=await p.evaluate(()=>{const svg=$('pic').querySelector('svg:last-of-type');const o=svg.querySelector('[class*="act-"]');const e=document.querySelector('.say-on');return o?(e&&e.textContent)+(svg.classList.contains('actq')?'(quick)':'(full)'):''});if(r)seen.add(r);if(!(await p.evaluate(()=>$('say').classList.contains('reading'))))break}
 await p.evaluate(()=>{readTok++;narrStop();readClear()});console.log(label,[...seen].join(' '))}
await run(0,4,false,'book1 p5 Slow off (new sai, dorme):');
await run(0,4,true,'book1 p5 Slow on:');
const r=await p.evaluate(()=>{const o=[];STORIES.forEach((st,s)=>st.pages.forEach((pg,i)=>{for(const m of pg.matchAll(RX))if(ACT[st.id+':'+i+':'+m[2]]&&first[m[2]]&&(first[m[2]].s!==s||first[m[2]].p!==i))o.push([s,i,m[2]])}));return o[0]});
await run(r[0],r[1],false,'known action '+r[2]+' Slow off:');
await b.close()})();
