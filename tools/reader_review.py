#!/usr/bin/env python3
"""Add the built-in daily Review (spaced repetition) to the reader, docs/index.html. Idempotent.

What it adds (the project review's flashcard step, the user's choice: built into the reader):
- a Review button in the library header with the number of words due today;
- a review screen (reuses #study): the Portuguese word and its own recording first; "Show" reveals the
  picture close-up and the page sentence with the word in bold; then "Again" or "I knew it";
- words with no picture region (an action flagged as not shown) are set aside for good, so they never block the count;
- scheduling: a word enters the pool once the reader has seen the page where it first appears;
  "I knew it" moves it to the next interval (1, 3, 7, 14, 30, 60, 120, 240 days), "Again" resets it and
  brings it back a few cards later; at most 15 new words a day; due words come first, oldest first;
- progress in state.rev {key: [dueDay, step, lastMillis, introDay]}, saved like the rest of the progress
  (account database when available, else the browser) and merged across devices by the newest change.
"""
from pathlib import Path

P = Path(__file__).resolve().parent.parent / "docs" / "index.html"
s = P.read_text(encoding="utf-8")
if "function renderReview" in s:
    print("review already present")
    raise SystemExit


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (old[:80], s.count(old))
    s = s.replace(old, new)


# --- markup: header button, and a span round the study screen's back link separator
rep('<button type="button" class="langbtn" id="howbtn"',
    '<button type="button" class="langbtn" id="revbtn"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="6" width="14" height="14" rx="2"/><path d="M7 3h12a2 2 0 0 1 2 2v12"/></svg><span id="revbtnl">Review</span><b class="revn" id="revn" hidden></b></button><button type="button" class="langbtn" id="howbtn"')
rep('<button class="linkbtn" id="sback" type="button">← Livro</button> · ',
    '<button class="linkbtn" id="sback" type="button">← Livro</button><span id="sdot"> · </span>')

# --- styles (the page's own <style> block after <body>)
rep(".quiz{display:grid;gap:14px;max-width:560px}",
    ".quiz{display:grid;gap:14px;max-width:560px}\n"
    "#study.revmode .tabs,#study.revmode #sback,#study.revmode #sdot{display:none}\n"
    ".revn{min-width:1.3em;padding:1px 6px;border-radius:999px;background:var(--accent);color:var(--surface);font:700 .75rem var(--f-ui);line-height:1.4;text-align:center}\n"
    ".rvword{margin:4px 0 0}\n"
    ".rvword .linkbtn{display:inline-flex;align-items:center;gap:10px;font:600 2rem var(--f-read,Georgia,serif);color:inherit;text-transform:none;letter-spacing:0}\n"
    ".rvword svg{opacity:.55}\n"
    ".rvsent{margin:0;font:1.05rem/1.55 var(--f-read,Georgia,serif)}\n"
    ".rvsent b{color:var(--accent)}")

# --- strings, six languages
STR = {
    "en": dict(rev="Review", revt="Daily review of the words you have met", revAsk="Do you know what it means? Think, then check.",
               revShow="Show", revAgain="Again", revGood="I knew it", revNone="Nothing to review right now. Read on, or come back tomorrow.",
               revDone="${n} words reviewed. See you tomorrow!", revHint="Words come back after 1, 3, 7, 14… days; a word you miss comes back sooner.",
               revLeft="${n} left",
               help="Review (top of the library) brings back the words you have met, on a schedule: the picture shows the meaning, and words you miss come back sooner."),
    "de": dict(rev="Wiederholen", revt="Tägliche Wiederholung der Wörter, die du schon kennst", revAsk="Weißt du, was es bedeutet? Denk kurz nach, dann prüfe.",
               revShow="Zeigen", revAgain="Nochmal", revGood="Gewusst", revNone="Gerade nichts zu wiederholen. Lies weiter oder komm morgen wieder.",
               revDone="${n} Wörter wiederholt. Bis morgen!", revHint="Wörter kommen nach 1, 3, 7, 14 … Tagen wieder; ein vergessenes Wort kommt früher.",
               revLeft="noch ${n}",
               help="Wiederholen (oben in der Bibliothek) bringt die Wörter, die du schon getroffen hast, nach Plan zurück: das Bild zeigt die Bedeutung, vergessene Wörter kommen früher wieder."),
    "pl": dict(rev="Powtórka", revt="Codzienna powtórka słów, które już znasz", revAsk="Wiesz, co znaczy? Pomyśl, a potem sprawdź.",
               revShow="Pokaż", revAgain="Jeszcze raz", revGood="Znam", revNone="Na razie nie ma nic do powtórki. Czytaj dalej albo wróć jutro.",
               revDone="Powtórzone słowa: ${n}. Do jutra!", revHint="Słowa wracają po 1, 3, 7, 14… dniach; zapomniane słowo wraca szybciej.",
               revLeft="zostało ${n}",
               help="Powtórka (na górze biblioteki) przypomina poznane słowa według planu: obrazek pokazuje znaczenie, a zapomniane słowa wracają szybciej."),
    "fr": dict(rev="Réviser", revt="Révision quotidienne des mots déjà rencontrés", revAsk="Sais-tu ce qu’il veut dire ? Réfléchis, puis vérifie.",
               revShow="Afficher", revAgain="Encore", revGood="Je savais", revNone="Rien à réviser pour l’instant. Lis la suite ou reviens demain.",
               revDone="${n} mots révisés. À demain !", revHint="Les mots reviennent après 1, 3, 7, 14… jours ; un mot oublié revient plus tôt.",
               revLeft="encore ${n}",
               help="Réviser (en haut de la bibliothèque) ramène les mots déjà rencontrés selon un calendrier : l’image montre le sens, et les mots oubliés reviennent plus tôt."),
    "nl": dict(rev="Herhalen", revt="Dagelijkse herhaling van woorden die je al tegenkwam", revAsk="Weet je wat het betekent? Denk even na en kijk dan.",
               revShow="Toon", revAgain="Opnieuw", revGood="Wist ik", revNone="Nu niets te herhalen. Lees verder of kom morgen terug.",
               revDone="${n} woorden herhaald. Tot morgen!", revHint="Woorden komen terug na 1, 3, 7, 14… dagen; een vergeten woord komt eerder terug.",
               revLeft="nog ${n}",
               help="Herhalen (bovenaan de bibliotheek) brengt de woorden die je al tegenkwam volgens schema terug: het plaatje toont de betekenis, vergeten woorden komen eerder terug."),
    "es": dict(rev="Repasar", revt="Repaso diario de las palabras que ya has visto", revAsk="¿Sabes qué significa? Piénsalo y compruébalo.",
               revShow="Mostrar", revAgain="Otra vez", revGood="La sabía", revNone="Nada que repasar ahora. Sigue leyendo o vuelve mañana.",
               revDone="${n} palabras repasadas. ¡Hasta mañana!", revHint="Las palabras vuelven tras 1, 3, 7, 14… días; una palabra olvidada vuelve antes.",
               revLeft="quedan ${n}",
               help="Repasar (arriba en la biblioteca) te trae las palabras que ya has visto según un plan: la imagen muestra el significado y las palabras olvidadas vuelven antes."),
}


def js(v):
    return "'" + v.replace("\\", "\\\\").replace("'", "\\'") + "'"


for lang, d in STR.items():
    head = f"\n {lang}:{{stop:"
    i = s.index(head)
    fields = "".join(f"{k}:{js(v)}," for k, v in d.items() if k not in ("revDone", "revLeft", "help"))
    fields += f"revDone:n=>`{d['revDone']}`,revLeft:n=>`{d['revLeft']}`,"
    s = s[:i] + f"\n {lang}:{{" + fields + "stop:" + s[i + len(head):]
    # one help line, appended to this language's help list
    h = s.index("help:[", i)
    depth, k = 0, h + 5
    while True:
        c = s[k]
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                break
        elif c in "\"'`":
            q = c
            k += 1
            while s[k] != q:
                k += 2 if s[k] == "\\" else 1
        k += 1
    s = s[:k] + "," + js(d["help"]) + s[k:]

# --- progress merge keeps the newest review entry per word
rep("auto:(b.auto!==undefined?b.auto:a.auto),miss:(b.miss!==undefined?b.miss:(a.miss||[]))}}",
    "auto:(b.auto!==undefined?b.auto:a.auto),miss:(b.miss!==undefined?b.miss:(a.miss||[])),rev:revMerge(a.rev,b.rev)}}\n"
    "function revMerge(a,b){const r={...(a||{})};for(const [k,v] of Object.entries(b||{}))if(!r[k]||(v[2]||0)>(r[k][2]||0))r[k]=v;return r}")

# --- the review itself
rep("function renderLib(){",
    r"""// ---------- Review: spaced repetition of the words the reader has met ----------
const RV_I=[1,3,7,14,30,60,120,240],RV_NEW=15;let rv=null;
const rvDay=()=>{const d=new Date();return Math.floor((d.getTime()-d.getTimezoneOffset()*6e4)/864e5)};
function revQueue(){const R=state.rev||{},d=rvDay(),due=[],fresh=[];
  for(const k of ALL){const f=first[k];if(!(state.seen[STORIES[f.s].id]||[]).includes(f.p))continue;const r=R[k];if(r){if(r[0]<=d)due.push(k)}else fresh.push(k)}
  const intro=Object.values(R).filter(r=>r[3]===d&&r[1]>=0).length;
  due.sort((a,b)=>R[a][0]-R[b][0]||first[a].s-first[b].s||first[a].p-first[b].p);
  fresh.sort((a,b)=>first[a].s-first[b].s||first[a].p-first[b].p);
  return [...due,...fresh.slice(0,Math.max(0,RV_NEW-intro))]}
function updRevBtn(){const n=revQueue().length,b=$('revn');if(!b)return;b.hidden=!n;b.textContent=n>99?'99+':String(n)}
function renderReview(){echoHide();readTok++;narrStop();try{speechSynthesis.cancel()}catch(e){}
  if(!rv||rv.day!==rvDay())rv={q:revQueue(),done:0,shown:false,day:rvDay()};
  const need=[...new Set(rv.q.map(k=>STORIES[first[k].s].id))].filter(id=>typeof loadBook==='function'&&!PHOTOS[id+':0']);
  if(need.length){Promise.all(need.map(loadBook)).then(renderReview,()=>{});return}
  {const R=state.rev=state.rev||{},d=rvDay();let gone=0;rv.q=rv.q.filter(k=>{if(cropOf(first[k].s,first[k].p,k))return true;R[k]=[1e9,-1,Date.now(),d];gone++;return false});if(gone)save()}
  view='review';$('lib').hidden=true;$('reader').hidden=true;$('study').hidden=false;$('study').classList.add('revmode');document.body.classList.remove('spreadmode');
  $('stitle').textContent=T().rev;$('slib').textContent=T().slib;drawReview();window.scrollTo({top:0})}
function drawReview(){const t=T(),r=rv;
  if(!r.q.length){$('sbody').innerHTML=`<div class="quiz"><p class="qdone">${r.done?t.revDone(r.done):t.revNone}</p><p class="shint">${t.revHint}</p><div><button class="btn primary" type="button" id="rvlib">${t.slib}</button></div></div>`;return}
  const k=r.q[0],f=first[k],crop=cropOf(f.s,f.p,k);
  const sent=STORIES[f.s].pages[f.p].replace(RX,(m,w,kk)=>kk===k?`<b>${w}</b>`:w);
  const spk=`<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M11 5 6 9H2v6h4l5 4z"/><path d="M15.5 8.5a5 5 0 0 1 0 7"/><path d="M19 5a10 10 0 0 1 0 14"/></svg>`;
  $('sbody').innerHTML=`<div class="quiz"><div class="qbar"><span>${t.revLeft(r.q.length)}</span><span>${t.book(f.s+1)}</span></div>
   <p class="rvword" lang="pt-PT"><button type="button" class="linkbtn" id="rvsay">${label[k]}${spk}</button></p>
   ${r.shown?`<span class="crop" style="${crop}"></span><p class="rvsent" lang="pt-PT">${sent}</p>
   <div class="qopts"><button class="btn" type="button" data-rv="0">${t.revAgain}</button><button class="btn primary" type="button" data-rv="1">${t.revGood}</button></div>`
   :`<p class="shint">${t.revAsk}</p><div><button class="btn primary" type="button" id="rvshow">${t.revShow}</button></div>`}</div>`;
  if(!r.shown)clipPlay(f.s,f.p,k)}
function rvGrade(ok){const k=rv.q.shift(),R=state.rev=state.rev||{},d=rvDay(),o=R[k]||[d,0,0,d];
  if(ok){R[k]=[d+RV_I[Math.min(o[1],RV_I.length-1)],o[1]+1,Date.now(),o[3]];rv.done++}
  else{R[k]=[d,0,Date.now(),o[3]];rv.q.splice(Math.min(3,rv.q.length),0,k)}
  rv.shown=false;save();drawReview()}
function renderLib(){""")
rep("  $('libmeter').innerHTML=T().libm(ALL.filter(k=>known.has(k)).length,ALL.length);\n}",
    "  $('libmeter').innerHTML=T().libm(ALL.filter(k=>known.has(k)).length,ALL.length);\n  $('study').classList.remove('revmode');updRevBtn();\n}")
# leaving the review for the book's study screen shows its tabs and back link again
rep("view='study';stab=tab||stab;", "view='study';stab=tab||stab;$('study').classList.remove('revmode');")

# --- clicks, language
rep("  const qa=e.target.closest('[data-qa]');if(qa){answer(qa.dataset.qa);return}",
    "  const qa=e.target.closest('[data-qa]');if(qa){answer(qa.dataset.qa);return}\n"
    "  if(e.target.closest('#revbtn')){rv=null;renderReview();return}\n"
    "  if(e.target.closest('#rvshow')){rv.shown=true;drawReview();return}\n"
    "  if(e.target.closest('#rvsay')){const k=rv.q[0];if(k)clipPlay(first[k].s,first[k].p,k);return}\n"
    "  const rg=e.target.closest('[data-rv]');if(rg){rvGrade(rg.dataset.rv==='1');return}\n"
    "  if(e.target.closest('#rvlib')){renderLib();return}")
rep("$('howbtnl').textContent=t.howbtn;",
    "$('howbtnl').textContent=t.howbtn;$('revbtnl').textContent=t.rev;$('revbtn').title=t.revt;")
rep("if(view==='lib')renderLib();else if(view==='study')renderStudy();else renderPage()}",
    "if(view==='lib')renderLib();else if(view==='study')renderStudy();else if(view==='review'){$('stitle').textContent=T().rev;$('slib').textContent=T().slib;drawReview()}else renderPage()}")

P.write_text(s, encoding="utf-8")
print("review added")
