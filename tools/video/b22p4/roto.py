# Per-frame rotoscope: flow-propagated prior -> GrabCut at 2x in a local window -> guided-filter alpha -> temporal smoothing
import cv2,numpy as np,pickle,glob
F=sorted(glob.glob('fr/*.png')); fr=[cv2.imread(f) for f in F]; H,W=fr[0].shape[:2]; N=len(fr)
gray=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) for f in fr]
T=pickle.load(open('tracks2.pkl','rb'))
dis=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
dis.setFinestScale(0)
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
back=[None]+[dis.calc(gray[t],gray[t-1],None) for t in range(1,N)]  # flow t -> t-1
fwd=[dis.calc(gray[t],gray[t+1],None) for t in range(N-1)]+[None]  # flow t -> t+1
def warp(a,fl): return cv2.remap(a.astype(np.float32),xx+fl[...,0],yy+fl[...,1],cv2.INTER_LINEAR)
K=lambda r:cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*r+1,2*r+1))
def cut(t,prior,limit,sure=4,S=2,lim_px=18,band=10,nowhite=False):
    """prior: float 0..1 shape guess; limit: bool, nothing outside dilate(limit) can be object"""
    lim=cv2.dilate(limit.astype(np.uint8),K(lim_px))>0
    ys,xs=np.nonzero(lim)
    x0,y0=max(0,xs.min()-30),max(0,ys.min()-30); x1,y1=min(W,xs.max()+30),min(H,ys.max()+30)
    crop=cv2.resize(fr[t][y0:y1,x0:x1],None,fx=S,fy=S,interpolation=cv2.INTER_LANCZOS4)
    pf=cv2.resize(prior[y0:y1,x0:x1],(crop.shape[1],crop.shape[0])); p=pf>0.25; both=pf>0.75
    l=cv2.resize(lim[y0:y1,x0:x1].astype(np.uint8),(crop.shape[1],crop.shape[0]))>0
    gc=np.where(p,cv2.GC_PR_FGD,cv2.GC_PR_BGD).astype(np.uint8)
    gc[cv2.erode(both.astype(np.uint8),K(sure*S))>0]=cv2.GC_FGD
    gc[~l]=cv2.GC_BGD; gc[~(cv2.dilate(p.astype(np.uint8),K(band*S))>0)]=cv2.GC_BGD
    if nowhite:
        hsv=cv2.cvtColor(crop,cv2.COLOR_BGR2HSV); wb=(hsv[...,1]<45)&(hsv[...,2]>185)
        gc[wb&~(cv2.erode(p.astype(np.uint8),K(10*S))>0)]=cv2.GC_BGD
    if (gc==cv2.GC_FGD).sum()<20 or (gc==cv2.GC_BGD).sum()<20: return (prior>0.5).astype(np.float32)
    bg=np.zeros((1,65)); fg=np.zeros((1,65))
    cv2.grabCut(crop,gc,None,bg,fg,4,cv2.GC_INIT_WITH_MASK)
    m=((gc==cv2.GC_FGD)|(gc==cv2.GC_PR_FGD)).astype(np.uint8)
    # keep components touching the sure core, close tiny holes
    n,lab=cv2.connectedComponents(m); core=cv2.erode(both.astype(np.uint8),K(sure*S))>0
    keep=np.isin(lab,np.unique(lab[core&(lab>0)])); m=cv2.morphologyEx(keep.astype(np.uint8),cv2.MORPH_CLOSE,K(2*S))
    ff=np.pad(m,1).copy(); cv2.floodFill(ff,None,(0,0),2); m=((ff[1:-1,1:-1]!=2)).astype(np.uint8)  # fill holes
    a=cv2.ximgproc.guidedFilter(crop,m.astype(np.float32),2*S,1e-3)   # edge-hugging soft alpha
    a=cv2.resize(np.clip(a,0,1),(x1-x0,y1-y0),interpolation=cv2.INTER_AREA)
    out=np.zeros((H,W),np.float32); out[y0:y1,x0:x1]=a; return out
_AN={}
def rita_warps(m0):
    # Rita is still; follow the camera using features in a window around her (RANSAC ignores the keeper diving through)
    ys,xs=np.nonzero(m0>0.5); cx,cy=xs.mean(),ys.mean(); hw,hh=(xs.max()-xs.min())*2.2,(ys.max()-ys.min())*1.1
    def win(t,Hm):
        c=cv2.perspectiveTransform(np.float32([[[cx,cy]]]),Hm)[0,0]
        m=np.zeros((H,W),np.uint8); cv2.rectangle(m,(int(c[0]-hw),int(c[1]-hh)),(int(c[0]+hw),int(c[1]+hh)),255,-1); return m
    sift=cv2.SIFT_create(4000); k0,d0=sift.detectAndCompute(gray[0],win(0,np.eye(3))); bf=cv2.BFMatcher()
    Hm=np.eye(3); out=[np.eye(3)]
    for t in range(1,N):
        k1,d1=sift.detectAndCompute(gray[t],win(t,Hm))
        mt=[m for m,n in bf.knnMatch(d0,d1,k=2) if m.distance<0.75*n.distance]
        if len(mt)>12:
            p0=np.float32([k0[m.queryIdx].pt for m in mt]); p1=np.float32([k1[m.trainIdx].pt for m in mt])
            A,inl=cv2.estimateAffine2D(p0,p1,method=cv2.RANSAC,ransacReprojThreshold=2.5)
            if A is not None and inl.sum()>10: Hm=np.vstack([A,[0,0,1]])
        out.append(Hm.copy())
        if t%16==0: print('rita cam',t,len(mt),np.round(Hm[:2],3).tolist(),flush=True)
    return [h[:2].astype(np.float32) for h in out]
def anchor(m0,t0,t1):
    if 'w' in _AN:
        t=_AN['idx'][id(t1)]; return cv2.warpAffine(m0.astype(np.float32),_AN['w'][t],(W,H))
    # move m0 by the translation+scale that takes track mask t0 to t1
    def st(m):
        ys,xs=np.nonzero(m); return xs.mean(),ys.mean(),np.sqrt(len(xs))
    a,b,c=st(t0); d,e,f=st(t1); k=f/c
    M=np.float32([[k,0,d-k*a],[0,k,e-k*b]]); return cv2.warpAffine(m0.astype(np.float32),M,(W,H))
def roto(key,limits,sure=4,first=None,follow=False,**kw):
    A=[]; prev=None
    for t in range(N):
        if t==0: prior=first if first is not None else limits[0].astype(np.float32); lim=limits[0] if first is None else first>0.5
        elif follow:  # deforming body: rigidly carried first cut is the anchor; flow-carried last cut adds the moving arms
            an=anchor(first,limits[0],limits[t]); w=np.clip(warp(prev,back[t]),0,1)
            core=np.minimum(cv2.erode(an,K(6)),w); uni=np.maximum(cv2.dilate(an,K(6)),w)
            prior=np.where(core>0.5,1.0,np.where(uni>0.5,0.5,0.0)).astype(np.float32)
            lim=cv2.dilate((uni>0.5).astype(np.uint8),K(14))>0
        else:
            tr=limits[t].astype(np.float32); prior=0.5*tr+0.5*np.clip(warp(prev,back[t]),0,1); lim=limits[t]
        a=np.asarray(cut(t,prior,lim,sure,**kw),np.float32)
        if follow and t:  # body below the shoulders = carried first cut; re-cut only head/arms/hands
            an=anchor(first,limits[0],limits[t]); ys=np.nonzero(an>0.5)[0]; y0,y1=ys.min(),ys.max(); ysp=y0+int(0.42*(y1-y0))
            top=np.zeros_like(an); top[:ysp]=1; top=cv2.GaussianBlur(top,(0,0),4)
            a=np.maximum(an*(1-top), np.maximum(a,cv2.erode(an,K(2)))*top)
        ar,pr=(a>0.5).sum(),((anchor(first,limits[0],limits[t]) if (follow and t) else prior)>0.5).sum()
        if pr>0 and not ((0.8 if follow else 0.75)<ar/pr<(1.7 if follow else 1.35)): a=prior if not follow else np.maximum(np.asarray(prior>0.75,np.float32),a*(prior>0))
        A.append(a); prev=a
        if t%16==0: print(key,t,int(ar),int(pr),flush=True)
    # temporal smoothing with flow-aligned neighbours (removes edge flicker)
    S=[]
    for t in range(N):
        acc=[A[t]*2]; w=2
        if t>0: acc.append(warp(A[t-1],back[t])); w+=1
        if t<N-1: acc.append(warp(A[t+1],fwd[t])); w+=1
        S.append(np.clip(sum(acc)/w,0,1))
    return S
R={}
head0=cv2.erode(T['cabeca'][0].astype(np.uint8),K(5)).astype(np.float32)   # drop the inflate from the page cut-out
R['cabeca']=roto('cabeca',T['cabeca'],10,first=head0,lim_px=8,band=4,nowhite=True)
# Rita: re-cut frame 0 from the rough outline, then follow her body by flow so the clapping arms stay in
r0=T['rita'][0]; init=cut(0,cv2.erode(r0.astype(np.uint8),K(6)).astype(np.float32),cv2.dilate(r0.astype(np.uint8),K(16))>0,10,lim_px=16,band=14)
_AN['w']=rita_warps(np.asarray(init,np.float32)); _AN['idx']={id(m):i for i,m in enumerate(T['rita'])}
R['rita']=roto('rita',T['rita'],4,first=np.asarray(init,np.float32),follow=True,lim_px=4,band=10)
R['bola']=pickle.load(open('ballmatte.pkl','rb'))
R['golo']=[np.clip(cv2.ximgproc.guidedFilter(fr[t],T['golo'][t].astype(np.float32),3,1e-3),0,1) for t in range(N)]
for t in range(N): R['golo'][t]=np.maximum(R['golo'][t],R['bola'][t])
pickle.dump({k:[(np.clip(a,0,1)*255).astype(np.uint8) for a in v] for k,v in R.items()},open('roto.pkl','wb')); print('saved')
