#!/usr/bin/env python3
"""Retellings of old books on the old book's pictures, reusing its published tap regions (no SAM, no new art).
  old.py <cfg> takes          # WORK/segs.json + WORK/takes.json (record each take, cut with tools/rerecord/cuttake.py)
  old.py <cfg> audio          # pages + NARR + title clip appended to the committed titles.mp3
  old.py <cfg> build          # pages, STORIES (again:N), photos copied from the old book (ids renamed), PACK, NARR, TCLIP/TWORDS
<cfg> is tools/b<N>b/retell.json: {sid, old, n, title, title_words, cover, pages, men:{page:[lines]}, narrator:"M"|"P"}.
Tags in the retelling must use keys that the old book already has on the same page (checked)."""
import json,os,re,sys,glob,hashlib,shutil,subprocess,numpy as np,soundfile as sf
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.abspath(os.path.join(HERE,'..','..')); DOC=f'{ROOT}/docs'; HTML=f'{DOC}/index.html'
sys.path.insert(0,HERE); sys.path.insert(0,os.path.join(HERE,'..','rerecord'))
CFGP=os.path.abspath(sys.argv[1]); C=json.load(open(CFGP)); CD=os.path.dirname(CFGP)
SID,OLD,N=C['sid'],C['old'],str(C['n']); WORK=os.environ.get('WORK',f'/home/claude/work/b{N}b'); A=f'{WORK}/audio'
for d in ('audio/out','audio/wav','audio/clips','build','seg'): os.makedirs(f'{WORK}/{d}',exist_ok=True)
P=json.load(open(os.path.join(CD,C['pages']),encoding='utf8')); NP=len(P)
VOICE={'M':'bBNhdwrIjl4fcVYiRbT2','P':'XxTHUwWTW2conYBz0vvk'}; NARRATOR=C.get('narrator','M'); OTHER={'M':'P','P':'M'}[NARRATOR]
RX=re.compile(r'\[([^|\]]+)\|([^\]]+)\]')
def end(t): return t if re.search(r'[.!?…:»]$',t) else t+'.'
def segs():
    from segments import clean
    S=[]; OTH={int(k):v for k,v in C.get('other',{}).items()}   # lines read by the other voice
    for i,p in enumerate(P):
        k=0
        for piece in RX.sub(r'\1',p).split('—'):
            x=clean(piece)
            if not re.search(r'\w',x): continue
            S.append([N+'b',i+1,k,OTHER if x in OTH.get(i+1,[]) else NARRATOR,x]); k+=1
    assert sum(len(v) for v in OTH.values())==sum(s[3]==OTHER for s in S),[s for s in S]
    return S
def takes():
    S=segs(); T={}
    def take(name,v,items): T[name]={'voice':VOICE[v],'items':items,'prompt':'\n\n'.join(end(x[2]) for x in items)}
    main=[['seg',f'{N}b.{b}.{k}',t] for _,b,k,v,t in S if v==NARRATOR]; half=(NP+1)//2
    take('n01',NARRATOR,[x for x in main if int(x[1].split('.')[1])<=half]); take('n02',NARRATOR,[x for x in main if int(x[1].split('.')[1])>half])
    oth=[['seg',f'{N}b.{b}.{k}',t] for _,b,k,v,t in S if v==OTHER]
    if oth: take('o01',OTHER,oth)
    take('t01','M',[['title',SID,C['title']]])
    json.dump(S,open(f'{WORK}/segs.json','w'),ensure_ascii=False,indent=0); json.dump(T,open(f'{WORK}/takes.json','w'),ensure_ascii=False,indent=1)
    for k,v in T.items(): print(k,v['voice'][:4],len(v['items']),len(v['prompt']))
def enc(wav,mp3): subprocess.run(['ffmpeg','-v','error','-y','-i',wav,'-ac','1','-ar','24000','-b:a','48k',mp3],check=True)
def dur(f): return float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f],capture_output=True,text=True).stdout)
def audio():
    import align; from narr import groups
    S=json.load(open(f'{WORK}/segs.json')); NARR={}; SR=44100
    for n in range(1,NP+1):
        parts=[]
        for j,k in enumerate(sorted(s[2] for s in S if s[1]==n)):
            a,sr=sf.read(f'{WORK}/seg/seg_{N}b.{n}.{k}.wav'); assert sr==SR
            if j: parts.append(np.zeros(int(.3*SR)))
            parts.append(a)
        a=np.concatenate([np.zeros(int(.05*SR))]+parts+[np.zeros(int(.15*SR))])
        w44=f'{A}/out/p{n}.wav'; sf.write(w44,a,SR); enc(w44,f'{A}/out/p{n}.mp3')
        w16=f'{A}/wav/p{n}.wav'; subprocess.run(['ffmpeg','-v','error','-y','-i',w44,'-ar','16000',w16],check=True)
        g=groups(P[n-1]); t=align.align(w16,g); NARR[f'{SID}:{n-1}']=t
        gaps=[(g[x],t[x][0]-t[x-1][1]) for x in range(1,len(t)) if t[x][0]-t[x-1][1]>1600]
        print(n,len(g),'start',t[0][0],'tail',round(len(a)/SR*1000-t[-1][1]),'gaps',gaps,flush=True)
    Cd=f'{A}/clips'; sil=f'{Cd}/_sil.mp3'; subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','anullsrc=r=24000:cl=mono','-t','0.35','-b:a','48k',sil],check=True)
    title=f'{Cd}/title.mp3'; enc(f'{WORK}/seg/title_{SID}.wav',title)
    base=f'{Cd}/_orig_titles.mp3'; open(base,'wb').write(subprocess.run(['git','-C',ROOT,'show','HEAD:docs/audio/titles.mp3'],capture_output=True,check=True).stdout)
    t0=dur(base)+dur(sil); lst=f'{Cd}/_t.txt'; open(lst,'w').write(f"file '{base}'\nfile '{sil}'\nfile '{title}'")
    subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',lst,'-c','copy',f'{Cd}/titles.mp3'],check=True)
    TC={SID:[round(t0,3),round(t0+dur(title),3)]}
    w16=f'{A}/wav/title.wav'; subprocess.run(['ffmpeg','-v','error','-y','-i',title,'-ar','16000','-ac','1',w16],check=True)
    tw=align.align(w16,C['title_words']); s0=t0*1000
    json.dump({'NARR':NARR,'TCLIP':TC,'TWORDS':{SID:[[int(s0+max(0,x)),int(s0+y)] for x,y in tw]}},open(f'{A}/data.json','w'),ensure_ascii=False); print(TC)
def once(s,old,new,mark):
    if mark in s: return s
    assert s.count(old)==1,(old[:60],s.count(old)); return s.replace(old,new)
def jc(s,name):
    i=s.index(name+'=')+len(name)+1; v,e=json.JSONDecoder().raw_decode(s,i); return v,i,e
def setj(s,name,v,**kw):
    _,i,e=jc(s,name); return s[:i]+json.dumps(v,ensure_ascii=False,**kw)+s[e:]
def h10(p): return hashlib.sha1(open(p,'rb').read()).hexdigest()[:10]
def hashed(tmp,dirn,ext):
    dst=os.path.join(DOC,dirn,f'{SID}.{h10(tmp)}.{ext}')
    for f in os.listdir(os.path.join(DOC,dirn)):
        if f.startswith(SID+'.') and f!=os.path.basename(dst): os.remove(os.path.join(DOC,dirn,f))
    shutil.copy(tmp,dst); return f'{dirn}/{SID}.{h10(tmp)}.{ext}'
def build():
    s=open(HTML,encoding='utf8').read()
    PH,_,_=jc(s,'PHF'); src=open(f'{DOC}/{PH[OLD]}',encoding='utf8').read()
    # every tag must already have a region on that page of the old book
    parts=re.split(r"'%s:(\d+)'"%OLD,src); have={int(parts[i]):{k for r in re.findall(r"o\('([^']+)'",parts[i+1]) for k in r.split()} for i in range(1,len(parts),2)}
    miss=[(i+1,k) for i,p in enumerate(P) for _,k in RX.findall(p) if k not in have.get(i,set())]; assert not miss,miss
    js=re.sub(r"'%s:(\d+)'"%OLD,lambda m:f"'{SID}:{m.group(1)}'",src); js=re.sub(OLD+r'(\d)',SID+r'\1',js)
    tmp=f'{WORK}/build/photos.js'; open(tmp,'w',encoding='utf8').write(js); phf=hashed(tmp,'photos','js')
    # text + STORIES
    pn=f'pages{N}b'; i=s.index(f'const pages{N}=['); j=s.index('\n];',i)+3
    s=once(s,s[i:j],s[i:j]+f'\n\nconst {pn}=[\n'+',\n'.join(json.dumps(p,ensure_ascii=False) for p in P)+'\n];',f'const {pn}=[')
    i=s.index(f'const {pn}=['); j=s.index('\n];',i)+3; s=s[:i]+f'const {pn}=[\n'+',\n'.join(json.dumps(p,ensure_ascii=False) for p in P)+'\n];'+s[j:]   # rerun: new text
    i=[m.end() for m in re.finditer(r"\{id:'[^']+',title:'[^']*',again:",s)][-1]; i=s.index('\n',i)+1   # after the last retelling
    if f"id:'{SID}'" not in s: s=s[:i]+("  {id:'%s',title:'%s',again:%s,cams:[],scenes:%s.map(()=>()=>''),pages:%s,cover:%d},\n"%(SID,C['title'],N,pn,pn,C['cover']))+s[i:]
    # narration pack; strip and cover are the old book's
    T=f'{WORK}/build'; sil=f'{T}/_sil3.mp3'; subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','anullsrc=r=24000:cl=mono','-t','0.3','-b:a','48k',sil],check=True)
    L=[];off=[];en=[];t=0.0
    for n in range(1,NP+1):
        f=f'{A}/out/p{n}.mp3'
        if n>1: L.append(f"file '{sil}'"); t+=dur(sil)
        L.append(f"file '{f}'"); off.append(round(t,2)); t+=dur(f); en.append(round(t,2))
    open(f'{T}/narr.txt','w').write('\n'.join(L)); subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',f'{T}/narr.txt','-c','copy',f'{T}/narr.mp3'],check=True)
    narr=hashed(f'{T}/narr.mp3','audio/book','mp3')
    PH[SID]=phf; s=setj(s,'PHF',PH)
    PK,_,_=jc(s,'const PACK'); PK['narr'][SID]={'src':narr,'off':off,'end':en}; PK['thumbs'][SID]=PK['thumbs'][OLD]; s=setj(s,'const PACK',PK,separators=(',',':'))
    m=re.search(r"COVER_IMG=\{.*?\};",s); ci=re.search(r"%s:'([^']*)'"%OLD,m.group(0)).group(1)
    s=re.sub(r"(COVER_IMG=\{.*?)(,%s:'[^']*')?\};"%SID,lambda m:m.group(1)+f",{SID}:'{ci}'"+'};',s,count=1)
    D=json.load(open(f'{A}/data.json'))
    for name,new in [('const NARR',D['NARR']),('const TCLIP',D['TCLIP']),('const TWORDS',D['TWORDS'])]:
        v,_,_=jc(s,name); v.update(new); s=setj(s,name,v)
    shutil.copy(f'{A}/clips/titles.mp3',f'{DOC}/audio/titles.mp3')
    open(HTML,'w',encoding='utf8').write(s); print('photos',phf,'narr',narr)
globals()[sys.argv[2]]()
