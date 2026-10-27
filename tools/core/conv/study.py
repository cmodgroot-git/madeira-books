"""Per-book picture word list + picture quiz (study view)."""
A='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4/index.html'
h=open(A).read()
CSS="""
/* study view: picture words + quiz */
#study .tabs{display:flex;gap:8px;flex-wrap:wrap}
#study .tabs .btn[aria-selected="true"]{background:var(--accent);color:var(--surface)}
.shint{color:var(--muted);font:500 .9rem var(--f-ui);margin:0}
.wgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px}
.wcard{display:grid;gap:6px;border:1px solid var(--line);border-radius:12px;background:var(--surface);padding:8px;cursor:pointer;text-align:left;font:inherit;color:inherit;-webkit-touch-callout:none;user-select:none}
.wcard:hover{border-color:var(--accent)}
.crop{aspect-ratio:4/3;border-radius:8px;background-repeat:no-repeat;background-color:#EDE6D8}
.wcard b{font:600 1.05rem var(--f-read,Georgia,serif)}
.wcard small{color:var(--muted);font:500 .75rem var(--f-ui)}
.wcard.playing{border-color:var(--new);box-shadow:0 0 0 2px var(--new-soft)}
.quiz{display:grid;gap:14px;max-width:560px}
.quiz .crop{aspect-ratio:4/3;width:100%;border-radius:12px}
.qopts{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.qopts .btn{justify-content:center;font:600 1.05rem var(--f-read,Georgia,serif);text-transform:none;letter-spacing:0;padding:12px}
.qopts .btn.ok{background:var(--known);border-color:var(--known);color:#fff}
.qopts .btn.no{background:#B4533A;border-color:#B4533A;color:#fff}
.qbar{display:flex;justify-content:space-between;align-items:center;color:var(--muted);font:600 .85rem var(--f-ui)}
.qdone{font:600 1.4rem var(--f-read,Georgia,serif)}
"""
if '/* study view' not in h:
    i=h.find('</style>'); h=h[:i]+CSS+h[i:]
HTML="""
  <section id="study" hidden>
    <div style="display:grid;gap:18px">
      <header>
        <div>
          <p class="sub"><button class="linkbtn" id="sback" type="button">← Livro</button> · <button class="linkbtn" id="slib" type="button">Biblioteca</button></p>
          <h1 id="stitle"></h1>
        </div>
        <div class="tabs" role="tablist"><button class="btn" id="tabw" role="tab" type="button">Palavras</button><button class="btn" id="tabq" role="tab" type="button">Quiz</button></div>
      </header>
      <div id="sbody"></div>
    </div>
  </section>
"""
if 'id="study"' not in h:
    i=h.find('  <details>'); h=h[:i]+HTML+h[i:]
# reader header: a link to the study view
if 'id="tostudy"' not in h:
    h=h.replace('<button class="linkbtn" id="back" type="button">← Biblioteca</button><span id="bookno"></span>','<button class="linkbtn" id="back" type="button">← Biblioteca</button><span id="bookno"></span> · <button class="linkbtn" id="tostudy" type="button">Palavras e quiz</button>',1)
STR={'en':("Words & quiz","Words","Quiz","Which word matches the picture?","right","Again","← Book","Library","Tap a word to hear it. Long-press for its meaning.","Words you missed before come back here."),
 'de':("Wörter & Quiz","Wörter","Quiz","Welches Wort passt zum Bild?","richtig","Nochmal","← Buch","Bibliothek","Tippe auf ein Wort, um es zu hören. Lange drücken zeigt die Bedeutung.","Wörter, die du verpasst hast, kommen hier wieder."),
 'fr':("Mots & quiz","Mots","Quiz","Quel mot correspond à l’image ?","justes","Encore","← Livre","Bibliothèque","Touche un mot pour l’entendre. Appui long pour son sens.","Les mots manqués reviennent ici."),
 'es':("Palabras y test","Palabras","Test","¿Qué palabra corresponde a la imagen?","correctas","Otra vez","← Libro","Biblioteca","Toca una palabra para oírla. Mantén pulsado para ver su significado.","Las palabras que fallaste vuelven aquí."),
 'nl':("Woorden & quiz","Woorden","Quiz","Welk woord past bij de afbeelding?","goed","Nog eens","← Boek","Bibliotheek","Tik op een woord om het te horen. Lang indrukken toont de betekenis.","Woorden die je miste komen hier terug."),
 'pl':("Słowa i quiz","Słowa","Quiz","Które słowo pasuje do obrazka?","poprawnie","Jeszcze raz","← Książka","Biblioteka","Dotknij słowa, aby je usłyszeć. Przytrzymaj, aby zobaczyć znaczenie.","Słowa, które pominąłeś, wracają tutaj.")}
for L,(st,w,q,qw,ok,ag,tb,lib,wh,mh) in STR.items():
    key=f" {L}:{{lib:"
    i=h.find(key)
    assert i>0,L
    if 'study:' in h[i:i+200]: continue
    ins=f" {L}:{{study:'{st}',swords:'{w}',squiz:'{q}',qwhich:'{qw}',qscore:(a,b)=>`${{a}} / ${{b}} {ok}`,again:'{ag}',toBook:'{tb}',slib:'{lib}',whint:'{wh}',mhint:'{mh}',lib:"
    h=h[:i]+ins+h[i+len(key):]
JS=r"""
// ---------- study view: picture words + quiz ----------
const photoOf=(sid,p)=>{const ph=PHOTOS[sid+':'+p];return ph?ph.svg():''};
function cropOf(s,p,k){
  const svg=photoOf(STORIES[s].id,p);const im=(svg.match(/id="[^"]*ph" href="([^"]+)"/)||[])[1];if(!im)return null;
  let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;
  for(const m of svg.matchAll(/<g class="o ([^"]*)"><use[^>]*\/><rect class="bb" x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"/g)){
    if(!m[1].split(' ').includes('k-'+k))continue;const x=+m[2],y=+m[3],w=+m[4],hh=+m[5];x0=Math.min(x0,x);y0=Math.min(y0,y);x1=Math.max(x1,x+w);y1=Math.max(y1,y+hh)}
  if(x1<x0)return null;
  const W=465.8,H=260;let w=x1-x0,hh=y1-y0,cx=(x0+x1)/2,cy=(y0+y1)/2;
  w=Math.max(w*1.35,60);hh=Math.max(hh*1.35,45);if(w/hh>4/3)hh=w*3/4;else w=hh*4/3;
  if(w>W){w=W;hh=w*3/4}if(hh>H){hh=H;w=hh*4/3}
  let x=Math.min(Math.max(cx-w/2,0),W-w),y=Math.min(Math.max(cy-hh/2,0),H-hh);
  return `background-image:url('${im}');background-size:${(W/w*100).toFixed(2)}% auto;background-position:${(W-w?x/(W-w)*100:0).toFixed(2)}% ${(H-hh?y/(H-hh)*100:0).toFixed(2)}%`}
function pageEls(p){const ks=[];let last=0;p.replace(RX,(m,w,k,off)=>{for(const _ of p.slice(last,off).matchAll(WRX))ks.push(null);ks.push(k);last=off+m.length;return m});for(const _ of p.slice(last).matchAll(WRX))ks.push(null);return ks}
function clipPlay(s,p,k){
  const T=NARR[STORIES[s].id+':'+p],idx=pageEls(STORIES[s].pages[p]).indexOf(k);
  if(!T||idx<0||!T[idx]){speak(label[k]);return}
  if(!narrA)narrA=new Audio();readTok++;narrStop();try{speechSynthesis.cancel()}catch(e){}
  const [a,b]=T[idx];narrA.src=`audio/b${s+1}p${p+1}.mp3`;narrA.playbackRate=1;
  const go=()=>{narrA.currentTime=Math.max(0,a/1000-.04);const pr=narrA.play();if(pr&&pr.catch)pr.catch(()=>{});
    const stopAt=b/1000+.08,chk=()=>{if(narrA.currentTime>=stopAt||narrA.paused){narrA.pause();return}narrRAF=requestAnimationFrame(chk)};narrRAF=requestAnimationFrame(chk)};
  if(narrA.readyState>=1&&narrA.src.endsWith(`b${s+1}p${p+1}.mp3`))go();else narrA.addEventListener('loadedmetadata',go,{once:true})}
let stab='w',quiz=null;
const bookWords=s=>storyKeys[s].filter(k=>first[k].s===s).map(k=>({s,p:first[k].p,k,crop:cropOf(s,first[k].p,k)})).filter(w=>w.crop);
function renderStudy(tab){
  view='study';stab=tab||stab;readTok++;narrStop();
  $('lib').hidden=true;$('reader').hidden=true;$('study').hidden=false;document.body.classList.remove('spreadmode');
  const t=T();$('stitle').textContent=STORIES[si].title;$('sback').textContent=t.toBook;$('slib').textContent=t.slib;$('tabw').textContent=t.swords;$('tabq').textContent=t.squiz;
  $('tabw').setAttribute('aria-selected',String(stab==='w'));$('tabq').setAttribute('aria-selected',String(stab==='q'));
  if(stab==='w'){
    const ws=bookWords(si);
    $('sbody').innerHTML=`<p class="shint">${t.whint}</p><div class="wgrid">`+ws.map(w=>`<button type="button" class="wcard" data-sk="${w.k}" data-sp="${w.p}" data-say="${w.k}"><span class="crop" style="${w.crop}"></span><b lang="pt-PT">${label[w.k]}</b><small>${t.page(w.p+1)}</small></button>`).join('')+'</div>';
  } else { if(!quiz||quiz.s!==si)newQuiz(); drawQuiz() }
  window.scrollTo({top:0});
}
function shuffle(a){for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a}
function newQuiz(){
  const mine=shuffle(bookWords(si)),miss=(state.miss||[]).filter(k=>first[k]&&first[k].s!==si).slice(0,2)
    .map(k=>({s:first[k].s,p:first[k].p,k,crop:cropOf(first[k].s,first[k].p,k)})).filter(w=>w.crop);
  const qs=shuffle([...miss,...mine.slice(0,8-miss.length)]);
  quiz={s:si,qs:qs.map(w=>{const pool=shuffle(bookWords(w.s).filter(x=>x.k!==w.k&&label[x.k]!==label[w.k])).slice(0,3);return {...w,opts:shuffle([w,...pool].map(x=>x.k))}}),i:0,right:0,ans:null}}
function drawQuiz(){
  const t=T(),q=quiz;
  if(q.i>=q.qs.length){$('sbody').innerHTML=`<div class="quiz"><p class="qdone">${t.qscore(q.right,q.qs.length)}</p><p class="shint">${t.mhint}</p><div><button class="btn primary" type="button" id="qagain">${t.again}</button></div></div>`;return}
  const w=q.qs[q.i];
  $('sbody').innerHTML=`<div class="quiz"><div class="qbar"><span>${q.i+1} / ${q.qs.length}</span><span>${t.qscore(q.right,q.i)}</span></div>
   <span class="crop" style="${w.crop}"></span><p class="shint">${t.qwhich}</p>
   <div class="qopts">${w.opts.map(k=>`<button type="button" class="btn${q.ans?(k===w.k?' ok':k===q.ans?' no':''):''}" data-qa="${k}" lang="pt-PT"${q.ans?' disabled':''}>${label[k]}</button>`).join('')}</div>
   ${q.ans?`<div><button class="btn primary" type="button" id="qnext">${t.next}</button></div>`:''}</div>`}
function answer(k){
  const q=quiz,w=q.qs[q.i];if(q.ans)return;q.ans=k;
  const m=new Set(state.miss||[]);if(k===w.k){q.right++;m.delete(w.k)}else m.add(w.k);state.miss=[...m];save();
  clipPlay(w.s,w.p,w.k);drawQuiz()}
"""
if 'function renderStudy' not in h:
    i=h.find('function renderLib(){'); h=h[:i]+JS.lstrip()+h[i:]
# clicks
old="  const w=e.target.closest('.w');if(w){"
new="  const sc=e.target.closest('[data-sk]');if(sc){if(Date.now()-lpAt<700)return;document.querySelectorAll('.wcard.playing').forEach(x=>x.classList.remove('playing'));sc.classList.add('playing');clipPlay(si,+sc.dataset.sp,sc.dataset.sk);return}\n  const qa=e.target.closest('[data-qa]');if(qa){answer(qa.dataset.qa);return}\n  if(e.target.closest('#qnext')){quiz.i++;quiz.ans=null;drawQuiz();return}\n  if(e.target.closest('#qagain')){newQuiz();drawQuiz();return}\n"+old
if "closest('[data-sk]')" not in h:
    assert h.count(old)==1; h=h.replace(old,new,1)
# buttons
old="$('say').onclick=toggleRead;"
if "$('tostudy').onclick" not in h:
    h=h.replace(old,"$('tostudy').onclick=()=>{try{speechSynthesis.cancel()}catch(e){}renderStudy('w')};$('sback').onclick=()=>go(si,cur);$('slib').onclick=renderLib;$('tabw').onclick=()=>renderStudy('w');$('tabq').onclick=()=>renderStudy('q');\n"+old,1)
# last page -> words & quiz
old="$('next').onclick=()=>{if(cur===STORIES[si].pages.length-1)renderLib();else go(si,cur+1)};"
if old in h: h=h.replace(old,"$('next').onclick=()=>{if(cur===STORIES[si].pages.length-1){readTok++;narrStop();try{speechSynthesis.cancel()}catch(e){}quiz=null;renderStudy('q')}else go(si,cur+1)};")
h=h.replace("$('next').textContent=last?T().done:T().next;","$('next').textContent=last?T().squiz+' →':T().next;")
# library view hides study; strings
h=h.replace("view='lib';$('lib').hidden=false;$('reader').hidden=true;","view='lib';$('lib').hidden=false;$('reader').hidden=true;$('study').hidden=true;")
h=h.replace("view='read';$('lib').hidden=true;$('reader').hidden=false;","view='read';$('lib').hidden=true;$('reader').hidden=false;$('study').hidden=true;")
h=h.replace("$('back').textContent=t.back;$('tiles')","$('back').textContent=t.back;$('tostudy').textContent=t.study;$('tiles')")
h=h.replace("function setLang(id){state.lang=id;save();applyLang();closeLang();if(view==='lib')renderLib();else renderPage()}","function setLang(id){state.lang=id;save();applyLang();closeLang();if(view==='lib')renderLib();else if(view==='study')renderStudy();else renderPage()}")
# long-press / ctrl-click on study cards shows meaning (they carry data-say)
open(A,'w').write(h); print('ok')
