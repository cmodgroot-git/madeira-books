#!/usr/bin/env python3
"""Book 19 audio: pages from the cut segments (WORK/seg, from tools/rerecord/cuttake.py with takes19.py),
NARR timings, and word clips + title appended to the committed words.mp3 / titles.mp3.
Writes WORK/audio/out/b19p<n>.mp3, WORK/audio/narr19.json, WORK/audio/clips19.json, WORK/audio/clips/{words,titles}.mp3."""
import json,os,re,sys,subprocess,numpy as np,soundfile as sf
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE); import align
from narr import groups
WORK=os.environ.get('WORK','/home/claude/work/b19'); A=f'{WORK}/audio'; SR=44100
ROOT=os.path.abspath(os.path.join(HERE,'..','..'))
def enc(wav,mp3): subprocess.run(['ffmpeg','-v','error','-y','-i',wav,'-ac','1','-ar','24000','-b:a','48k',mp3],check=True)
def dur(f): return float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f],capture_output=True,text=True).stdout)
def pages():
    P=json.load(open(f'{HERE}/pages19.json',encoding='utf8')); S=json.load(open(f'{WORK}/segs.json')); NARR={}
    for n in range(1,9):
        parts=[]
        for j,k in enumerate(sorted(s[2] for s in S if s[1]==n)):
            a,sr=sf.read(f'{WORK}/seg/seg_19.{n}.{k}.wav'); assert sr==SR
            if j: parts.append(np.zeros(int(.3*SR)))
            parts.append(a)
        a=np.concatenate([np.zeros(int(.05*SR))]+parts+[np.zeros(int(.15*SR))])
        w44=f'{A}/out/b19p{n}.wav'; sf.write(w44,a,SR); enc(w44,f'{A}/out/b19p{n}.mp3')
        w16=f'{A}/wav/b19p{n}.wav'; subprocess.run(['ffmpeg','-v','error','-y','-i',w44,'-ar','16000',w16],check=True)
        g=groups(P[n-1]); t=align.align(w16,g); NARR[f'jantar3:{n-1}']=t
        gaps=[(g[x],t[x][0]-t[x-1][1]) for x in range(1,len(t)) if t[x][0]-t[x-1][1]>1600]
        print(n,len(g),'start',t[0][0],'tail',round(len(a)/SR*1000-t[-1][1]),'gaps',gaps,flush=True)
    json.dump(NARR,open(f'{A}/narr19.json','w'))
def clips():
    T=json.load(open(f'{WORK}/takes.json')); C=f'{A}/clips'
    sil=f'{C}/_sil.mp3'; subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','anullsrc=r=24000:cl=mono','-t','0.35','-b:a','48k',sil],check=True)
    def mp3(name):
        out=f'{C}/{name}.mp3'; enc(f'{WORK}/seg/{name}.wav',out); return out
    words=[(w,mp3('word_'+re.sub(r'[^\w.-]','_',w))) for _,w,_ in T['w01']['items']]
    title=mp3('title_jantar3')
    def orig(name):   # start from the committed file, so a rerun never appends twice
        p=f'{C}/_orig_{name}'; open(p,'wb').write(subprocess.run(['git','-C',ROOT,'show',f'HEAD:docs/audio/{name}'],capture_output=True,check=True).stdout); return p
    def append(base,items,outname):
        t=dur(base); ent={}; L=[f"file '{base}'"]
        for k,f in items: t+=dur(sil); L+=[f"file '{sil}'",f"file '{f}'"]; d=dur(f); ent[k]=[round(t,3),round(t+d,3)]; t+=d
        lst=f'{C}/_{outname}.txt'; open(lst,'w').write('\n'.join(L))
        subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',lst,'-c','copy',f'{C}/{outname}'],check=True); return ent
    W=append(orig('words.mp3'),words,'words.mp3'); TC=append(orig('titles.mp3'),[('jantar3',title)],'titles.mp3')
    w16=f'{A}/wav/title.wav'; subprocess.run(['ffmpeg','-v','error','-y','-i',title,'-ar','16000','-ac','1',w16],check=True)
    tw=align.align(w16,['um','jantar','a','três']); s0=TC['jantar3'][0]*1000
    TW={'jantar3':[[int(s0+max(0,x)),int(s0+y)] for x,y in tw]}
    json.dump({'WCLIP':W,'TCLIP':TC,'TWORDS':TW},open(f'{A}/clips19.json','w'),ensure_ascii=False); print(W,TC,TW)
if __name__=='__main__':
    for step in sys.argv[1:]: globals()[step]()
