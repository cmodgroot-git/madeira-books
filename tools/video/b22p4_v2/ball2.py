import cv2,numpy as np,glob,pickle
F=sorted(glob.glob('fr/*.png')); N=len(F); H,W=720,1280
TR=pickle.load(open('track_sam.pkl','rb'))
K={}
for t in range(0,31,5):   # the AI tracker was right for the first 30 frames
    ys,xs=np.nonzero(TR['bola'][t]>127); K[t]=(xs.mean(),ys.mean(),np.sqrt(len(xs)/np.pi))
K.update({40:(842,128,31),46:(910,190,26),52:(924,220,26),58:(902,228,26),64:(854,262,24),70:(812,304,24),76:(764,364,24),
 82:(728,406,22),90:(686,592,26),98:(660,570,28),106:(636,588,29),114:(658,592,28),124:(720,586,28),134:(790,592,26),
 160:(976,572,26),175:(1010,572,26),190:(1020,576,25),210:(1026,580,25),230:(1026,580,25),250:(1026,582,25),270:(1026,582,25),283:(1024,578,25)})
ks=sorted(K); kv=np.array([K[k] for k in ks]); I=np.stack([np.interp(range(N),ks,kv[:,i]) for i in range(3)],1)
P=I.copy(); used=0
for t in range(N):
    g=cv2.GaussianBlur(cv2.cvtColor(cv2.imread(F[t]),cv2.COLOR_BGR2GRAY),(0,0),1.2)
    x,y,r=I[t]; R=int(r*2+14); x0,y0=int(max(0,x-R)),int(max(0,y-R)); x1,y1=int(min(W,x+R)),int(min(H,y+R))
    best=None
    for p2 in (28,20,14):
        cs=cv2.HoughCircles(g[y0:y1,x0:x1],cv2.HOUGH_GRADIENT,1.2,8,param1=90,param2=p2,minRadius=int(r*0.75),maxRadius=int(r*1.25))
        if cs is None: continue
        for cx,cy,cr in cs[0][:10]:
            d=np.hypot(cx+x0-x,cy+y0-y)
            if d<10 and (best is None or d<best[0]): best=(d,cx+x0,cy+y0,cr)
        if best: break
    if best and t not in K: P[t]=(best[1],best[2],0.5*best[3]+0.5*r); used+=1
sm=P.copy()
for t in range(1,N-1): sm[t]=0.25*P[t-1]+0.5*P[t]+0.25*P[t+1]
def nudge(t0,dx,dy,w=4):
    for t in range(max(0,t0-w),min(N,t0+w+1)):
        k=1-abs(t-t0)/(w+1); sm[t,0]+=dx*k; sm[t,1]+=dy*k
nudge(98,6,6); nudge(160,7,0)
np.save('ball2.npy',sm); print('hough used',used,'of',N)
# mattes: exact disc, faded where the ball is hidden (too little white inside the disc)
out=[]
for t in range(N):
    im=cv2.imread(F[t]); hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV); S=4; x,y,r=sm[t]
    m=np.zeros((H*S,W*S),np.uint8); cv2.circle(m,(int(x*S),int(y*S)),int(r*S),255,-1,cv2.LINE_AA)
    a=cv2.resize(m,(W,H),interpolation=cv2.INTER_AREA).astype(np.float32)/255
    inside=a>0.5; white=((hsv[...,2]>165)&(hsv[...,1]<60))[inside].mean() if inside.any() else 0
    out.append((a,white))
wv=np.array([w for _,w in out]); vis=np.clip((wv-0.12)/0.15,0,1); vis=np.convolve(np.r_[vis[:3][::-1],vis,vis[-3:][::-1]],np.ones(7)/7,'valid')
mattes=[(a*v*255).astype(np.uint8) for (a,_),v in zip(out,vis)]
pickle.dump(mattes,open('ball2.pkl','wb')); print('hidden frames',[t for t in range(N) if vis[t]<0.5])
