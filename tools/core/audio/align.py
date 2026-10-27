"""CTC forced alignment of known text to narration audio -> word start/end times (seconds)."""
import sys, json, re, subprocess, unicodedata, numpy as np, torch
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
M='jonatasgrosman/wav2vec2-large-xlsr-53-portuguese'
_p=_m=None
def load():
    global _p,_m
    if _p is None:
        _p=Wav2Vec2Processor.from_pretrained(M); _m=Wav2Vec2ForCTC.from_pretrained(M).eval()
    return _p,_m
def wav(path):
    raw=subprocess.run(['ffmpeg','-v','error','-i',path,'-ac','1','-ar','16000','-f','f32le','-'],capture_output=True,check=True).stdout
    return np.frombuffer(raw,np.float32)
def align(path, words):
    """words: list of word strings in order. returns list of (start,end) seconds"""
    p,m=load(); a=wav(path)
    with torch.no_grad():
        lp=torch.log_softmax(m(torch.tensor(p(a,sampling_rate=16000,return_tensors='pt').input_values[0])[None]).logits[0],-1).numpy()
    voc=p.tokenizer.get_vocab(); blank=voc.get('<pad>',0); sep=voc.get('|')
    def norm(w):
        w=w.lower().replace('’',"'")
        return [c for c in w if c in voc]
    toks=[];owner=[]
    for wi,w in enumerate(words):
        cs=norm(w) or [c for c in unicodedata.normalize('NFD',w.lower()) if c in voc]
        for c in cs: toks.append(voc[c]); owner.append(wi)
        if sep is not None and wi<len(words)-1: toks.append(sep); owner.append(-1)
    T,L=lp.shape[0],len(toks)
    # Viterbi over the CTC trellis (blank-interleaved)
    S=2*L+1; lab=[blank if s%2==0 else toks[s//2] for s in range(S)]
    NEG=-1e9; dp=np.full((T,S),NEG,np.float32); bp=np.zeros((T,S),np.int8)
    dp[0,0]=lp[0,lab[0]]; dp[0,1]=lp[0,lab[1]]
    for t in range(1,T):
        prev=dp[t-1]
        c0=prev; c1=np.concatenate([[NEG],prev[:-1]]); c2=np.concatenate([[NEG,NEG],prev[:-2]])
        allow=np.array([s%2==1 and s>=2 and lab[s]!=lab[s-2] for s in range(S)])
        c2=np.where(allow,c2,NEG)
        st=np.stack([c0,c1,c2]); k=st.argmax(0); dp[t]=st.max(0)+lp[t,lab]; bp[t]=k
    s=S-1 if dp[-1,S-1]>dp[-1,S-2] else S-2; path=[0]*T
    for t in range(T-1,-1,-1):
        path[t]=s; s-=int(bp[t,s])
    fr=a.shape[0]/16000/T
    st=[None]*len(words); en=[None]*len(words)
    for t,s in enumerate(path):
        if s%2==1:
            o=owner[s//2]
            if o>=0:
                if st[o] is None: st[o]=t*fr
                en[o]=(t+1)*fr
    for i in range(len(words)):
        if st[i] is None: st[i]=en[i-1] if i else 0; en[i]=st[i]+.05
    return [(round(x,3),round(y,3)) for x,y in zip(st,en)]
if __name__=='__main__':
    txt=sys.argv[2]; ws=re.findall(r"[\w'’-]+",txt)
    r=align(sys.argv[1],ws)
    for w,(x,y) in zip(ws,r): print(f'{x:6.2f} {y:6.2f} {w}')
