import pickle,numpy as np,cv2,sys
sys.path.insert(0,'.'); import frames as F
from PIL import Image
out,mask=pickle.load(open('b4p2new/sea_frames.pkl','rb')); B=F.load('b4p2.jpg'); n=len(out)
fr=[B*(1-mask[...,None])+o*mask[...,None] for o in out]
st=[np.abs(fr[(i+1)%n]-fr[i]).mean() for i in range(n)]
print('steps',np.round(st,2).tolist())
# max step heat
hm=np.max([np.abs(fr[(i+1)%n]-fr[i]).max(2) for i in range(n)],0)
Image.fromarray(np.clip(hm*3,0,255).astype(np.uint8)).resize((800,449)).save('conv/sea_heat.png')
# rock motion: change on rock pixels
LB=F.lum(B); rock=(LB<70)
print('rock max change',max(np.abs(f-B)[rock].max() for f in fr), 'rock mean',np.mean([np.abs(f-B)[rock].mean() for f in fr]))
# hard edges in mask: gradient of mask
g=np.abs(cv2.Sobel(mask,cv2.CV_32F,1,0))+np.abs(cv2.Sobel(mask,cv2.CV_32F,0,1)); print('mask max grad',g.max())
