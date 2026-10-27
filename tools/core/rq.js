const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();
await p.goto('http://localhost:8765/_t.html');await p.waitForTimeout(1000);
const r=await p.evaluate(()=>{const out={};for(let s=0;s<STORIES.length;s++){si=s;let qr=0,or=0,n=0;for(let t=0;t<200;t++){newQuiz();for(const q of quiz.qs){n++;if(q.k==='rita')qr++;if(q.opts.includes('rita'))or++; if(new Set(q.opts.map(k=>label[k])).size<q.opts.length)out.dup=(out.dup||0)+1}}out[s]=[n,qr,or]}
 si=0;out.words=bookWords(0).map(w=>w.k+'@'+w.p+':'+w.crop.match(/position:(.*)/)[1]).join(' | ');return out});
console.log(JSON.stringify(r,null,1));await b.close()})();
