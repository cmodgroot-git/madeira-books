"""Split books 1–17 into spoken segments: every page is cut at its dashes, each piece read by Marta,
or by Pedro when it is a man's line (speakers.MEN). Writes WORK/segs.json: [book, page, k, voice, text]."""
import json,re,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from speakers import MEN
WORK=os.environ.get('WORK','/home/claude/work/rr')
RX=re.compile(r'\[([^|\]]+)\|([^\]]+)\]')
def clean(t):
    t=re.sub(r'[«»“”"]',' ',t); t=re.sub(r'\s+',' ',t).strip(); t=re.sub(r'\s+([,.!?…:;])',r'\1',t)
    return t.replace('RITA, ÉS UMA HEROÍNA!','Rita, és uma heroína!')
def segments(pages):
    segs=[]
    for b in range(1,18):
        for i,p in enumerate(pages[str(b)]):
            key=f'{b}.{i+1}'; men=[clean(m) for m in MEN.get(key,[])]; used=set(); k=0
            for piece in RX.sub(r'\1',p).split('—'):
                parts=[('M',clean(piece))]
                for m in men:   # a man's line inside a longer piece (no closing dash): split it off
                    nw=[]
                    for v,x in parts:
                        if v=='M' and m in x: a,c=x.split(m,1); nw+=[('M',a.strip()),('P',m),('M',c.strip())]; used.add(m)
                        else: nw.append((v,x))
                    parts=nw
                for v,x in parts:
                    if re.search(r'\w',x): segs.append([b,i+1,k,v,x]); k+=1
            assert used==set(men),(key,set(men)-used)
    return segs
if __name__=='__main__':
    d=json.load(open(f'{WORK}/pages.json')); S=segments(d['pages'])
    json.dump(S,open(f'{WORK}/segs.json','w'),ensure_ascii=False,indent=0)
    M=[s for s in S if s[3]=='M']; P=[s for s in S if s[3]=='P']
    print('segments',len(S),'Marta',len(M),sum(len(s[4]) for s in M),'chars; Pedro',len(P),sum(len(s[4]) for s in P),'chars')
