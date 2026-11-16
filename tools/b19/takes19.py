"""Book 19 recording takes (Marta narration + women's lines, Pedro for Tiago's line, word sounds, title).
Splits each page at its dashes as tools/rerecord/segments.py does. Writes WORK/segs.json and WORK/takes.json."""
import json,os,re,sys
HERE=os.path.dirname(os.path.abspath(__file__)); WORK=os.environ.get('WORK','/home/claude/work/b19')
sys.path.insert(0,os.path.join(HERE,'..','rerecord')); from segments import clean
VOICE={'M':'bBNhdwrIjl4fcVYiRbT2','P':'XxTHUwWTW2conYBz0vvk'}
MEN={7:['Gosto muito da tua mãe. Mas da próxima vez, poderíamos jantar só os dois?']}
RX=re.compile(r'\[([^|\]]+)\|([^\]]+)\]')
def end(t): return t if re.search(r'[.!?…:]$',t) else t+'.'
P=json.load(open(f'{HERE}/pages19.json',encoding='utf8')); S=[]
for i,p in enumerate(P):
    k=0
    for piece in RX.sub(r'\1',p).split('—'):
        x=clean(piece)
        if not re.search(r'\w',x): continue
        S.append([19,i+1,k,'P' if x in MEN.get(i+1,[]) else 'M',x]); k+=1
assert sum(s[3]=='P' for s in S)==1
forms=sorted({sh.lower() for p in P for sh,_ in RX.findall(p)})
s=open(os.path.join(HERE,'..','..','docs','index.html'),encoding='utf8').read(); i=s.index('const WCLIP=')+12
W=json.JSONDecoder().raw_decode(s,i)[0]; new=[f for f in forms if f not in W]
T={}
def take(name,v,items,sep='\n\n'): T[name]={'voice':VOICE[v],'items':items,'prompt':sep.join(end(x[2]) for x in items) if sep=='\n\n' else ', '.join(x[2] for x in items)+'.'}
take('m01','M',[['seg',f'19.{b}.{k}',t] for _,b,k,v,t in S if v=='M'])
take('p01','P',[['seg',f'19.{b}.{k}',t] for _,b,k,v,t in S if v=='P'])
take('w01','M',[['word',w,w] for w in new],sep=', ')
take('t01','M',[['title','jantar3','Um Jantar a Três']])
json.dump(S,open(f'{WORK}/segs.json','w'),ensure_ascii=False,indent=0); json.dump(T,open(f'{WORK}/takes.json','w'),ensure_ascii=False,indent=1)
for k,v in T.items(): print(k,len(v['items']),len(v['prompt'])); print(v['prompt'][:2000]); print()
