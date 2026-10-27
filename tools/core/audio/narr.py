"""Build narration for pages: audio/raw/b<B>p<P>.mp3 -> published audio/b<B>p<P>.mp3 (mono 64k) + word timings in NARR.
usage: narr.py texts            -> write audio/texts.json (spoken text per page)
       narr.py build B:P [B:P..] -> align and insert"""
import sys, re, json, subprocess, os
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'
D=S+'artifact-files/87e1712e-5e90-4175-b828-2581544915d4/'
RX=re.compile(r'\[([^|\]]+)\|([^\]]+)\]'); WRX=re.compile(r"[^\W_]+(?:[-'’][^\W_]+)*")
def pages():
    h=open(D+'index.html').read()
    ids=re.findall(r"\{id:'(\w+)',title:'[^']*',.*?pages:(\w+)",h)
    out={}
    for bi,(sid,var) in enumerate(ids):
        m=re.search(r'const '+var+r'=\[(.*?)\n\];',h,re.S)
        arr=json.loads('['+m.group(1)+']')
        for pi,p in enumerate(arr): out[(bi+1,pi+1,sid)]=p
    return out
def elements(p):
    els=[];last=0;plain=RX.sub(r'\1',p);pos=0
    for m in RX.finditer(p):
        t=p[last:m.start()]
        for w in WRX.finditer(t): els.append(w.group(0))
        els.append(m.group(1)); last=m.end()
    for w in WRX.finditer(p[last:]): els.append(w.group(0))
    return plain,els
def spoken(plain): return re.sub(r'[«»“”"]','',plain).replace('—','—')
if sys.argv[1]=='texts':
    T={f'b{b}p{q}':spoken(elements(p)[0]) for (b,q,sid),p in pages().items()}
    json.dump(T,open(S+'audio/texts.json','w'),ensure_ascii=False,indent=0); print(len(T))
elif sys.argv[1]=='build':
    sys.path.insert(0,S+'audio'); import align
    P=pages(); h=open(D+'index.html').read()
    i=h.find('const NARR=')+len('const NARR='); j=h.find(';\n',i); N=json.loads(h[i:j])
    os.makedirs(D+'audio',exist_ok=True)
    for bp in sys.argv[2:]:
        b,q=map(int,bp.split(':')); key=[k for k in P if k[0]==b and k[1]==q][0]; sid=key[2]
        plain,els=elements(P[key]); words=[];own=[]
        for ei,e in enumerate(els):
            for w in WRX.findall(e): words.append(w); own.append(ei)
        raw=S+f'audio/raw/b{b}p{q}.mp3'; out=D+f'audio/b{b}p{q}.mp3'
        subprocess.run(['ffmpeg','-v','error','-y','-i',raw,'-ac','1','-ar','24000','-b:a','48k',out],check=True)
        tw=align.align(out,words); span=[[None,None] for _ in els]
        for (s,e),o in zip(tw,own):
            if span[o][0] is None: span[o][0]=s
            span[o][1]=e
        N[f'{sid}:{q-1}']=[[int(s*1000),int(e*1000)] for s,e in span]
        dur=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',out],capture_output=True,text=True).stdout)
        gaps=[round(tw[k+1][0]-tw[k][1],2) for k in range(len(tw)-1)]
        flag=('LATE-START ' if tw[0][0]>1.2 else '')+('LONG-TAIL ' if dur-tw[-1][1]>1.5 else '')+('GAP%.1f '%max(gaps) if gaps and max(gaps)>1.6 else '')
        print(bp,len(els),'els',round(tw[0][0],2),'-',round(tw[-1][1],1),'of',round(dur,1),'s',os.path.getsize(out)//1024,'KB',flag,flush=True)
    h=open(D+'index.html').read(); i=h.find('const NARR=')+len('const NARR='); j=h.find(';\n',i)
    h=h[:i]+json.dumps(N,separators=(',',':'))+h[j:]; open(D+'index.html','w').write(h)
