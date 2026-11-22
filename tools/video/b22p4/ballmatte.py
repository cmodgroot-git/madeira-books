# exact anti-aliased disc per frame, minus skin (knee/hand passing in front)
import cv2,numpy as np,glob,pickle
F=sorted(glob.glob('fr/*.png')); P=np.load('ballpath.npy'); out=[]
for t,f in enumerate(F):
    im=cv2.imread(f); H,W=im.shape[:2]; S=4
    m=np.zeros((H*S,W*S),np.uint8); x,y,r=P[t]
    cv2.circle(m,(int(x*S),int(y*S)),int(r*S),255,-1,cv2.LINE_AA,0)
    a=cv2.resize(m,(W,H),interpolation=cv2.INTER_AREA).astype(np.float32)/255
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV); skin=((hsv[...,0]<25)&(hsv[...,1]>55)&(hsv[...,2]>70)).astype(np.uint8)
    skin=cv2.morphologyEx(skin,cv2.MORPH_OPEN,np.ones((3,3),np.uint8)); skin=cv2.dilate(skin,np.ones((3,3),np.uint8))
    a=a*(1-cv2.GaussianBlur(skin.astype(np.float32),(0,0),1.0)); out.append(np.clip(a,0,1))
pickle.dump(out,open('ballmatte.pkl','wb'))
