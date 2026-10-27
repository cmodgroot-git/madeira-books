const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();
await p.goto('http://localhost:8765/_t.html');await p.waitForTimeout(1000);
const r=await p.evaluate(()=>{const out=[];for(let s=0;s<STORIES.length;s++){si=s;let lens=new Set(),bad=0;for(let t=0;t<200;t++){newQuiz();lens.add(quiz.qs.length);const seen={};for(const q of quiz.qs){const k=q.crop;if(seen[k])bad++;seen[k]=1}}out.push(s+':'+[...lens]+' dupPics '+bad)}
 si=0;newQuiz();out.push(quiz.qs.map(q=>q.k).join(' '));return out});
console.log(r.join('\n'));await b.close()})();
