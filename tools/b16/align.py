#!/usr/bin/env python3
"""CTC forced alignment of Portuguese narration (wav2vec2 XLSR-53 Portuguese).
  align.py decode <wav>...            transcribe (greedy) to check what was said
  align.py page <wav> <json words>    -> [[startMs,endMs],...] per word group
"""
import sys,json,re,unicodedata,numpy as np,soundfile as sf,torch
from transformers import Wav2Vec2ForCTC,Wav2Vec2Processor
MID='jonatasgrosman/wav2vec2-large-xlsr-53-portuguese'
_M=None
def model():
    global _M
    if _M is None:
        p=Wav2Vec2Processor.from_pretrained(MID); m=Wav2Vec2ForCTC.from_pretrained(MID).eval(); _M=(p,m)
    return _M
def emissions(wav):
    p,m=model(); a,sr=sf.read(wav); assert sr==16000
    with torch.inference_mode():
        x=p(a,sampling_rate=16000,return_tensors='pt').input_values; lp=torch.log_softmax(m(x).logits[0],-1).numpy()
    return lp,len(a)/16000/lp.shape[0]
def decode(wav):
    p,_=model(); lp,_=emissions(wav); ids=lp.argmax(-1)
    return p.decode(ids)
def norm(w,vocab):
    w=w.lower().replace('’',"'")
    out=''.join(c for c in unicodedata.normalize('NFC',w) if c in vocab)
    if not out: out=''.join(c for c in unicodedata.normalize('NFD',w) if c in vocab)
    return out
def align(wav,groups):
    """groups: list of strings (each may hold several words); returns [[s,e] ms] per group"""
    p,_=model(); vocab=p.tokenizer.get_vocab(); blank=p.tokenizer.pad_token_id; sep=vocab.get('|')
    lp,fdur=emissions(wav)
    toks=[];owner=[]
    for gi,g in enumerate(groups):
        ws=[norm(w,vocab) for w in re.split(r"[\s\-]+",g)]; ws=[w for w in ws if w]
        for wi,w in enumerate(ws):
            if toks: toks.append(sep); owner.append(-1)
            for c in w: toks.append(vocab[c]); owner.append(gi)
    T,N=lp.shape[0],len(toks)
    # Viterbi over CTC (with blanks between tokens)
    ext=[blank]; own=[-1]
    for t,o in zip(toks,owner): ext+= [t,blank]; own+=[o,-1]
    S=len(ext); NEG=-1e9
    dp=np.full((T,S),NEG); bp=np.zeros((T,S),np.int8)
    dp[0,0]=lp[0,ext[0]]; dp[0,1]=lp[0,ext[1]]
    for t in range(1,T):
        prev=dp[t-1]
        a=prev; b=np.concatenate([[NEG],prev[:-1]]); c=np.concatenate([[NEG,NEG],prev[:-2]])
        allow=np.array([ (s>=2 and ext[s]!=blank and ext[s]!=ext[s-2]) for s in range(S)])
        c=np.where(allow,c,NEG)
        st=np.stack([a,b,c]); k=st.argmax(0); dp[t]=st.max(0)+lp[t,ext]; bp[t]=k
    s=S-1 if dp[T-1,S-1]>dp[T-1,S-2] else S-2; path=[]
    for t in range(T-1,-1,-1):
        path.append(s); s-=int(bp[t,s])
    path=path[::-1]
    span={}
    for t,s in enumerate(path):
        o=own[s]
        if o>=0 and ext[s]!=blank:
            a,b=span.get(o,(t,t)); span[o]=(min(a,t),max(b,t))
    out=[]
    for gi in range(len(groups)):
        if gi in span: a,b=span[gi]; out.append([int(round(a*fdur*1000)),int(round((b+1)*fdur*1000))])
        else: out.append(None)
    # fill gaps (groups with no letters)
    for i,v in enumerate(out):
        if v is None:
            pv=next((out[j] for j in range(i-1,-1,-1) if out[j]),[0,0]); out[i]=[pv[1],pv[1]+20]
    return out
if __name__=='__main__':
    if sys.argv[1]=='decode':
        for w in sys.argv[2:]: print(w,'|',decode(w))
    elif sys.argv[1]=='page': print(json.dumps(align(sys.argv[2],json.loads(sys.argv[3]))))
