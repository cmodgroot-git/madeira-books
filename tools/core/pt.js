const {chromium}=require('playwright');(async()=>{const b=await chromium.launch({args:['--autoplay-policy=no-user-gesture-required']});
for(const [w,h,n] of [[1366,650,'d'],[390,844,'m']]){const p=await b.newPage({viewport:{width:w,height:h}});
await p.goto('http://localhost:8765/_t.html');await p.waitForTimeout(1200);
await p.click('[data-open="10"]');const seq=[];let last='';for(let i=0;i<30;i++){await p.waitForTimeout(100);const r=await p.evaluate(()=>{const e=document.querySelector('.say-on');return (e?e.textContent:'')+($('say').classList.contains('reading')?'':'|idle')});if(r!==last){seq.push(r);last=r}}
console.log(n,'open:',seq.join(' > '));await p.screenshot({path:`/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/pt_${n}.png`});
if(n==='d'){await p.click('#say');const s2=[];last='';for(let i=0;i<45;i++){await p.waitForTimeout(100);const r=await p.evaluate(()=>{const e=document.querySelector('.say-on');return e?e.textContent:''});if(r!==last){s2.push(r);last=r}}console.log('listen:',s2.join(' > '));
 await p.evaluate(()=>go(si,1));await p.waitForTimeout(500);console.log('page2 title in text:',await p.evaluate(()=>!!$('text').querySelector('.ptitle')),'header shown:',await p.evaluate(()=>!$('title').hidden));}
}
await b.close()})();
