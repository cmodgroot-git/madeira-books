"""Align a word-list recording and cut each word into its own clip. usage: cutwords.py <batch idx>"""
import sys, json, re, subprocess, os, numpy as np
sys.path.insert(0,os.path.dirname(__file__)); import align
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'
D=S+'artifact-files/87e1712e-5e90-4175-b828-2581544915d4/'
WRX=re.compile(r"[^\W_]+(?:[-'’][^\W_]+)*")
B=json.load(open(S+'audio/wordbatches.json'))
os.makedirs(D+'audio/w',exist_ok=True)
idx=json.load(open(S+'audio/wordindex.json')) if os.path.exists(S+'audio/wordindex.json') else {}
def slug(f):
    import unicodedata
    s=unicodedata.normalize('NFD',f.lower()); s=''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+','-',s).strip('-')
for bi in map(int,sys.argv[1:]):
    src=S+f'audio/words/batch{bi}.mp3'; forms=B[bi]
    toks=[];own=[]
    for fi,f in enumerate(forms):
        for w in WRX.findall(f): toks.append(w); own.append(fi)
    tw=align.align(src,toks); a=align.wav(src); dur=len(a)/16000
    st=[None]*len(forms); en=[None]*len(forms)
    for (s,e),o in zip(tw,own):
        st[o]=s if st[o] is None else st[o]; en[o]=e
    out=[]
    for fi,f in enumerate(forms):
        lo=(en[fi-1]+st[fi])/2 if fi else max(0,st[fi]-.25)
        hi=(en[fi]+st[fi+1])/2 if fi+1<len(forms) else min(dur,en[fi]+.35)
        lo=max(lo,st[fi]-.25); hi=min(hi,en[fi]+.35)
        name=slug(f); dst=D+f'audio/w/{name}.mp3'
        subprocess.run(['ffmpeg','-v','error','-y','-ss',f'{lo:.3f}','-to',f'{hi:.3f}','-i',src,'-af','afade=t=in:d=0.02,areverse,afade=t=in:d=0.04,areverse','-ac','1','-ar','24000','-b:a','48k',dst],check=True)
        idx[f.lower()]=name; out.append((f,round(st[fi],2),round(en[fi]-st[fi],2),round(hi-lo,2)))
    gaps=[round(st[i+1]-en[i],2) for i in range(len(forms)-1)]
    print('batch',bi,'dur',round(dur,1),'first',round(st[0],2),'min gap',min(gaps),'short',[o for o in out if o[2]<.18])
json.dump(idx,open(S+'audio/wordindex.json','w'),ensure_ascii=False,indent=0)
