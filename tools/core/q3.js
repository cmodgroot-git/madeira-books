const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage();const reqs=[];p.on('request',r=>{if(/photos\//.test(r.url()))reqs.push(r.url().split('/').pop())});
await p.goto('http://localhost:8765/_t.html');await p.waitForTimeout(1500);console.log('at start',reqs.join(' '));
await p.click('[data-open="3"]');await p.waitForTimeout(1500);console.log('after book 4',reqs.join(' '),await p.evaluate(()=>[cur,STORIES[si].id,!!$('pic').querySelector('svg image')]));
await p.evaluate(()=>{state.miss=['rita','kart'];renderStudy('q')});await p.waitForTimeout(1500);console.log('quiz',reqs.join(' '),await p.evaluate(()=>[quiz.qs.length,quiz.qs.map(q=>q.k).join(',')]));
await b.close()})();
