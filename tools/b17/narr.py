#!/usr/bin/env python3
"""Book 16 narration: groups per page (one per [data-s] element), mono 48 kbit/s mp3, NARR timings."""
import json,re,subprocess,sys,os
sys.path.insert(0,os.path.dirname(__file__))
import align
WORK=os.environ.get('WORK','/tmp/claude-0/-home-user-madeira-books/11c1ecef-e1df-5fad-8f8e-68eb719ae5fc/scratchpad/b17')
RX=re.compile(r'\[([^|\]]+)\|([^\]]+)\]'); WRX=re.compile(r"[^\W_]+(?:[-'’][^\W_]+)*")
def groups(p):
    out=[];last=0
    for m in RX.finditer(p):
        out+=WRX.findall(p[last:m.start()]); out.append(m.group(1)); last=m.end()
    out+=WRX.findall(p[last:]); return out
if __name__=='__main__':
    P=json.load(open(f'{WORK}/pages17.json',encoding='utf8')); A=f'{WORK}/audio'; NARR={}
    for i,p in enumerate(P):
        g=groups(p); n=i+1
        subprocess.run(['ffmpeg','-v','error','-y','-i',f'{A}/raw/b17p{n}.mp3','-ac','1','-ar','24000','-b:a','48k',f'{A}/out/b17p{n}.mp3'],check=True)
        t=align.align(f'{A}/wav/b17p{n}.wav',g); NARR[f'presente:{i}']=t
        dur=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f'{A}/out/b17p{n}.mp3'],capture_output=True,text=True).stdout)
        gaps=[(g[k],t[k][0]-t[k-1][1]) for k in range(1,len(t)) if t[k][0]-t[k-1][1]>1600]
        print(n,len(g),'start',t[0][0],'tail',round(dur*1000-t[-1][1]),'gaps',gaps,flush=True)
    json.dump(NARR,open(f'{A}/narr17.json','w'))
