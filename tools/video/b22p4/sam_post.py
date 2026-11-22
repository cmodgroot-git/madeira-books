import cv2,numpy as np,pickle,glob
F=sorted(glob.glob('fr/*.png')); fr=[cv2.imread(f) for f in F]; N=len(F); H,W=fr[0].shape[:2]
S=pickle.load(open('sam_out.pkl','rb')); R=pickle.load(open('roto.pkl','rb'))
gray=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) for f in fr]
dis=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM); yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
def warp(a,fl): return cv2.remap(a,xx+fl[...,0],yy+fl[...,1],cv2.INTER_LINEAR)
# Rita: nothing below her shoe soles (the keeper's head slides in under her feet)
for t in range(N):
    a=S['rita'][t]; ys,xs=np.nonzero(a>0.5); y0,y1=ys.min(),ys.max()
    hsv=cv2.cvtColor(fr[t],cv2.COLOR_BGR2HSV); white=(hsv[...,2]>175)&(hsv[...,1]<55)&(a>0.5)
    wy=np.nonzero(white[y0+int(0.8*(y1-y0)):y1+1].any(1))[0]
    if len(wy): cut=y0+int(0.8*(y1-y0))+wy.max()+3; a[cut:]=0
    ys,xs=np.nonzero(a>0.5); y0,y1=ys.min(),ys.max(); yb=y0+int(0.86*(y1-y0))
    keep=((hsv[...,1]<80)&(hsv[...,2]>115))|((hsv[...,0]>=95)&(hsv[...,0]<=125)&(hsv[...,2]>70))   # shoes or denim
    bad=np.zeros((H,W),np.uint8); bad[yb:]=(~keep[yb:]).astype(np.uint8); bad=cv2.morphologyEx(bad,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    a=a*(1-cv2.GaussianBlur(bad.astype(np.float32),(0,0),1.0))
    n,l,st,_=cv2.connectedComponentsWithStats((a>0.5).astype(np.uint8))
    if n>2: big=1+st[1:,4].argmax(); a*=cv2.dilate((l==big).astype(np.uint8),np.ones((5,5),np.uint8))
    S['rita'][t]=a
# temporal smoothing with flow-aligned neighbours
for k in S:
    A=S[k]; out=[]
    for t in range(N):
        acc=2*A[t]; w=2
        if t>0: acc=acc+warp(A[t-1],dis.calc(gray[t],gray[t-1],None)); w+=1
        if t<N-1: acc=acc+warp(A[t+1],dis.calc(gray[t],gray[t+1],None)); w+=1
        out.append(np.clip(acc/w,0,1))
    R[k]=[(a*255).astype(np.uint8) for a in out]
pickle.dump(R,open('roto_final.pkl','wb')); print('ok')
