"""Recorded narration player + tap-to-hear from the recording + long-press for meaning (phones)."""
import re
A='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4/index.html'
h=open(A).read()
if 'const NARR=' not in h:
    i=h.find('let readTok=0,readTimers=[],readLast=null;')
    h=h[:i]+'const NARR={};\n'+h[i:]
JS=r"""
// ---------- recorded narration (exact word timings) ----------
let narrA=null,narrRAF=0;
const narrKey=()=>STORIES[si].id+':'+cur, narrSrc=()=>`audio/b${si+1}p${cur+1}.mp3`;
function narrStop(){cancelAnimationFrame(narrRAF);if(narrA){narrA.onended=null;try{narrA.pause()}catch(e){}}}
function narrPlay(tok){
  const T=NARR[narrKey()];if(!T)return false;
  if(!narrA)narrA=new Audio();narrStop();
  narrA.src=narrSrc();narrA.preservesPitch=true;narrA.playbackRate=state.slow?.75:1;narrA.currentTime=0;
  const els=[...$('text').querySelectorAll('[data-s]')],LEADN=.35;
  const tick=()=>{if(tok!==readTok)return;const t=narrA.currentTime+LEADN*narrA.playbackRate;let k=-1;
    for(let i=0;i<T.length;i++){if(T[i][0]/1000<=t)k=i;else break}
    if(k>=0&&els[k])readMark(tok,+els[k].dataset.s);narrRAF=requestAnimationFrame(tick)};
  narrA.onended=()=>{if(tok!==readTok)return;cancelAnimationFrame(narrRAF);readClear()};
  const p=narrA.play();$('say').classList.add('reading');narrRAF=requestAnimationFrame(tick);
  if(p&&p.catch)p.catch(()=>{if(tok===readTok){readClear()}});
  return true}
function narrWord(el){
  const T=NARR[narrKey()];if(!T)return false;const els=[...$('text').querySelectorAll('[data-s]')],k=els.indexOf(el);if(k<0||!T[k])return false;
  if(!narrA)narrA=new Audio();readTok++;narrStop();readClear();try{speechSynthesis.cancel()}catch(e){}
  const [s,e]=T[k];narrA.src=narrSrc();narrA.playbackRate=1;
  const go=()=>{narrA.currentTime=Math.max(0,s/1000-.04);const p=narrA.play();if(p&&p.catch)p.catch(()=>{});
    const stopAt=e/1000+.08,chk=()=>{if(narrA.currentTime>=stopAt||narrA.paused){narrA.pause();return}narrRAF=requestAnimationFrame(chk)};narrRAF=requestAnimationFrame(chk)};
  if(narrA.readyState>=1)go();else narrA.addEventListener('loadedmetadata',go,{once:true});
  return true}
"""
if 'function narrPlay' not in h:
    i=h.find('function readPage(){'); h=h[:i]+JS.lstrip()+h[i:]
# readPage: use the recording when there is one
old="  readClear();const tok=++readTok;\n  const LEAD="
if old in h and 'if(narrPlay(tok))return;' not in h:
    h=h.replace(old,"  readClear();const tok=++readTok;narrStop();\n  if(narrPlay(tok))return;\n  const LEAD=",1)
# stopping: toggleRead, go, back
h=h.replace("function toggleRead(){if($('say').classList.contains('reading')){readTok++;try{speechSynthesis.cancel()}catch(e){}readClear();return}readPage()}",
            "function toggleRead(){if($('say').classList.contains('reading')){readTok++;narrStop();try{speechSynthesis.cancel()}catch(e){}readClear();return}readPage()}")
h=h.replace("function go(s,p){if(s<0||s>=STORIES.length||p<0||p>=STORIES[s].pages.length)return;si=s;cur=p;try{speechSynthesis.cancel()}catch(e){}",
            "function go(s,p){if(s<0||s>=STORIES.length||p<0||p>=STORIES[s].pages.length)return;si=s;cur=p;readTok++;narrStop();try{speechSynthesis.cancel()}catch(e){}")
h=h.replace("$('back').onclick=()=>{try{speechSynthesis.cancel()}catch(e){}renderLib()};","$('back').onclick=()=>{readTok++;narrStop();try{speechSynthesis.cancel()}catch(e){}renderLib()};")
# tap a word: hear it from the recording when there is one
h=h.replace("const w=e.target.closest('.w');if(w){light(w.dataset.k);speak(w.textContent);return}",
            "const w=e.target.closest('.w');if(w){if(Date.now()-lpAt<700)return;light(w.dataset.k);narrWord(w)||speak(w.textContent);return}")
# long-press on phones shows the meaning
LP=r"""
// Long-press a word (phones and tablets) shows its meaning, like Ctrl/⌘/⌥-click on a computer.
let lpT=0,lpAt=0,lpXY=null;
document.addEventListener('pointerdown',e=>{if(e.pointerType==='mouse')return;const t=e.target.closest('.w,[data-say]');if(!t)return;lpXY=[e.clientX,e.clientY];clearTimeout(lpT);
  lpT=setTimeout(()=>{lpAt=Date.now();const k=t.dataset.k||t.dataset.say;light(k);showGloss(t,k);try{navigator.vibrate&&navigator.vibrate(15)}catch(_){}},480)},{passive:true});
['pointerup','pointercancel'].forEach(n=>document.addEventListener(n,()=>clearTimeout(lpT),{passive:true}));
document.addEventListener('pointermove',e=>{if(lpXY&&Math.hypot(e.clientX-lpXY[0],e.clientY-lpXY[1])>10)clearTimeout(lpT)},{passive:true});
document.addEventListener('contextmenu',e=>{if(Date.now()-lpAt<1500&&e.target.closest('.w,[data-say]'))e.preventDefault()});
"""
if 'let lpT=0' not in h:
    i=h.find('// Modifier-click on a word shows its meaning.'); h=h[:i]+LP.lstrip()+h[i:]
# no text-selection callout on words
if '-webkit-touch-callout:none' not in h:
    h=h.replace('.w.new{','.w,[data-say]{-webkit-touch-callout:none;-webkit-user-select:none;user-select:none}\n.w.new{',1)
open(A,'w').write(h)
print(h.count('narrPlay(tok)'),h.count('let lpT=0'),h.count('narrWord(w)'),h.count('touch-callout:none'))
