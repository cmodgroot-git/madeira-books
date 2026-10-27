"""Action-word cues: wavy underline in the text, and a motion cue in the picture when an action word is tapped.
ACT entries are kept in gen/act.json  {"story:page:key": {...}} and written into index.html as const ACT."""
import json, re, sys
S = '/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'
A = S + 'artifact-files/87e1712e-5e90-4175-b828-2581544915d4/index.html'
ACT = json.load(open(S + 'gen/act.json'))
h = open(A).read()

CSS = r"""
/* action words */
.w.act{text-decoration-style:wavy;text-decoration-thickness:1.2px;text-underline-offset:.28em}
.w.act.known{text-decoration-color:color-mix(in srgb,var(--fg) 30%,transparent)}
.w.act.active{text-decoration-color:transparent}
.sw.act{border:0;height:6px;background:var(--muted);-webkit-mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='6'%3E%3Cpath d='M0 3 Q2.25 0 4.5 3 T9 3 T13.5 3 T18 3' fill='none' stroke='black' stroke-width='1.4'/%3E%3C/svg%3E") no-repeat;mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='6'%3E%3Cpath d='M0 3 Q2.25 0 4.5 3 T9 3 T13.5 3 T18 3' fill='none' stroke='black' stroke-width='1.4'/%3E%3C/svg%3E") no-repeat}
.pic svg .o.hl.act-move{animation:actmove 1.4s cubic-bezier(.35,.1,.3,1) forwards}
@keyframes actmove{0%{transform:scale(1.03) translate(0,0)}100%{transform:scale(1.03) translate(var(--dx),var(--dy))}}
.pic svg .o.hl.act-hold{animation:acthold 1.1s ease-in-out 2}

.pic svg .o.hl.act-spin{animation:actspin 1.4s linear 1}
@keyframes actspin{0%{transform:scale(1.03,1.03)}25%{transform:scale(.04,1.03)}50%{transform:scale(-1.03,1.03)}75%{transform:scale(-.04,1.03)}100%{transform:scale(1.03,1.03)}}
.pic svg .o.hl.act-rest{animation:actrest 2.4s ease-in-out 1}
@keyframes actrest{0%,100%{transform:scale(1.03)}50%{transform:scale(1.055)}}
@keyframes acthold{0%,100%{transform:scale(1.03)}35%{transform:scale(1.07)}70%{transform:scale(.995)}}
.actfx{pointer-events:none}
.pic svg .actplate{animation:actplate .35s ease-out both;pointer-events:none}
@keyframes actplate{from{opacity:0}}
.actfx path{fill:none;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1;animation:actdraw .55s ease-out .2s forwards}
.actfx .sh{stroke:#2A1D14;stroke-opacity:.5;stroke-width:3.2}
.actfx .ln{stroke:#FFF6E6;stroke-width:1.7}
.actfx.sound path{animation:actdraw .35s ease-out .1s forwards,actpulse .7s ease-in-out .45s 3}
@keyframes actdraw{to{stroke-dashoffset:0}}
@keyframes actpulse{50%{opacity:.25}}
@media (prefers-reduced-motion:reduce){.pic svg .o.hl.act-move,.pic svg .o.hl.act-hold,.pic svg .o.hl.act-rest,.pic svg .o.hl.act-spin{animation:none}.actfx path{animation:none;stroke-dashoffset:0}}
"""

JS = r"""
const NS_SVG='http://www.w3.org/2000/svg';
const actOf=k=>{const st=STORIES[si];return st?ACT[st.id+':'+cur+':'+k]:null};
function actClear(svg){svg.querySelectorAll('.actfx,.actplate').forEach(e=>e.remove());svg.querySelectorAll('.act-move,.act-hold,.act-rest,.act-spin').forEach(e=>e.classList.remove('act-move','act-hold','act-rest','act-spin'))}
function actFx(svg,els,a){
  actClear(svg);if(!a||!els.length)return;
  let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;
  els.forEach(g=>g.querySelectorAll('rect.bb').forEach(r=>{const x=+r.getAttribute('x'),y=+r.getAttribute('y'),w=+r.getAttribute('width'),h=+r.getAttribute('height');x0=Math.min(x0,x);y0=Math.min(y0,y);x1=Math.max(x1,x+w);y1=Math.max(y1,y+h)}));
  if(a.box){[x0,y0,x1,y1]=[a.box[0],a.box[1],a.box[0]+a.box[2],a.box[1]+a.box[3]]}
  const ds=[];const f=n=>n.toFixed(1);
  if(a.t==='move'){
    els.forEach(e=>{e.style.setProperty('--dx',a.dx+'px');e.style.setProperty('--dy',a.dy+'px');e.classList.add('act-move')});if(a.plate){const im=document.createElementNS(NS_SVG,'image');im.setAttribute('href',a.plate);im.setAttribute('x',a.pbox[0]);im.setAttribute('y',a.pbox[1]);im.setAttribute('width',a.pbox[2]);im.setAttribute('height',a.pbox[3]);im.setAttribute('preserveAspectRatio','none');im.setAttribute('class','actplate');const dm=svg.querySelector('rect.dimmer');(dm||els[0]).parentNode.insertBefore(im,dm||els[0])}
    const L=Math.hypot(a.dx,a.dy)||1,ux=a.dx/L,uy=a.dy/L,px=-uy,py=ux;
    const cx=(x0+x1)/2+(a.ox||0),cy=(y0+y1)/2+(a.oy||0),hw=(x1-x0)/2*Math.abs(ux)+(y1-y0)/2*Math.abs(uy);
    const len=a.len||22,sx=cx+ux*(hw+4)+a.dx,sy=cy+uy*(hw+4)+a.dy,ex=sx+ux*len,ey=sy+uy*len;
    ds.push(`M${f(sx)},${f(sy)} L${f(ex)},${f(ey)} M${f(ex-ux*5+px*3.5)},${f(ey-uy*5+py*3.5)} L${f(ex)},${f(ey)} L${f(ex-ux*5-px*3.5)},${f(ey-uy*5-py*3.5)}`);
    if(a.trail!==false)for(const o of [-1,0,1]){const bx=cx-ux*(hw+3)+px*o*(a.spread||6),by=cy-uy*(hw+3)+py*o*(a.spread||6),l=o?8:12;ds.push(`M${f(bx)},${f(by)} L${f(bx-ux*l)},${f(by-uy*l)}`)}
  }else if(a.t==='spin'){
    els.forEach(e=>e.classList.add('act-spin'));if(a.plate){const im=document.createElementNS(NS_SVG,'image');im.setAttribute('href',a.plate);im.setAttribute('x',a.pbox[0]);im.setAttribute('y',a.pbox[1]);im.setAttribute('width',a.pbox[2]);im.setAttribute('height',a.pbox[3]);im.setAttribute('preserveAspectRatio','none');im.setAttribute('class','actplate');const dm=svg.querySelector('rect.dimmer');(dm||els[0]).parentNode.insertBefore(im,dm||els[0])}
    const cx=(x0+x1)/2+(a.ox||0),cy=(y0+y1)/2+(a.oy||0),r=(a.r||Math.max(x1-x0,y1-y0)/2+5),A0=(a.a0??200)*Math.PI/180,A1=(a.a1??470)*Math.PI/180;let d='';for(let i=0;i<=24;i++){const t=A0+(A1-A0)*i/24;d+=(i?' L':'M')+f(cx+r*Math.cos(t))+','+f(cy+r*.55*Math.sin(t))}
    const tx=-Math.sin(A1),ty=Math.cos(A1)*.55,L=Math.hypot(tx,ty),ux=tx/L,uy=ty/L,px=-uy,py=ux,ex=cx+r*Math.cos(A1),ey=cy+r*.55*Math.sin(A1);
    ds.push(d,`M${f(ex-ux*5+px*3.5)},${f(ey-uy*5+py*3.5)} L${f(ex)},${f(ey)} L${f(ex-ux*5-px*3.5)},${f(ey-uy*5-py*3.5)}`);
  }else if(a.t==='hold'||a.t==='rest'){
    els.forEach(e=>e.classList.add('act-'+a.t));return;
  }else if(a.t==='arrow'){
    if(a.pulse)els.forEach(e=>e.classList.add('act-hold'));
    const L=Math.hypot(a.x2-a.x1,a.y2-a.y1)||1,ux=(a.x2-a.x1)/L,uy=(a.y2-a.y1)/L,px=-uy,py=ux,ex=a.x2,ey=a.y2;
    ds.push(`M${f(a.x1)},${f(a.y1)} L${f(ex)},${f(ey)} M${f(ex-ux*5+px*3.5)},${f(ey-uy*5+py*3.5)} L${f(ex)},${f(ey)} L${f(ex-ux*5-px*3.5)},${f(ey-uy*5-py*3.5)}`);
  }else if(a.t==='sound'){
    const n=a.n||3,sp=(a.spread||30)*Math.PI/180,r1=a.r1||6,r2=a.r2||13;
    for(let i=0;i<n;i++){const t=a.ang*Math.PI/180+(i-(n-1)/2)*sp,c=Math.cos(t),s=Math.sin(t);ds.push(`M${f(a.x+c*r1)},${f(a.y+s*r1)} L${f(a.x+c*r2)},${f(a.y+s*r2)}`)}
  }
  const g=document.createElementNS(NS_SVG,'g');g.setAttribute('class','actfx '+a.t);
  for(const cls of ['sh','ln'])for(const d of ds){const p=document.createElementNS(NS_SVG,'path');p.setAttribute('d',d);p.setAttribute('pathLength','1');p.setAttribute('class',cls);g.appendChild(p)}
  svg.appendChild(g);
}
"""

# 1. data + helpers (replace on re-run)
blk = 'const ACT=' + json.dumps(ACT, ensure_ascii=False) + ';'
if 'const ACT=' in h:
    h = re.sub(r'const ACT=\{.*?\};', lambda m: blk, h, count=1, flags=re.S)
else:
    i = h.find('let view=\'lib\',si=0,cur=0,hlTimer;')
    assert i > 0
    h = h[:i] + blk + JS + h[i:]
# 2. light(): add cue, clear on timeout
old = "if(els.length){svg.classList.add('focus');els.forEach(e=>{inflateOrigin(e);e.classList.add('hl')})}"
if 'actFx(svg,[...els]' not in h:
    assert h.count(old) == 1
    h = h.replace(old, "actClear(svg);" + old + "actFx(svg,[...els],actOf(k));", 1)
    old2 = "hlTimer=setTimeout(()=>{svg.classList.remove('focus');"
    assert h.count(old2) == 1
    h = h.replace(old2, "hlTimer=setTimeout(()=>{actClear(svg);svg.classList.remove('focus');", 1)
# 3. text: action class
old = "const cls=['w'];if(known.has(k))cls.push('known');else if(isFirst(k))cls.push('new');"
if "cls.push('act')" not in h:
    assert h.count(old) == 1
    h = h.replace(old, old + "if(actOf(k))cls.push('act');", 1)
# 4. legend + strings
if 'id="lact"' not in h:
    old = '<span><i class="sw seen"></i><span id="lseen">'
    i = h.find(old); j = h.find('</span></span>', i) + len('</span></span>')
    h = h[:j] + '<span><i class="sw act"></i><span id="lact">ação</span></span>' + h[j:]
    h = h.replace("$('lseen').textContent=t.lseen;", "$('lseen').textContent=t.lseen;$('lact').textContent=t.lact;", 1)
    LACT = {'seen before': 'action', 'schon gesehen': 'Handlung', 'już widziane': 'czynność', 'déjà vu': 'action', 'al gezien': 'actie', 'ya vista': 'acción', 'já vista': 'ação'}
    for seen, act in LACT.items():
        h = h.replace(f"lseen:'{seen}'", f"lseen:'{seen}',lact:'{act}'")
# 5. CSS
if '/* action words */' not in h:
    i = h.find('.pic svg .o.k-olha.hl{filter:none;animation:none}')
    assert i > 0
    h = h[:i] + CSS.strip() + '\n' + h[i:]
open(A, 'w').write(h)
print('ok', len(ACT))
