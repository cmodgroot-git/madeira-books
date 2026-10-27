import pickle,numpy as np,sys
sys.path.insert(0,'.'); import frames as F
from PIL import Image
B=F.load('b4p2.jpg'); w,wm=pickle.load(open('b4p2new/water.pkl','rb')); fr,al=pickle.load(open('b4p2new/splash.pkl','rb'))
ks=[int(a) for a in sys.argv[1].split(',')]
o=Image.new('RGB',(4*500,((len(ks)+3)//4)*250))
for j,k in enumerate(ks):
  x=B*(1-wm[...,None])+w[k%16]*wm[...,None]; a=al[k][...,None]; x=x*(1-a)+fr[k]*a
  o.paste(Image.fromarray(np.clip(x,0,255).astype(np.uint8)).crop((380,280,960,570)).resize((500,250)),((j%4)*500,(j//4)*250))
o.save('conv/first.jpg',quality=88)
