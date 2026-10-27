const {chromium}=require('playwright');(async()=>{const b=await chromium.launch({args:['--autoplay-policy=no-user-gesture-required']});const p=await b.newPage({viewport:{width:1366,height:650}});
const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('http://localhost:8765/_t.html');await p.waitForTimeout(1200);
const si=await p.evaluate(()=>STORIES.findIndex(s=>s.id==='veleiro'));
const shots=[];
for(let pg=0;pg<8;pg++){await p.evaluate(([s,pg])=>go(s,pg),[si,pg]);await p.waitForTimeout(700);
  const ks=await p.evaluate(()=>[...document.querySelectorAll('#text .w[data-k]')].map(e=>e.dataset.k));
  for(const k of [...new Set(ks)]){await p.evaluate(k=>{const e=document.querySelector(`#text .w[data-k="${k}"]`);light(k)},k);await p.waitForTimeout(450);
    const r=await p.evaluate(()=>{const svg=$('pic').querySelector('svg:last-of-type');return [svg.querySelectorAll('.hl').length,svg.querySelectorAll('.actfx path,[class*="act-"]').length]});
    const f=`/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/b13/tap_${pg}_${k}.png`;await p.locator('#pic').screenshot({path:f});shots.push([pg,k,r.join('/'),f]);
    await p.waitForTimeout(150)}}
console.log(shots.map(s=>s.slice(0,3).join(':')).join(' '));
// title + listen page 1
await p.evaluate(s=>go(s,0),si);await p.waitForTimeout(500);await p.click('#say');const seq=[];let last='';for(let i=0;i<30;i++){await p.waitForTimeout(100);const t=await p.evaluate(()=>{const e=document.querySelector('.say-on');return e?e.textContent:''});if(t!==last){seq.push(t);last=t}}
console.log('listen:',seq.join('>'));await p.click('#say');
await p.evaluate(s=>{si=s;renderStudy('w')},si);await p.waitForTimeout(800);console.log('cards',await p.evaluate(()=>document.querySelectorAll('.wcard').length));
await p.screenshot({path:'/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/b13/words.png',fullPage:true});
await p.evaluate(()=>renderStudy('q'));await p.waitForTimeout(500);console.log('quiz',await p.evaluate(()=>[quiz.qs.length,getComputedStyle(document.querySelector('.quiz .crop')).height]));
console.log('errs',errs);await b.close()})();
