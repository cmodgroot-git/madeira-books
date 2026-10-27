import sys,numpy as np,torch; sys.path.insert(0,'.'); import align
p,m=align.load()
def dec(path,t0=0,t1=None):
    a=align.wav(path); a=a[int(t0*16000):int(t1*16000) if t1 else None]
    with torch.no_grad(): ids=m(torch.tensor(p(a,sampling_rate=16000,return_tensors='pt').input_values[0])[None]).logits[0].argmax(-1)
    return p.decode(ids)
if __name__=='__main__':
  for spec in sys.argv[1:]:
    f,a,b=spec.split(':'); print(spec,'->',dec(f,float(a),float(b)))
