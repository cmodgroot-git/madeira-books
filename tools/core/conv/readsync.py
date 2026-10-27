"""Read-along that keeps up on phones: speak sentence/clause chunks (each start re-syncs), pace words by syllables,
and learn the voice's real speed from each chunk's duration (kept per voice in localStorage)."""
A='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4/index.html'
h=open(A).read()
i=h.find('function readPage(){'); j=h.find('\nlet view=',i)
NEW=r"""function readPage(){
  const text=STORIES[si].pages[cur].replace(RX,'$1');
  try{speechSynthesis.cancel()}catch(e){}
  readClear();const tok=++readTok;
  const rate=state.slow?.6:.85,vk='rk:'+((voice&&voice.name)||'default');
  let K=200;try{const v=+localStorage.getItem(vk);if(v>60&&v<600)K=v}catch(e){}
  const syl=w=>Math.max(1,(w.match(/[aeiouáéíóúâêôãõày]+/gi)||[]).length)+.35;
  // chunks: split after . ! ? ; : , — » … followed by a space (each chunk's start re-syncs the highlight)
  const chunks=[];let s0=0;text.replace(/[.!?;:,—»…]+["»”]?\s+/g,(m,o)=>{const e=o+m.length;if(text.slice(s0,e).trim())chunks.push([s0,e]);s0=e;return m});
  if(text.slice(s0).trim())chunks.push([s0,text.length]);
  const words=[...$('text').querySelectorAll('[data-s]')].map(el=>({s:+el.dataset.s,e:+el.dataset.e}));
  chunks.forEach(([cs,ce],ci)=>{
    let u;try{u=new SpeechSynthesisUtterance(text.slice(cs,ce))}catch(e){return}
    u.lang='pt-PT';if(voice)u.voice=voice;u.rate=rate;
    let gotB=false,t0=0;const ws=words.filter(w=>w.s>=cs&&w.s<ce);
    const W=ws.reduce((a,w)=>a+syl(text.slice(w.s,w.e)),0);
    u.onboundary=e=>{if(tok!==readTok)return;if(e.name&&e.name!=='word')return;if(!gotB){gotB=true;readTimers.forEach(clearTimeout);readTimers=[]}readMark(tok,cs+e.charIndex)};
    u.onstart=()=>{if(tok!==readTok)return;$('say').classList.add('reading');t0=performance.now();
      readTimers.forEach(clearTimeout);readTimers=[];readMark(tok,ws.length?ws[0].s:cs);
      // no word events on many phone voices: pace the words by syllables at the learned speed
      let acc=0;const ms=K/rate;
      ws.forEach((w,k)=>{if(k)readTimers.push(setTimeout(()=>{if(!gotB)readMark(tok,w.s)},acc*ms));acc+=syl(text.slice(w.s,w.e))})};
    u.onend=()=>{if(tok!==readTok)return;
      if(!gotB&&t0&&W>=3){const d=performance.now()-t0,k=d*rate/(W+1.2);if(k>60&&k<600){K=.6*K+.4*k;try{localStorage.setItem(vk,String(Math.round(K)))}catch(e){}}}
      if(ci===chunks.length-1)readClear()};
    u.onerror=e=>{if(tok!==readTok)return;if(e&&e.error==='interrupted')return;readClear()};
    speechSynthesis.speak(u);
  });
}"""
assert i>0 and j>i
h=h[:i]+NEW+h[j:]
open(A,'w').write(h); print('ok')
