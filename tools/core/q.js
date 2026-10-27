const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:800,height:900}});
await p.goto('http://localhost:8765/_t.html');await p.waitForTimeout(1500);
const r=await p.evaluate(()=>{const bs=[...document.querySelectorAll('button')].filter(x=>/^Quiz$/i.test(x.textContent.trim()));return bs.length});
console.log('quiz buttons on home',r);
await p.evaluate(()=>{const s=document.querySelector('[data-story],.book,.card');s&&s.click()});await p.waitForTimeout(800);
await p.evaluate(()=>{const q=[...document.querySelectorAll('button')].find(x=>/^Quiz$/i.test(x.textContent.trim()));q&&q.click()});await p.waitForTimeout(1500);
const c=await p.evaluate(()=>{const e=document.querySelector('.quiz .crop');return e?e.getBoundingClientRect().height:null});console.log('crop height',c);
await p.screenshot({path:'/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/quizfix.png'});await b.close()})();
