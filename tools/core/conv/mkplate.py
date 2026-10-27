"""Make a clean-plate overlay for a move cue: python3 conv/mkplate.py <story> <idx> <key> <plate_raw.png>"""
import sys, glob, os, pickle, json, numpy as np, cv2
from PIL import Image
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'
A=S+'artifact-files/87e1712e-5e90-4175-b828-2581544915d4/'
sid,idx,key,raw=sys.argv[1],int(sys.argv[2]),sys.argv[3],sys.argv[4]
f=sorted(glob.glob(S+f'gen/hlcache/{sid}_{idx}_*.pkl'),key=os.path.getmtime)[-1]
arr,regions,_,_=pickle.load(open(f,'rb'))
m=np.zeros(arr.shape[:2],np.uint8)
for k,r in regions:
    if key in k.split(): m|=(r>0).astype(np.uint8)
m=cv2.dilate(m,np.ones((15,15),np.uint8)); a=np.clip(cv2.GaussianBlur(m.astype(np.float32),(0,0),5)*1.3,0,1)
ys,xs=np.nonzero(a>0.01); x0,y0,x1,y1=xs.min(),ys.min(),xs.max()+1,ys.max()+1
P=np.asarray(Image.open(raw).convert('RGB').resize((1600,898),Image.LANCZOS))
os.makedirs(A+'img/act',exist_ok=True)
name=f'img/act/{sid}{idx}{key}.webp'
Image.fromarray(np.dstack([P[y0:y1,x0:x1],(a[y0:y1,x0:x1]*255).astype(np.uint8)]),'RGBA').save(A+name,quality=85,method=6)
SX,SY=465.8/1600,260/898
box=[round(float(x0*SX),1),round(float(y0*SY),1),round(float((x1-x0)*SX),1),round(float((y1-y0)*SY),1)]
# preview: original with plate composited
O=arr.astype(np.float32); C=O*(1-a[...,None])+P*a[...,None]
Image.fromarray(np.hstack([arr[y0:y1,x0:x1],C[y0:y1,x0:x1].astype(np.uint8)])).save(S+f'gen/plates/prev_{sid}{idx}{key}.jpg')
print(json.dumps({'plate':name,'pbox':box}))
