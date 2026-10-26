#!/usr/bin/env python3
"""Add book 16 (golfe, «Com os Pés no Chão») and the echo feature to docs/index.html.
Idempotent: each step checks whether it has already been applied.
  build16.py text      # pages16, STORIES, GLOSS, NOT_SHOWN, UI, echo code+CSS+data
"""
import json,os,re,sys
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.abspath(os.path.join(HERE,'..','..'))
DOC=os.path.join(ROOT,'docs'); HTML=os.path.join(DOC,'index.html')
WORK=os.environ.get('WORK','/tmp/claude-0/-home-user-madeira-books/11c1ecef-e1df-5fad-8f8e-68eb719ae5fc/scratchpad/b16')
sys.path.insert(0,HERE)
from echo16 import ECHO
SID,TITLE,COVER='golfe','Com os Pés no Chão',4
def rd(): return open(HTML,encoding='utf8').read()
def wr(s): open(HTML,'w',encoding='utf8').write(s)
def once(s,old,new,mark):
    if mark in s: return s
    assert s.count(old)==1,(old[:60],s.count(old)); return s.replace(old,new)
def json_const(s,name):
    i=s.index(name+'=')+len(name)+1; d=json.JSONDecoder(); v,end=d.raw_decode(s,i); return v,i,end
def set_json_const(s,name,v):
    _,i,end=json_const(s,name); return s[:i]+json.dumps(v,ensure_ascii=False)+s[end:]
QECHO={'Which word matches the picture?':'Which sentence reports these words?','Welches Wort passt zum Bild?':'Welcher Satz gibt diese Worte wieder?',
 'Które słowo pasuje do obrazka?':'Które zdanie przytacza te słowa?','Quel mot correspond à l’image ?':'Quelle phrase rapporte ces paroles ?',
 'Welk woord past bij de afbeelding?':'Welke zin geeft deze woorden weer?','¿Qué palabra corresponde a la imagen?':'¿Qué frase cuenta estas palabras?'}
def text(s):
    P=json.load(open(f'{WORK}/pages16.json',encoding='utf8'))
    i=s.index('const pages15=['); j=s.index('\n];',i)+3
    s=once(s,s[i:j],s[i:j]+'\n\nconst pages16=[\n'+',\n'.join(json.dumps(p,ensure_ascii=False) for p in P)+'\n];','const pages16=[')
    s=once(s,"pages:pages15,cover:6},\n","pages:pages15,cover:6},\n  {id:'golfe',title:'Com os Pés no Chão',cams:[],scenes:pages16.map(()=>()=>''),pages:pages16,cover:%d},\n"%COVER,"id:'golfe'")
    G,_,_=json_const(s,'const GLOSS'); G.update(json.load(open(f'{WORK}/gloss16.json',encoding='utf8')))
    for v in ECHO.values():
        for e in v: G[e['id']]=e['g']
    s=set_json_const(s,'const GLOSS',G)
    N,_,_=json_const(s,'const NOT_SHOWN'); N['golfe:6']=['respira']; s=set_json_const(s,'const NOT_SHOWN',N)
    for a,b in QECHO.items():
        old="qwhich:'%s',"%a
        if s.count(old)==1: s=s.replace(old,old+"qecho:'%s',"%b.replace("'","\\'"))
    css=open(f'{HERE}/echo.css',encoding='utf8').read()
    s=once(s,'/* action words */',css+'/* action words */','/* echoes: a reported line')
    data={k:[{x:e[x] for x in ('id','ph','o','pairs')} for e in v] for k,v in ECHO.items()}
    js=open(f'{HERE}/echo.js',encoding='utf8').read().replace('__ECHO__',json.dumps(data,ensure_ascii=False))
    if 'const ECHO=' in s: s=re.sub(r'const ECHO=\{.*?\};',lambda m:'const ECHO='+json.dumps(data,ensure_ascii=False)+';',s,count=1,flags=re.S)
    else: s=once(s,'function renderPage(){',js+'\nfunction renderPage(){','const ECHO=')
    s=once(s,"$('title').hidden=cur===0;","echoWrap();$('title').hidden=cur===0;","echoWrap();$('title')")
    s=once(s,"const w=e.target.closest('.w');if(w){","const ec=e.target.closest('.echo');if(ec){if(Date.now()-lpAt<700)return;echoShow(ec);return}\n  const w=e.target.closest('.w');if(w){","closest('.echo');if(ec){")
    s=s.replace("closest('.w,[data-say]')","closest('.w,[data-say],.echo')").replace("t.dataset.k||t.dataset.say;","t.dataset.k||t.dataset.say||t.dataset.eco;")
    s=once(s,"el.classList.add('say-on');readLast=el;","el.classList.add('say-on');readLast=el;\n  {const ec=el.closest('.echo');if(ec&&state.slow&&ec!==echoLast){echoLast=ec;echoShow(ec,{audio:false})}}","echoLast=ec;echoShow")
    s=once(s,"readLast=null;$('say').classList.remove('reading')}","readLast=null;echoLast=null;$('say').classList.remove('reading')}","echoLast=null;$('say')")
    s=once(s,",i:0,right:0,ans:null}}\nfunction drawQuiz",",i:0,right:0,ans:null};echoQuiz()}\nfunction echoQuiz(){const id=STORIES[quiz.s].id,all=Object.entries(ECHO).filter(([k])=>k.split(':')[0]===id).flatMap(([,v])=>v);if(all.length<3)return;\n  const e=all[Math.floor(Math.random()*all.length)],opts=shuffle([e,...shuffle(all.filter(x=>x!==e)).slice(0,2)]).map(x=>x.id);\n  quiz.qs.splice(1+Math.floor(Math.random()*quiz.qs.length),0,{echo:e.id,opts})}\nfunction drawQuiz","function echoQuiz(")
    s=once(s,"  const w=q.qs[q.i];\n  $('sbody').innerHTML=`<div class=\"quiz\">","  const w=q.qs[q.i];\n  if(w.echo){const e=echoOf(w.echo);$('sbody').innerHTML=`<div class=\"quiz\"><div class=\"qbar\"><span>${q.i+1} / ${q.qs.length}</span><span>${t.qscore(q.right,q.i+(q.ans?1:0))}</span></div><span class=\"ebub\" lang=\"pt-PT\">«${e.o}»</span><p class=\"shint\">${t.qecho||t.qwhich}</p><div class=\"qopts\">${w.opts.map(id=>`<button type=\"button\" class=\"btn eopt${q.ans?(id===w.echo?' ok':id===q.ans?' no':''):''}\" data-qa=\"${id}\" lang=\"pt-PT\"${q.ans?' disabled':''}>${echoOf(id).ph}</button>`).join('')}</div>${q.ans?`<div><button class=\"btn primary\" type=\"button\" id=\"qnext\">${t.next}</button></div>`:''}</div>`;return}\n  $('sbody').innerHTML=`<div class=\"quiz\">","if(w.echo){const e=echoOf(w.echo)")
    s=once(s,"const q=quiz,w=q.qs[q.i];if(q.ans)return;q.ans=k;\n","const q=quiz,w=q.qs[q.i];if(q.ans)return;q.ans=k;\n  if(w.echo){if(k===w.echo)q.right++;wordClip(echoOf(w.echo).o);drawQuiz();return}\n","if(w.echo){if(k===w.echo)q.right++")
    for fn in ('function renderPage(){','function renderStudy(','function renderLib(){'):
        j=s.index(fn); k=s.index('{',j+len(fn)-1) if fn.endswith('(') else j+len(fn)-1
        if not s[k+1:].startswith('echoHide();'): s=s[:k+1]+'echoHide();'+s[k+1:]
    return s

# ---------------- media and data ----------------
import hashlib,subprocess,shutil
from PIL import Image
def h10(path): return hashlib.sha1(open(path,'rb').read()).hexdigest()[:10]
def hashed(tmp,dirn,ext):
    hp=h10(tmp); dst=os.path.join(DOC,dirn,f'{SID}.{hp}.{ext}')
    for f in os.listdir(os.path.join(DOC,dirn)):
        if f.startswith(SID+'.') and f!=os.path.basename(dst): os.remove(os.path.join(DOC,dirn,f))
    shutil.copy(tmp,dst); return f'{dirn}/{SID}.{hp}.{ext}'
ECOKEYS={i:' '.join(e['id'] for e in ECHO.get(f'{SID}:{i}',[])) for i in range(8)}
LIFE={int(k):v for k,v in json.load(open(f'{WORK}/life16.json')).items()} if os.path.exists(f'{WORK}/life16.json') else {}   # page -> animation layer (life16.py)
def photos_js():
    sys.path.insert(0,HERE); import hlmask
    ents=[]
    for i in range(8):
        p=f'{SID}{i}'; defs=[]; groups=[]
        for j,(keys,m) in enumerate(hlmask.load(i)):
            b64,(x0,y0,x1,y1),(bx0,by0,bx1,by1)=hlmask.mask_png(m)
            sx,sy=465.8/1600,260/898; X,Y,Wd,Ht=x0*sx,y0*sy,(x1-x0)*sx,(y1-y0)*sy
            defs.append(f'<mask id="{p}m{j}" maskUnits="userSpaceOnUse" x="{X:.1f}" y="{Y:.1f}" width="{Wd:.1f}" height="{Ht:.1f}"><image href="data:image/png;base64,{b64}" x="{X:.1f}" y="{Y:.1f}" width="{Wd:.1f}" height="{Ht:.1f}" preserveAspectRatio="none"/></mask>')
            k=ECOKEYS[i] if keys=='eco' else keys
            groups.append("${o('"+k+"',`<use href=\"#"+p+"ph\" mask=\"url(#"+p+f"m{j})\"/><rect class=\"bb\" x=\"{bx0*sx:.1f}\" y=\"{by0*sy:.1f}\" width=\"{(bx1-bx0)*sx:.1f}\" height=\"{(by1-by0)*sy:.1f}\" fill=\"none\"/>`)}}")
        life=LIFE.get(i,'')
        svg=f'<defs>{"".join(defs)}</defs><image id="{p}ph" href="img/b16p{i+1}.jpg" x="0" y="0" width="465.8" height="260" preserveAspectRatio="none"/>{life}<rect class="dimmer" x="0" y="0" width="465.8" height="260" fill="#1B1512"/>'+''.join(groups)
        ents.append(f"'{SID}:{i}':{{w:465.8,svg:()=>`{svg}`}}")
    js='__PHB(function(){return {'+',\n'.join(ents)+'}});\n'
    tmp=f'{WORK}/photos_{SID}.js'; open(tmp,'w',encoding='utf8').write(js); return hashed(tmp,'photos','js')
def media(s):
    M=f'{WORK}/masters'; T=f'{WORK}/build'; os.makedirs(T,exist_ok=True)
    thumbs=[]
    for n in range(1,9):
        im=Image.open(f'{M}/b16p{n}.jpg').convert('RGB'); pub=im.resize((1200,674),Image.LANCZOS); pub.save(f'{DOC}/img/b16p{n}.jpg',quality=86,optimize=True)
        thumbs.append(pub.resize((192,108),Image.LANCZOS))
    strip=Image.new('RGB',(192*8,108)); [strip.paste(t,(192*k,0)) for k,t in enumerate(thumbs)]; strip.save(f'{T}/strip.webp',quality=72,method=6)
    Image.open(f'{DOC}/img/b16p{COVER+1}.jpg').resize((720,404),Image.LANCZOS).save(f'{T}/cover.webp',quality=80,method=6)
    A=f'{WORK}/audio'; sil=f'{A}/clips/_sil3.mp3'
    subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','anullsrc=r=24000:cl=mono','-t','0.3','-b:a','48k',sil],check=True)
    def dur(f): return float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f],capture_output=True,text=True).stdout)
    L=[];off=[];end=[];t=0.0
    for n in range(1,9):
        f=f'{A}/out/b16p{n}.mp3'
        if n>1: L.append(f"file '{sil}'"); t+=dur(sil)
        L.append(f"file '{f}'"); off.append(round(t,2)); t+=dur(f); end.append(round(t,2))
    open(f'{T}/narr.txt','w').write('\n'.join(L))
    subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',f'{T}/narr.txt','-c','copy',f'{T}/narr.mp3'],check=True)
    narr=hashed(f'{T}/narr.mp3','audio/book','mp3'); strip=hashed(f'{T}/strip.webp','img/t/book','webp'); cover=hashed(f'{T}/cover.webp','img/c','webp')
    phf=photos_js()
    shutil.copy(f'{A}/clips/words.mp3',f'{DOC}/audio/words.mp3'); shutil.copy(f'{A}/clips/titles.mp3',f'{DOC}/audio/titles.mp3')
    # data
    s=re.sub(r"(COVER_IMG=\{.*?)(,golfe:'[^']*')?\};",lambda m:m.group(1)+f",golfe:'{cover}'"+'};',s,count=1)
    i=s.index('PHF=')+4; v,e=json.JSONDecoder().raw_decode(s,i); v[SID]=phf; s=s[:i]+json.dumps(v,ensure_ascii=False)+s[e:]
    i=s.index('const PACK=')+11; v,e=json.JSONDecoder().raw_decode(s,i); v['narr'][SID]={'src':narr,'off':off,'end':end}; v['thumbs'][SID]=strip; s=s[:i]+json.dumps(v,ensure_ascii=False,separators=(',',':'))+s[e:]
    N=json.load(open(f'{A}/narr16.json')); C=json.load(open(f'{A}/clips16.json'))
    for name,new in [('const NARR',N),('const WCLIP',C['WCLIP']),('const TCLIP',C['TCLIP']),('const TWORDS',C['TWORDS'])]:
        v,_,_=json_const(s,name); v.update(new); s=set_json_const(s,name,v)
    v,_,_=json_const(s,'const ACT'); v.update(json.load(open(f'{HERE}/act16.json'))); s=set_json_const(s,'const ACT',v)
    print('photos',phf,'narr',narr,'strip',strip,'cover',cover); return s

if __name__=='__main__':
    s=rd()
    for step in sys.argv[1:]: s=globals()[step](s)
    wr(s)
