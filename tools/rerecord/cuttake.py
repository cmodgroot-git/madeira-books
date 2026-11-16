"""Download a take, align its items, cut each item to WORK/seg/<id>.wav (44.1 kHz) and check it.
  cuttake.py <take> <url>   -> prints per-item similarity of the transcript to the text; low ones flagged."""
import json,os,re,sys,subprocess,difflib,unicodedata,numpy as np,soundfile as sf
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import align
WORK=os.environ.get('WORK','/home/claude/work/rr'); T=json.load(open(f'{WORK}/takes.json'))
def norm(t): t=unicodedata.normalize('NFD',t.lower()); return re.sub(r'[^a-z]','',''.join(c for c in t if not unicodedata.combining(c)))
def sim(a,b): return difflib.SequenceMatcher(None,norm(a),norm(b)).ratio()
def run(name,url):
    os.makedirs(f'{WORK}/raw',exist_ok=True); os.makedirs(f'{WORK}/seg',exist_ok=True); os.makedirs(f'{WORK}/chk',exist_ok=True)
    mp3=f'{WORK}/raw/{name}.mp3'
    if not os.path.exists(mp3): subprocess.run(['curl','-sS','-o',mp3,url],check=True)
    w16=f'{WORK}/raw/{name}.16k.wav'; w44=f'{WORK}/raw/{name}.44k.wav'
    subprocess.run(['ffmpeg','-v','error','-y','-i',mp3,'-ac','1','-ar','16000',w16],check=True)
    subprocess.run(['ffmpeg','-v','error','-y','-i',mp3,'-ac','1','-ar','44100',w44],check=True)
    items=T[name]['items']; spans=align.align(w16,[x[2] for x in items])
    a,sr=sf.read(w44); n=len(a); res=[]
    word=items[0][0]=='word'; pre,post=(60,110) if word else (80,160)
    for k,(it,(s,e)) in enumerate(zip(items,spans)):
        lo=spans[k-1][1] if k else 0; hi=spans[k+1][0] if k+1<len(spans) else n/sr*1000
        s2=max(s-pre,(lo+s)/2); e2=min(e+post,(e+hi)/2)
        seg=a[int(s2/1000*sr):int(e2/1000*sr)].copy(); f=int(.012*sr); seg[:f]*=np.linspace(0,1,f); seg[-f:]*=np.linspace(1,0,f)
        safe=re.sub(r'[^\w.-]','_',str(it[1]))[:80]; out=f'{WORK}/seg/{it[0]}_{safe}.wav'; sf.write(out,seg,sr)
        c16=f'{WORK}/chk/{it[0]}_{safe}.wav'; subprocess.run(['ffmpeg','-v','error','-y','-i',out,'-ar','16000',c16],check=True)
        heard=align.decode(c16); r=sim(heard,it[2]); res.append([it[0],it[1],round(r,2),heard,round((e2-s2)/1000,2)])
    json.dump(res,open(f'{WORK}/chk/{name}.json','w'),ensure_ascii=False)
    low=[x for x in res if x[2]<(0.6 if word else 0.75)]
    print(name,len(res),'items, mean sim',round(sum(x[2] for x in res)/len(res),2),'| low:',len(low))
    for x in low: print('   LOW',x)
if __name__=='__main__': run(sys.argv[1],sys.argv[2])
