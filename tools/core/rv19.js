const {chromium}=require('playwright');(async()=>{const b=await chromium.launch({args:['--autoplay-policy=no-user-gesture-required']});
const p=await b.newPage({viewport:{width:1366,height:800}});const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
await p.goto('http://localhost:8765/_t.html');await p.waitForTimeout(1500);
const info=await p.evaluate(()=>{const d=rvDay();state.seen={};STORIES.forEach(st=>state.seen[st.id]=st.pages.map((_,i)=>i));state.rev={};
  for(const k of ['abre','ve','sobe','acorda','apanha','olha','ouvem','pede','vaiabaixo','espreita'])state.rev[k]=[1e9,-1,0,d-5];
  for(const k of ['mesa','mala','carro','agua','mar','casa'])state.rev[k]=[d,3,0,d-30];   // matured, due today
  save();rv=null;return {q:revQueue().slice(0,22)}});
console.log('queue',info.q.join(' '));
await p.evaluate(()=>renderReview());await p.waitForTimeout(2500);
const res=[];
for(let i=0;i<16;i++){const c=await p.evaluate(()=>{const k=rv.q[0];return {k,ctx:rv.ctx[k]&&(STORIES[rv.ctx[k][0]].id+(rv.ctx[k][1]+1)),first:STORIES[first[k].s].id+(first[k].p+1)}});
  await p.click('#rvshow');await p.waitForTimeout(400);
  const t0=await p.evaluate(()=>narrA?narrA.currentTime:-1);await p.waitForTimeout(900);const t1=await p.evaluate(()=>narrA&&!narrA.paused?narrA.currentTime:-1);
  const sent=await p.evaluate(()=>document.querySelector('#rvsent').textContent);const crop=await p.evaluate(()=>document.querySelector('.crop').getAttribute('style').slice(-60));
  await p.screenshot({path:`/home/claude/work/rv/${i}_${c.k}.png`});
  res.push(`${c.k} ${c.first}→${c.ctx} audio ${t0.toFixed(1)}→${t1.toFixed(1)} | ${sent}`);
  await p.click('[data-rv="1"]');await p.waitForTimeout(300)}
console.log(res.join('\n'));console.log('errs',errs);await b.close()})();
