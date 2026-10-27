const {chromium,devices}=require('playwright');(async()=>{const b=await chromium.launch({args:['--autoplay-policy=no-user-gesture-required']});
for(const mob of [false,true]){
const p=await (mob?b.newPage({...devices['Pixel 7']}):b.newPage({viewport:{width:1366,height:650}}));
const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('response',r=>{if(r.status()>=400)errs.push(r.status()+' '+r.url())});
await p.goto('http://localhost:8765/_t.html');await p.waitForTimeout(1500);
const si=await p.evaluate(()=>STORIES.findIndex(s=>s.id==='voo'));
await p.evaluate(s=>go(s,0),si);await p.waitForTimeout(2500);
for(let pg=0;pg<8;pg++){await p.evaluate(([s,pg])=>go(s,pg),[si,pg]);await p.waitForTimeout(900);
 await p.screenshot({path:`/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/b14/pk_${mob?'m':'d'}${pg}.png`})}
await p.evaluate(s=>go(s,4),si);await p.waitForTimeout(800);await p.click('#say');const seq=[];let last='';for(let i=0;i<40;i++){await p.waitForTimeout(100);const t=await p.evaluate(()=>{const e=document.querySelector('.say-on');return e?e.textContent:''});if(t!==last){seq.push(t);last=t}}
console.log(mob?'mobile':'desktop','listen p5:',seq.join('>'));await p.click('#say');
await p.evaluate(()=>{state.view='lib';});await p.goto('http://localhost:8765/_t.html');await p.waitForTimeout(1500);
const cov=await p.evaluate(()=>[...document.querySelectorAll('img')].filter(i=>i.src.includes('voo')).map(i=>[i.src.split('/').pop(),i.naturalWidth]));
console.log('cover',JSON.stringify(cov),'errs',errs);await p.close()}
await b.close()})();
