#!/usr/bin/env python3
"""Assemble the re-recorded audio for books 1–17 and write it into docs/ (Marta + Pedro).
  assemble.py pages   -> WORK/out/<sid><p>.mp3 + WORK/narr_all.json (NARR, aligned)
  assemble.py clips   -> docs/audio/words.mp3, docs/audio/titles.mp3 + WORK/clips_all.json (WCLIP, TCLIP, TWORDS)
  assemble.py write   -> per-book narration packs, PACK, NARR, WCLIP, TCLIP, TWORDS in docs/index.html
Book 18 (ribeira) keeps its narration; its 26 word clips and title are carried over from the current files."""
import json,os,re,sys,subprocess,hashlib,shutil,numpy as np,soundfile as sf
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE); import align
ROOT=os.path.abspath(os.path.join(HERE,'..','..')); DOC=os.path.join(ROOT,'docs'); HTML=os.path.join(DOC,'index.html')
WORK=os.environ.get('WORK','/home/claude/work/rr'); SR=44100
D=json.load(open(f'{WORK}/pages.json')); IDS=[i for i,_ in D['ids']]
RX=re.compile(r'\[([^|\]]+)\|([^\]]+)\]'); WRX=re.compile(r"[^\W_]+(?:[-'’][^\W_]+)*")
def groups(p):
    out=[];last=0
    for m in RX.finditer(p): out+=WRX.findall(p[last:m.start()]); out.append(m.group(1)); last=m.end()
    out+=WRX.findall(p[last:]); return out
def rd(): return open(HTML,encoding='utf8').read()
def jc(s,name):
    i=s.index(name+'=')+len(name)+1; v,e=json.JSONDecoder().raw_decode(s,i); return v,i,e
def enc(wav,mp3): subprocess.run(['ffmpeg','-v','error','-y','-i',wav,'-ac','1','-ar','24000','-b:a','48k',mp3],check=True)
def dur(f): return float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f],capture_output=True,text=True).stdout)
def pages():
    S=json.load(open(f'{WORK}/segs.json')); os.makedirs(f'{WORK}/out',exist_ok=True); NARR={}
    by={}
    for b,p,k,v,t in S: by.setdefault((b,p),[]).append(k)
    for (b,p),ks in sorted(by.items()):
        parts=[]
        for j,k in enumerate(sorted(ks)):
            a,sr=sf.read(f'{WORK}/seg/seg_{b}.{p}.{k}.wav'); assert sr==SR
            if j: parts.append(np.zeros(int(.3*SR)))
            parts.append(a)
        a=np.concatenate([np.zeros(int(.05*SR))]+parts+[np.zeros(int(.15*SR))]); sid=IDS[b-1]
        w44=f'{WORK}/out/{sid}{p-1}.wav'; sf.write(w44,a,SR); enc(w44,f'{WORK}/out/{sid}{p-1}.mp3')
        w16=f'{WORK}/out/{sid}{p-1}.16k.wav'; subprocess.run(['ffmpeg','-v','error','-y','-i',w44,'-ar','16000',w16],check=True)
        g=groups(D['pages'][str(b)][p-1]); t=align.align(w16,g); NARR[f'{sid}:{p-1}']=t
        gaps=[(g[x],t[x][0]-t[x-1][1]) for x in range(1,len(t)) if t[x][0]-t[x-1][1]>1600]
        print(sid,p,len(g),'start',t[0][0],'tail',round(len(a)/SR*1000-t[-1][1]),'gaps',gaps,flush=True)
    json.dump(NARR,open(f'{WORK}/narr_all.json','w'))
def clips():
    s=rd(); W,_,_=jc(s,'const WCLIP'); T,_,_=jc(s,'const TCLIP'); E,_,_=jc(s,'const ECHO')
    TT=json.load(open(f'{WORK}/takes.json'))['t01']['items']   # [title, sid, text]
    # current files, decoded, to carry book 18 over
    def load(mp3):
        w=f'{WORK}/_cur.wav'; subprocess.run(['ffmpeg','-v','error','-y','-i',mp3,'-ac','1','-ar',str(SR),w],check=True); return sf.read(w)[0]
    curW=load(os.path.join(DOC,'audio','words.mp3')); curT=load(os.path.join(DOC,'audio','titles.mp3'))
    keep=set(json.load(open(os.path.join(ROOT,'tools','b18','data','clips18.json')))['WCLIP'])
    echo={e['o'].lower():e['o'] for v in E.values() for e in v}
    sil=np.zeros(int(.35*SR)); buf=[];t=0.0;NW={}
    for k in W:
        if k in keep: a=curW[int(W[k][0]*SR):int(W[k][1]*SR)]
        elif k in echo: a=sf.read(f'{WORK}/seg/echo_'+re.sub(r'[^\w.-]','_',k)[:80]+'.wav')[0]
        else: a=sf.read(f'{WORK}/seg/word_'+re.sub(r'[^\w.-]','_',k)[:80]+'.wav')[0]
        if buf: buf.append(sil); t+=len(sil)/SR
        NW[k]=[round(t,3),round(t+len(a)/SR,3)]; buf.append(a); t+=len(a)/SR
    sf.write(f'{WORK}/words.wav',np.concatenate(buf),SR); enc(f'{WORK}/words.wav',os.path.join(DOC,'audio','words.mp3'))
    sil=np.zeros(int(.4*SR)); buf=[];t=0.0;NT={};TW={}
    titles=[(sid,txt) for _,sid,txt in TT]+[('ribeira',None)]
    for sid,txt in titles:
        if txt is None: a=curT[int(T[sid][0]*SR):int(T[sid][1]*SR)]; txt='Antes que Mudes de Ideias'
        else: a=sf.read(f'{WORK}/seg/title_{sid}.wav')[0]
        if buf: buf.append(sil); t+=len(sil)/SR
        w16=f'{WORK}/_t.wav'; sf.write(f'{WORK}/_t44.wav',a,SR); subprocess.run(['ffmpeg','-v','error','-y','-i',f'{WORK}/_t44.wav','-ar','16000',w16],check=True)
        tw=align.align(w16,txt.split())
        NT[sid]=[round(t,3),round(t+len(a)/SR,3)]; TW[sid]=[[int(t*1000+max(0,x)),int(t*1000+y)] for x,y in tw]
        buf.append(a); t+=len(a)/SR
    sf.write(f'{WORK}/titles.wav',np.concatenate(buf),SR); enc(f'{WORK}/titles.wav',os.path.join(DOC,'audio','titles.mp3'))
    # the mp3 encoder delay shifts everything a little: measure and report the file lengths
    print('words',len(NW),round(dur(os.path.join(DOC,'audio','words.mp3')),2),'s vs',round(NW[list(NW)[-1]][1],2),'| titles',len(NT),round(dur(os.path.join(DOC,'audio','titles.mp3')),2),'s')
    json.dump({'WCLIP':NW,'TCLIP':NT,'TWORDS':TW},open(f'{WORK}/clips_all.json','w'),ensure_ascii=False)
def write():
    s=rd(); N=json.load(open(f'{WORK}/narr_all.json')); C=json.load(open(f'{WORK}/clips_all.json'))
    P,i,e=jc(s,'const PACK'); retired=[]
    os.makedirs(f'{WORK}/packs',exist_ok=True); sil=f'{WORK}/packs/_sil3.mp3'
    subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','anullsrc=r=24000:cl=mono','-t','0.3','-b:a','48k',sil],check=True)
    for b,sid in enumerate(IDS[:17],1):
        n=len(D['pages'][str(b)]); L=[];off=[];end=[];t=0.0
        for p in range(n):
            f=f'{WORK}/out/{sid}{p}.mp3'
            if p: L.append(f"file '{sil}'"); t+=dur(sil)
            L.append(f"file '{f}'"); off.append(round(t,2)); t+=dur(f); end.append(round(t,2))
        open(f'{WORK}/packs/{sid}.txt','w').write('\n'.join(L)); tmp=f'{WORK}/packs/{sid}.mp3'
        subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',f'{WORK}/packs/{sid}.txt','-c','copy',tmp],check=True)
        h=hashlib.sha1(open(tmp,'rb').read()).hexdigest()[:10]; src=f'audio/book/{sid}.{h}.mp3'
        old=P['narr'][sid]['src']
        if old!=src:
            retired.append(old)
            if os.path.exists(os.path.join(DOC,old)): os.remove(os.path.join(DOC,old))
        shutil.copy(tmp,os.path.join(DOC,src)); P['narr'][sid]={'src':src,'off':off,'end':end}
    s=s[:i]+json.dumps(P,ensure_ascii=False,separators=(',',':'))+s[e:]
    for name,new in [('const NARR',N),('const WCLIP',C['WCLIP']),('const TCLIP',C['TCLIP']),('const TWORDS',C['TWORDS'])]:
        v,i,e=jc(s,name)
        if name=='const NARR': v.update(new)
        else: v=new
        s=s[:i]+json.dumps(v,ensure_ascii=False)+s[e:]
    open(HTML,'w',encoding='utf8').write(s); json.dump(retired,open(f'{WORK}/retired.json','w')); print('retired',len(retired))
if __name__=='__main__':
    for step in sys.argv[1:]: globals()[step]()
