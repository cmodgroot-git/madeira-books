"""Group segments into recording takes (≤ LIM chars each; one paragraph per segment) and word batches.
Writes WORK/takes.json: {name: {voice, items:[[kind,id,text]], prompt}}."""
import json,os,re
WORK=os.environ.get('WORK','/home/claude/work/rr'); LIM=1700
VOICE={'M':'bBNhdwrIjl4fcVYiRbT2','P':'XxTHUwWTW2conYBz0vvk'}
def end(t): return t if re.search(r'[.!?…:]$',t) else t+'.'
S=json.load(open(f'{WORK}/segs.json')); WL=json.load(open(f'{WORK}/wordlist.json'))
D=json.load(open(f'{WORK}/pages.json')); titles=[(i,t) for i,t in D['ids'][:17]]
T={}; cur=[]; n=0
def flush(v,items,name):
    T[name]={'voice':VOICE[v],'items':items,'prompt':'\n\n'.join(end(x[2]) for x in items)}
for s in [s for s in S if s[3]=='M']:
    item=['seg',f'{s[0]}.{s[1]}.{s[2]}',s[4]]
    if cur and sum(len(x[2])+2 for x in cur)+len(s[4])>LIM: n+=1; flush('M',cur,f'm{n:02d}'); cur=[]
    cur.append(item)
n+=1; flush('M',cur,f'm{n:02d}')
flush('P',[['seg',f'{s[0]}.{s[1]}.{s[2]}',s[4]] for s in S if s[3]=='P']+[['echo',e.lower(),e] for e in WL['echo']],'p01')
flush('M',[['title',i,t] for i,t in titles],'t01')
words=WL['words']; B=15
for k in range(0,len(words),B):
    batch=words[k:k+B]; name=f'w{k//B+1:02d}'
    T[name]={'voice':VOICE['M'],'items':[['word',w,w] for w in batch],'prompt':', '.join(batch)+'.'}
json.dump(T,open(f'{WORK}/takes.json','w'),ensure_ascii=False,indent=0)
print(len(T),'takes:',{k:len(v['prompt']) for k,v in T.items() if not k.startswith('w')}, 'word batches',sum(k.startswith('w') for k in T))
