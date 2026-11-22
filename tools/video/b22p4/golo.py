# Goal = the real white posts, crossbar and net lines inside the goal area (people in front drop out by themselves)
import cv2,numpy as np,glob,pickle
F=sorted(glob.glob('fr/*.png')); fr=[cv2.imread(f) for f in F]; N=len(fr); H,W=fr[0].shape[:2]
gray=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) for f in fr]
posts0=[((516,182),(516,598)),((508,178),(1066,157)),((1056,160),(1056,628))]
poly0=np.float32([(498,176),(1066,152),(1139,191),(1178,608),(1066,632),(1044,627),(503,602)])
T=pickle.load(open('tracks2.pkl','rb'))
sift=cv2.SIFT_create(5000); bf=cv2.BFMatcher()
def mask_bg(t):  # skip the moving people/ball when measuring camera motion
    m=np.full((H,W),255,np.uint8)
    for k in ('cabeca','bola'): m[cv2.dilate(T[k][t].astype(np.uint8),np.ones((61,61),np.uint8))>0]=0
    ys,xs=np.nonzero(T['cabeca'][t]); m[ys.min():H, max(0,xs.min()-150):xs.max()+120]=0  # Tiago's body
    return m
k0,d0=sift.detectAndCompute(gray[0],mask_bg(0)); out=[]
K=np.ones((31,31),np.uint8)
for t in range(N):
    if t==0: Hm=np.eye(3)
    else:
        k1,d1=sift.detectAndCompute(gray[t],mask_bg(t))
        mt=[m for m,n in bf.knnMatch(d0,d1,k=2) if m.distance<0.75*n.distance]
        p0=np.float32([k0[m.queryIdx].pt for m in mt]); p1=np.float32([k1[m.trainIdx].pt for m in mt])
        Hm,_=cv2.findHomography(p0,p1,cv2.RANSAC,2.5)
    poly=cv2.perspectiveTransform(poly0[None],Hm)[0]
    reg=np.zeros((H,W),np.uint8); cv2.fillPoly(reg,[poly.astype(np.int32)],1)
    hsv=cv2.cvtColor(fr[t],cv2.COLOR_BGR2HSV); V=hsv[...,2]; Sat=hsv[...,1]
    posts=np.zeros((H*4,W*4),np.uint8)
    for p,q in posts0:
        P,Q=cv2.perspectiveTransform(np.float32([[p,q]]),Hm)[0]; L=np.linalg.norm(Q-P); u=(Q-P)/L; nv=np.array([-u[1],u[0]])
        offs=np.arange(-26,26.5,0.5); ts=np.linspace(0.05,0.95,120)
        mx=(P[0]+np.outer(ts*L,np.ones_like(offs))*u[0]+offs[None]*nv[0]).astype(np.float32)
        my=(P[1]+np.outer(ts*L,np.ones_like(offs))*u[1]+offs[None]*nv[1]).astype(np.float32)
        prof=np.median(cv2.remap(V.astype(np.float32),mx,my,cv2.INTER_LINEAR),0)
        prof=cv2.GaussianBlur(prof[None],(1,0),1.2,borderType=cv2.BORDER_REPLICATE)[0] if False else np.convolve(prof,np.ones(3)/3,'same')
        c=len(offs)//2; br=prof[c-8:c+9].argmax()+c-8   # brightest line near the centre = post
        lo=br-1
        while lo>2 and not (prof[lo]<prof[lo-1] and prof[lo]<prof[br]-25): lo-=1
        hi=br+1
        while hi<len(prof)-3 and not (prof[hi]<prof[hi+1] and prof[hi]<prof[br]-25): hi+=1
        o1,o2=offs[lo]+0.5,offs[hi]-0.5
        quad=np.float32([P+nv*o1-u*4,Q+nv*o1+u*4,Q+nv*o2+u*4,P+nv*o2-u*4])*4
        cv2.fillPoly(posts,[quad.astype(np.int32)],255,cv2.LINE_AA)
        if t%24==0: print(' post',t,round(o1,1),round(o2,1))
    posts=cv2.resize(posts,(W,H),interpolation=cv2.INTER_AREA).astype(np.float32)/255
    occ=((Sat>95)|(V<120)).astype(np.float32)            # arm/glove/shirt crossing a post
    posts=posts*(1-cv2.GaussianBlur(occ,(0,0),1.0))
    thin=cv2.morphologyEx(V,cv2.MORPH_TOPHAT,np.ones((5,5),np.uint8)).astype(np.int16)
    net=((thin>16)&(Sat<70)&(reg>0)).astype(np.uint8)
    n,l,st,_=cv2.connectedComponentsWithStats(net)
    big=np.nonzero((np.maximum(st[:,2],st[:,3])>=14)&~((st[:,2]>70)&(st[:,3]<9)))[0]; big=big[big>0]
    net=np.isin(l,big).astype(np.uint8)
    m=net
    a=np.maximum(np.clip(cv2.ximgproc.guidedFilter(fr[t],m.astype(np.float32),1,1e-3),0,1),posts)
    out.append(a)
    if t%24==0: print(t,int(m.sum()))
# light temporal smoothing
sm=[np.clip((out[max(0,t-1)]+2*out[t]+out[min(N-1,t+1)])/4,0,1) for t in range(N)]
ball=pickle.load(open('ballmatte.pkl','rb'))
R=pickle.load(open('roto.pkl','rb')); R['golo']=[(np.maximum(sm[t],ball[t])*255).astype(np.uint8) for t in range(N)]
pickle.dump(R,open('roto.pkl','wb'))
f=fr[40].copy(); f[sm[40]>0.5]=(0,255,255); cv2.imwrite('golo_chk.jpg',f)
