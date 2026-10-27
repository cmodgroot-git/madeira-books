"""Moving-vehicle interior (skill madeira-vehicle-interior), approved on book 7 page 8.
The whole view through the glass rides an uneven road (bumps and settles a few px, no blur); in each side window the
scenery passes toward the back of the car, sharp at the window's front edge and increasingly blurred toward its back edge,
blended over the still painting at OPA. The car, people and seats never move.

build(B, glass, sides, lines=None, outside=None, car=None, N=40, T=4.0, OPA=.7) -> frames, alpha
  B       master float32 HxWx3
  glass   uint8 mask of all glass that shows the outside (windscreen + side panes), people/belts/mirror removed
  sides   [(mask, dirn, front_x, back_x)]  dirn -1 = scenery moves left, +1 = right
  lines   float alpha of continuous lines parallel to travel (road edge lines) kept crisp and static in the side glass
  outside f(img, t) -> img   change to the outside view before the bump (e.g. tunnel lights pulsing)
  car     f(img, t) -> img   change in the car's frame after the bump (e.g. wipers, raindrops on the glass)
"""
import numpy as np, cv2
SIG=[0,2,4,7,11,16]
def bump(t,t0,a,f=7.,dmp=6.):
    u=t-t0
    return 0. if u<0 else a*np.exp(-dmp*u)*np.sin(2*np.pi*f*u+np.pi/2)
def jolt(t,T,hits=((0.55,2.6),(2.35,1.6),(3.3,0.9))):
    s=T/4.0
    dy=sum(bump(t+o,t0*s,a) for o in (0,T) for t0,a in hits)+.35*np.sin(2*np.pi*t*3/T)
    rot=np.deg2rad(.06*np.sin(2*np.pi*t/T)+.05*sum(bump(t+o,hits[0][0]*s,1.) for o in (0,T)))
    return dy,rot
def plate(B,glass):
    band=cv2.dilate(glass,np.ones((21,21),np.uint8))&(1-glass)
    return cv2.inpaint(np.clip(B,0,255).astype(np.uint8),band,9,cv2.INPAINT_TELEA).astype(np.float32)
def side_frames(PL,mask,dirn,front,back,N,cycles=2,P=150,K=50):
    H,W=mask.shape; GX=np.arange(W)[None,:].repeat(H,0).astype(np.float32)
    rows=[]
    for y in range(H):
        xs=np.nonzero(mask[y])[0]
        if len(xs)<6: continue
        for rr in np.split(xs,np.nonzero(np.diff(xs)>1)[0]+1):
            if len(rr)<6: continue
            xa,xb=rr[0],rr[-1]+1
            seg=cv2.resize(PL[y:y+1,xa:xb],(P+K,1),interpolation=cv2.INTER_LINEAR)[0]
            w=np.linspace(0,1,K)[:,None]; tile=seg[:P].copy(); tile[:K]=seg[P:P+K]*(1-w)+seg[:K]*w
            rows.append((y,xa,xb,tile))
    ys,xs=np.nonzero(mask); y0,y1,x0,x1=max(0,ys.min()-4),min(H,ys.max()+5),max(0,xs.min()-30),min(W,xs.max()+31)
    mm=mask[y0:y1,x0:x1].astype(np.float32); gx=GX[y0:y1,x0:x1]
    tpos=np.clip((front-gx)/(front-back),0,1) if front>back else np.clip((gx-front)/(back-front),0,1)
    idx=np.interp(1+15*tpos**1.3,SIG,np.arange(len(SIG))); lo=np.floor(idx).astype(int); hi=np.minimum(lo+1,len(SIG)-1); fr=(idx-lo)[...,None]
    out=[]
    for k in range(N):
        lay=PL[y0:y1,x0:x1].copy()
        for y,xa,xb,tile in rows:
            xx=np.arange(xa,xb); off=k*cycles*P/N*dirn
            lay[y-y0,xa-x0:xb-x0]=tile[np.mod(np.round((xx-xa)*P/(xb-xa)-off).astype(int),P)]
        st=[lay]
        for s in SIG[1:]:
            num=cv2.GaussianBlur(lay*mm[...,None],(0,0),sigmaX=s,sigmaY=.6); den=cv2.GaussianBlur(mm,(0,0),sigmaX=s,sigmaY=.6)[...,None]
            st.append(num/np.maximum(den,1e-3))
        st=np.stack(st,0)
        res=np.take_along_axis(st,lo[None,...,None].repeat(3,-1),0)[0]*(1-fr)+np.take_along_axis(st,hi[None,...,None].repeat(3,-1),0)[0]*fr
        out.append(((y0,y1,x0,x1),res,mm))
    return out
def build(B,glass,sides,lines=None,outside=None,car=None,N=40,T=4.0,OPA=.7,cycles=2):
    H,W=glass.shape; GX,GY=np.meshgrid(np.arange(W,dtype=np.float32),np.arange(H,dtype=np.float32))
    PL=plate(B,glass)
    SF=[(m,side_frames(PL,m,d,f,b,N,cycles)) for m,d,f,b in sides]
    frames=[]
    for k in range(N):
        t=k/N*T; img=PL.copy()
        for m,fs in SF:
            (y0,y1,x0,x1),res,mm=fs[k]; sub=img[y0:y1,x0:x1]
            sub[:]=np.where(mm[...,None]>0,PL[y0:y1,x0:x1]*(1-OPA)+res*OPA,sub)
        if lines is not None: img=img*(1-lines[...,None])+PL*lines[...,None]
        if outside is not None: img=outside(img,t)
        dy,rot=jolt(t,T); cx,cy=W/2,H/3; c,s=np.cos(rot),np.sin(rot)
        mx=cx+(GX-cx)*c-(GY-cy)*s; my=cy+(GX-cx)*s+(GY-cy)*c-dy
        img=cv2.remap(img,mx.astype(np.float32),my.astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
        if car is not None: img=car(img,t)
        frames.append(img)
    return frames
def crisp_line(B,pane,band_y=330,maxx=None):
    """fit a straight anti-aliased band to a bright, low-saturation road line inside a pane"""
    H,W=pane.shape; hsv=cv2.cvtColor(np.clip(B,0,255).astype(np.uint8),cv2.COLOR_RGB2HSV)
    GY=np.arange(H)[:,None].repeat(W,1)
    L=((hsv[...,2]>150)&(hsv[...,1]<45)&(pane>0)&(GY>band_y)).astype(np.uint8)
    n,lb,st,_=cv2.connectedComponentsWithStats(L); L=np.isin(lb,[i for i in range(1,n) if st[i,2]>25])
    ys,xs=np.nonzero(L)
    if len(xs)<30: return np.zeros((H,W),np.float32)
    k,c=np.linalg.lstsq(np.vstack([xs,np.ones_like(xs)]).T,ys,rcond=None)[0]; half=max(3.,np.percentile(np.abs(ys-(k*xs+c)),90))
    big=np.zeros((H*4,W*4),np.uint8); x0,x1=xs.min()-30,(maxx if maxx else xs.max()+30)
    cv2.line(big,(int(x0*4),int((k*x0+c)*4)),(int(x1*4),int((k*x1+c)*4)),255,int(half*8),cv2.LINE_AA)
    return cv2.GaussianBlur(cv2.resize(big,(W,H),interpolation=cv2.INTER_AREA).astype(np.float32)/255*pane,(0,0),.7)
