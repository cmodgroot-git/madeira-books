# Ball: find the real circle each frame near the keyframed guess (Hough), smooth the path, draw an exact anti-aliased disc
import cv2,numpy as np,pickle,glob
F=sorted(glob.glob('fr/*.png')); fr=[cv2.imread(f) for f in F]; H,W=fr[0].shape[:2]; N=len(fr)
T=pickle.load(open('tracks2.pkl','rb'))
guess=[]
for t in range(N):
    ys,xs=np.nonzero(T['bola'][t]); guess.append((xs.mean(),ys.mean(),np.sqrt(len(xs)/np.pi)))
res=[]; prev=None
for t in range(N):
    gx,gy,gr=guess[t] if prev is None else (0.5*guess[t][0]+0.5*prev[0],0.5*guess[t][1]+0.5*prev[1],prev[2])
    R=int(max(90,gr*2.5)); x0,y0=int(max(0,gx-R)),int(max(0,gy-R)); x1,y1=int(min(W,gx+R)),int(min(H,gy+R))
    g=cv2.GaussianBlur(cv2.cvtColor(fr[t][y0:y1,x0:x1],cv2.COLOR_BGR2GRAY),(0,0),1.5)
    best=None
    for p2 in (40,30,22,16):
        cs=cv2.HoughCircles(g,cv2.HOUGH_GRADIENT,1.2,10,param1=90,param2=p2,minRadius=int(gr*0.6),maxRadius=int(gr*1.5))
        if cs is None: continue
        for cx,cy,r in cs[0][:15]:
            cx+=x0; cy+=y0
            # score: close to guess, and bright (white ball) inside
            m=np.zeros(g.shape,np.uint8); cv2.circle(m,(int(cx-x0),int(cy-y0)),int(r*0.8),1,-1)
            br=g[m>0].mean() if m.sum() else 0
            d=np.hypot(cx-gx,cy-gy)/gr; sc=br/255*1.5-d*0.8-abs(r-gr)/gr
            if best is None or sc>best[0]: best=(sc,cx,cy,r)
        if best: break
    if best is None or np.hypot(best[1]-gx,best[2]-gy)>gr*2.2: best=(0,gx,gy,gr)
    prev=best[1:]; res.append(prev)
res=np.array(res)
# light smoothing (keeps the bounce sharp)
sm=res.copy()
for t in range(1,N-1): sm[t]=0.25*res[t-1]+0.5*res[t]+0.25*res[t+1]
np.save('ballhough.npy',sm)
for t in range(0,N,8): print(t,np.round(res[t]).astype(int).tolist(),np.round(guess[t]).astype(int).tolist())
