import cv2,numpy as np,pickle,glob
F=sorted(glob.glob('fr/*.png')); N=len(F); H,W=720,1280
T=pickle.load(open('track_v2.pkl','rb')); KP=pickle.load(open('keeper.pkl','rb')); G=pickle.load(open('golo_v2.pkl','rb'))
gray=[cv2.cvtColor(cv2.imread(f),cv2.COLOR_BGR2GRAY) for f in F]
dis=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM); yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
warp=lambda a,fl:cv2.remap(a,xx+fl[...,0],yy+fl[...,1],cv2.INTER_LINEAR)
R={'cabeca':[],'rita':[]}
for t in range(N):
    b=dis.calc(gray[t],gray[t-1],None) if t else None; f=dis.calc(gray[t],gray[t+1],None) if t<N-1 else None
    for k in R:
        A=lambda i:T[k][i].astype(np.float32)/255
        acc=2*A(t); w=2
        if b is not None: acc=acc+warp(A(t-1),b); w+=1
        if f is not None: acc=acc+warp(A(t+1),f); w+=1
        R[k].append((np.clip(acc/w,0,1)*255).astype(np.uint8))

R['bola']=T['bola']
del gray
K9=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(11,11))
gol=[]
for t in range(N):
    k=cv2.morphologyEx((KP[t]>127).astype(np.uint8),cv2.MORPH_OPEN,K9)        # strip net strings from the keeper cut
    n,l,st,_=cv2.connectedComponentsWithStats(k)
    if n>1: k=(l==1+st[1:,4].argmax()).astype(np.uint8)
    occ=np.maximum(cv2.dilate(k,np.ones((7,7),np.uint8)),cv2.dilate((R['rita'][t]>100).astype(np.uint8),np.ones((7,7),np.uint8))).astype(np.float32)
    g=G[t].astype(np.float32)/255*(1-cv2.GaussianBlur(occ,(0,0),1.5))
    gol.append((np.maximum(g,R['bola'][t].astype(np.float32)/255)*255).astype(np.uint8))
out=dict(R); out['golo']=gol
pickle.dump(out,open('roto_v2.pkl','wb'))
for t in (50,150):
    f=cv2.imread(F[t]); f[gol[t]>127]=(0,255,255); cv2.imwrite(f'golo_fin{t}.jpg',cv2.resize(f,(640,360)))
print('ok')
