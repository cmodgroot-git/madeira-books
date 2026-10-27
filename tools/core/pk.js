const {chromium}=require('playwright');(async()=>{const b=await chromium.launch({args:['--autoplay-policy=no-user-gesture-required']});const p=await b.newPage({viewport:{width:1366,height:650}});
const errs=[];p.on('pageerror',e=>errs.push(e.message));const reqs=[];p.on('request',r=>{if(/audio\//.test(r.url()))reqs.push(r.url().split('/').slice(-2).join('/'))});
await p.goto('http://localhost:8765/_t.html');await p.waitForTimeout(1200);
await p.evaluate(()=>go(4,3));await p.waitForTimeout(1200);
await p.click('#say');const seq=[];let last='';for(let i=0;i<40;i++){await p.waitForTimeout(100);const r=await p.evaluate(()=>{const e=document.querySelector('.say-on');return (e?e.textContent:'')});if(r!==last){seq.push(r);last=r}}
const info=await p.evaluate(()=>[PACK.narr[STORIES[si].id].off[cur],narrA.currentTime.toFixed(2)]);console.log('book5 p4 words:',seq.join('>'),'| off/now',info);
console.log('text:',await p.evaluate(()=>$('text').textContent.slice(0,80)));
// jump near the end of the page and confirm it stops at the page end (and Whole book turns)
await p.evaluate(()=>{state.auto=true;const P=PACK.narr[STORIES[si].id];narrA.currentTime=P.end[cur]-0.4});await p.waitForTimeout(3500);
console.log('after end:',await p.evaluate(()=>[cur,$('say').classList.contains('reading'),narrA.currentTime.toFixed(2),PACK.narr[STORIES[si].id].off[cur]]));
await p.evaluate(()=>{readTok++;narrStop();readClear();state.auto=false});
// page buttons strip
await p.locator('#tiles').screenshot({path:'/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/tiles.png'});
console.log('audio requests',[...new Set(reqs)].join(' '),'errs',errs);await b.close()})();
