"""Read-along: every word wrapped with its offsets in the spoken text; Listen highlights each word as it is spoken
and lights tappable words in the picture (with their action cue)."""
S = '/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'
A = S + 'artifact-files/87e1712e-5e90-4175-b828-2581544915d4/index.html'
h = open(A).read()

old_render = "$('text').innerHTML=p.replace(RX,(m,w,k)=>{const cls=['w'];if(known.has(k))cls.push('known');else if(isFirst(k))cls.push('new');if(actOf(k))cls.push('act');return `<button type=\"button\" class=\"${cls.join(' ')}\" data-k=\"${k}\">${w}</button>`});"
new_render = "$('text').innerHTML=textHTML(p,k=>{const cls=['w'];if(known.has(k))cls.push('known');else if(isFirst(k))cls.push('new');if(actOf(k))cls.push('act');return cls.join(' ')});"

JS = r"""
// ---------- read-along ----------
const WRX=/[\p{L}\p{N}]+(?:[-'’][\p{L}\p{N}]+)*/gu;
function textHTML(p,clsOf){
  let out='',pos=0,last=0;
  const plain=s=>s.replace(WRX,(w,o)=>`<span class="tw" data-s="${pos+o}" data-e="${pos+o+w.length}">${w}</span>`);
  p.replace(RX,(m,w,k,off)=>{const t=p.slice(last,off);out+=plain(t);pos+=t.length;
    out+=`<button type="button" class="${clsOf(k)}" data-k="${k}" data-s="${pos}" data-e="${pos+w.length}">${w}</button>`;pos+=w.length;last=off+m.length;return m});
  out+=plain(p.slice(last));return out}
let readTok=0,readTimers=[],readLast=null;
function readClear(){readTimers.forEach(clearTimeout);readTimers=[];document.querySelectorAll('.say-on').forEach(e=>e.classList.remove('say-on'));readLast=null;$('say').classList.remove('reading')}
function readMark(tok,i){
  if(tok!==readTok)return;
  const ws=[...$('text').querySelectorAll('[data-s]')];
  const el=ws.find(e=>+e.dataset.s<=i&&i<+e.dataset.e)||ws.find(e=>+e.dataset.s>=i);
  if(!el||el===readLast)return;
  document.querySelectorAll('.say-on').forEach(e=>e.classList.remove('say-on'));
  el.classList.add('say-on');readLast=el;
  if(el.dataset.k)light(el.dataset.k);
}
function readPage(){
  const text=STORIES[si].pages[cur].replace(RX,'$1');
  try{speechSynthesis.cancel()}catch(e){}
  readClear();const tok=++readTok;
  let u;try{u=new SpeechSynthesisUtterance(text)}catch(e){return}
  u.lang='pt-PT';if(voice)u.voice=voice;u.rate=.85;
  let gotBoundary=false;
  u.onboundary=e=>{if(e.name&&e.name!=='word')return;gotBoundary=true;readTimers.forEach(clearTimeout);readTimers=[];readMark(tok,e.charIndex)};
  u.onstart=()=>{if(tok!==readTok)return;$('say').classList.add('reading');
    // voices without word events: pace the words by length (word events, when they come, cancel this)
    if(gotBoundary)return;const ms=78/u.rate;
    [...$('text').querySelectorAll('[data-s]')].forEach(el=>{const s=+el.dataset.s;readTimers.push(setTimeout(()=>{if(!gotBoundary)readMark(tok,s)},s*ms))})};
  u.onend=u.onerror=()=>{if(tok!==readTok)return;readClear()};
  speechSynthesis.speak(u);
}
"""

CSS = r"""
/* read-along */
#text .tw,#text .w{transition:background-color .15s, box-shadow .15s}
#text .tw.say-on,#text .w.say-on{background:var(--hl);box-shadow:0 0 0 2px var(--hl);border-radius:4px}
#say.reading{box-shadow:0 0 0 2px var(--accent)}
"""

assert h.count(old_render) == 1 or 'textHTML(p,' in h
h = h.replace(old_render, new_render, 1)
if 'function textHTML' not in h:
    i = h.find("let view='lib',si=0,cur=0,hlTimer;")
    h = h[:i] + JS + h[i:]
old_say = "$('say').onclick=()=>speak(STORIES[si].pages[cur].replace(RX,'$1'));"
if old_say in h: h = h.replace(old_say, "$('say').onclick=readPage;", 1)
if '/* read-along */' not in h:
    i = h.find('/* action words */')
    h = h[:i] + CSS.strip() + '\n' + h[i:]
open(A, 'w').write(h)
print('ok')
