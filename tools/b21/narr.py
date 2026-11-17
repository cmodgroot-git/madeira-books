#!/usr/bin/env python3
"""Book 21 narration (Marta narrates, Pedro the men's lines; pages assembled from segments in WORK/audio/hq): groups per page (one per [data-s] element), mono 48 kbit/s mp3, NARR timings."""
import json,re,subprocess,sys,os
sys.path.insert(0,os.path.dirname(__file__))
import align
WORK=os.environ.get('WORK','/home/claude/work/b21')
RX=re.compile(r'\[([^|\]]+)\|([^\]]+)\]'); WRX=re.compile(r"[^\W_]+(?:[-'’][^\W_]+)*")
def groups(p):
    out=[];last=0
    for m in RX.finditer(p):
        out+=WRX.findall(p[last:m.start()]); out.append(m.group(1)); last=m.end()
    out+=WRX.findall(p[last:]); return out
if __name__=='__main__':
    P=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'pages21.json'),encoding='utf8')); A=f'{WORK}/audio'; NARR={}
    for i,p in enumerate(P):
        g=groups(p); n=i+1
        subprocess.run(['ffmpeg','-v','error','-y','-i',f'{A}/raw/b21p{n}.mp3','-ac','1','-ar','24000','-b:a','48k',f'{A}/out/b21p{n}.mp3'],check=True)
        t=align.align(f'{A}/wav/b21p{n}.wav',g); NARR[f'casa3:{i}']=t
        dur=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f'{A}/out/b21p{n}.mp3'],capture_output=True,text=True).stdout)
        gaps=[(g[k],t[k][0]-t[k-1][1]) for k in range(1,len(t)) if t[k][0]-t[k-1][1]>1600]
        print(n,len(g),'start',t[0][0],'tail',round(dur*1000-t[-1][1]),'gaps',gaps,flush=True)
    json.dump(NARR,open(f'{A}/narr21.json','w'))
