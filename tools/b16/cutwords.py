#!/usr/bin/env python3
"""Cut book 16 word clips from batch recordings, trim the title and echo lines, and append them
to docs/audio/words.mp3 and docs/audio/titles.mp3. Prints new WCLIP / TCLIP entries (seconds)."""
import json,os,subprocess,sys,numpy as np,soundfile as sf
sys.path.insert(0,os.path.dirname(__file__)); import align
WORK=os.environ.get('WORK','/tmp/claude-0/-home-user-madeira-books/11c1ecef-e1df-5fad-8f8e-68eb719ae5fc/scratchpad/b16'); A=f'{WORK}/audio'
DOC=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','docs','audio'))
BATCH={'wb1':['pólo','campo de golfe','clube','saco de golfe','inês','taco','luva','joelhos','bola','bate','relva','patos'],
       'wb2':['fogem','baía','machico','ponta de são lourenço','hortênsias','tentilhão','buraco','rola','abraça-a','envergonhados','porta-bagagens']}
LINES={'querias uma coisa com os pés no chão?':'e_querias','a minha amiga inês vai ensinar-nos.':'e_ensinar','já joguei golfe muitas vezes!':'e_joguei','nunca trouxe ninguém aqui.':'e_trouxeb','eu trago o vinho.':'e_trago'}
def dur(f): return float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f],capture_output=True,text=True).stdout)
def enc(a,out):
    tmp=out+'.wav'; n=len(a); f=int(0.012*16000)
    a=a.copy(); a[:f]*=np.linspace(0,1,f); a[-f:]*=np.linspace(1,0,f); sf.write(tmp,a,16000)
    subprocess.run(['ffmpeg','-v','error','-y','-i',tmp,'-ac','1','-ar','24000','-b:a','48k',out],check=True); os.remove(tmp)
def speech_span(a,thr=0.02):
    e=np.array([np.abs(a[i:i+320]).max() for i in range(0,len(a)-320,160)]); on=np.nonzero(e>thr*e.max()*5 if e.max()<0.1 else e>thr)[0]
    return on[0]*160,on[-1]*160+320
def first_saying(a):
    """keep only the first saying: cut at the first silence over 0.35 s after speech starts"""
    s,e=speech_span(a); env=np.array([np.abs(a[i:i+320]).max() for i in range(s,e,160)])
    quiet=env<0.02*max(env.max(),1e-6)*3; run=0
    for k,q in enumerate(quiet):
        run=run+1 if q else 0
        if run*160>0.35*16000: return s,s+(k-run+1)*160+2400
    return s,e
def internal_gap(a):
    env=np.array([np.abs(a[i:i+320]).max() for i in range(0,max(1,len(a)-320),160)]); q=env<0.03*env.max(); run=best=0
    s=np.argmax(~q); e=len(q)-np.argmax(~q[::-1])
    for x in q[s:e]: run=run+1 if x else 0; best=max(best,run)
    return best*160/16000
if __name__=='__main__':
    os.makedirs(f'{A}/clips',exist_ok=True); clips=[]
    for b,forms in BATCH.items():
        a,_=sf.read(f'{A}/wav/{b}.wav'); spans=align.align(f'{A}/wav/{b}.wav',forms)
        for f,(s,e) in zip(forms,spans):
            s=max(0,int((s-(160 if f.startswith('ponta') else 60))*16)); e=min(len(a),int((e+110)*16)); seg=a[s:e]
            out=f'{A}/clips/{f}.mp3'; enc(seg,out); clips.append((f,out)); print(f,round((e-s)/16000,2),'gap',round(internal_gap(seg),2),flush=True)
    for line,b in LINES.items():
        a,_=sf.read(f'{A}/wav/{b}.wav'); s,e=first_saying(a); s=max(0,s-800); e=min(len(a),e+800)
        if b=='e_trouxeb': s,e=0,int(1.95*16000)
        out=f'{A}/clips/{b}.mp3'; enc(a[s:e],out); clips.append((line,out)); print(line,round((e-s)/16000,2),flush=True)
    a,_=sf.read(f'{A}/wav/title.wav'); s,e=first_saying(a); s=max(0,s-800); e=min(len(a),e+800); enc(a[s:e],f'{A}/clips/title.mp3')
    print('title',round((e-s)/16000,2))
    sil=f'{A}/clips/_sil.mp3'; subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','anullsrc=r=24000:cl=mono','-t','0.35','-b:a','48k',sil],check=True)
    def append(base,items,outname):
        lst=f'{A}/clips/_{outname}.txt'; t=dur(base); ent={}; L=[f"file '{base}'"]
        for k,f in items: t+=dur(sil); L+= [f"file '{sil}'",f"file '{f}'"]; d=dur(f); ent[k]=[round(t,3),round(t+d,3)]; t+=d
        open(lst,'w').write('\n'.join(L)); tmp=f'{A}/clips/{outname}'
        subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',lst,'-c','copy',tmp],check=True)
        return ent,tmp
    def orig(name):   # always start from the committed file, so a rerun never appends twice
        p=f'{A}/clips/_orig_{name}'; open(p,'wb').write(subprocess.run(['git','-C',DOC,'show',f'a294271:docs/audio/{name}'],capture_output=True,check=True).stdout); return p
    W,wf=append(orig('words.mp3'),clips,'words.mp3'); T,tf=append(orig('titles.mp3'),[('golfe',f'{A}/clips/title.mp3')],'titles.mp3')
    json.dump({'WCLIP':W,'TCLIP':T},open(f'{A}/clips16.json','w'),ensure_ascii=False); print(json.dumps(T))
