"""Book 6 scene life. usage: b6anim.py <page 0-7>"""
import sys, glob, os, pickle, numpy as np, cv2
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'; sys.path.insert(0,S)
import frames as F, windfx
W,H=1600,898; GX,GY=F.GX,F.GY; K=8/7
def regions(i):
    f=sorted(glob.glob(S+f'gen/hlcache/pico_{i}_*.pkl'),key=os.path.getmtime)[-1]
    return {k:m for k,m in pickle.load(open(f,'rb'))[1]}
def soft(m,b=1.5): return np.clip(cv2.GaussianBlur(m.astype(np.float32),(0,0),b),0,1)
def put(i,fr,mask,name,dur):
    base=f'b6p{i+1}'; pa,box=F.save(fr,mask,base,name)
    windfx.add_layer(f'pico:{i}',F.loop(pa,box,dur),f'{base}_{name}'); print(i,name,len(pa),box,flush=True)
def drift_plate(B,area,keep_out=None):
    """inpaint everything outside `area` so only that area's pixels feed a scroll"""
    ys,xs=np.nonzero(area); x0,x1,y0,y1=max(0,xs.min()-80),min(W,xs.max()+80),max(0,ys.min()-30),min(H,ys.max()+30)
    hole=(area==0).astype(np.uint8)
    if keep_out is not None: hole|=keep_out.astype(np.uint8)
    hole=cv2.dilate(hole,np.ones((7,7),np.uint8)); plate=B.copy()
    plate[y0:y1,x0:x1]=cv2.inpaint(np.clip(B[y0:y1,x0:x1],0,255).astype(np.uint8),hole[y0:y1,x0:x1],15,cv2.INPAINT_TELEA)
    return plate
def glints(B,dots,n=24,amp=.5,r=5,seed=7,speed=None):
    """dots (master px) brighten and fade, each on its own phase; speed>0 makes a travelling wave along the list"""
    rng=np.random.default_rng(seed); ph=rng.uniform(0,1,len(dots)) if speed is None else np.arange(len(dots))*speed; out=[]
    for i in range(n):
        g=np.zeros((H,W),np.float32)
        for (x,y),p in zip(dots,ph): cv2.circle(g,(int(x),int(y)),r,float(amp*.5*(1-np.cos(2*np.pi*(i/n+p)))),-1)
        g=cv2.GaussianBlur(g,(0,0),r*.6); out.append(B*(1+g[...,None]))
    return out
i=int(sys.argv[1]); B=F.load(f'b6p{i+1}.jpg'); R=regions(i)
if i==0:   # stars twinkle in the night window
    sky=R['estrelas']; L=F.lum(B)
    st=((L>150)&(sky>0)).astype(np.uint8); n,lb,stt,cen=cv2.connectedComponentsWithStats(st)
    dots=[tuple(cen[k]) for k in range(1,n) if stt[k,4]<60][:70]
    fr=glints(B,dots,amp=.7,r=4); m=np.zeros((H,W),np.float32)
    for x,y in dots: cv2.circle(m,(int(x),int(y)),7,1.,-1)
    put(i,fr,soft(m,1.5),'ls',4)
elif i==1:   # the tunnel lights pulse toward the car, as if streaming past
    lz=R['luzes']; L=F.lum(B); bright=((L>185)&(lz>0)).astype(np.uint8)
    n,lb,stt,cen=cv2.connectedComponentsWithStats(bright)
    pts=[tuple(cen[k]) for k in range(1,n) if stt[k,4]>3]
    vp=(790*K,235*K); pts.sort(key=lambda p:-np.hypot(p[0]-vp[0],p[1]-vp[1]))   # nearest (far from the vanishing point) first
    d=np.array([np.hypot(p[0]-vp[0],p[1]-vp[1]) for p in pts]); ph=-(d/ max(d.max(),1))*1.0
    out=[]
    for f in range(16):
        g=np.zeros((H,W),np.float32)
        for (x,y),p,dd in zip(pts,ph,d):
            r=int(2+dd/90); cv2.circle(g,(int(x),int(y)),r,float(.55*.5*(1-np.cos(2*np.pi*(f/16*3+p*3)))),-1)
        g=cv2.GaussianBlur(g,(0,0),3); out.append(B*(1+g[...,None]))
    put(i,out,soft(cv2.dilate(lz,np.ones((9,9),np.uint8)),3),'ll',1.6)
elif i==2:   # fog drifts past the windows
    fog=R['nevoeiro']; plate=drift_plate(B,fog)
    fr=F.fall_scroll(plate,n=24,P=70.,direction=(-1,0)); put(i,fr,soft(cv2.erode(fog,np.ones((5,5),np.uint8)),3),'lf',8)
elif i==3:   # the sea of clouds rolls slowly
    c=R['nuvens mar branco']; plate=drift_plate(B,c)
    fr=F.fall_scroll(plate,n=24,P=60.,direction=(1,0)); put(i,fr,soft(cv2.erode(c,np.ones((7,7),np.uint8)),4),'lc',24)
elif i==4:   # clouds roll below the summit wall
    m=np.zeros((H,W),np.uint8); cv2.fillPoly(m,[np.array([(0,round(335*K)),(1600,round(335*K)),(1600,round(535*K)),(round(1010*K),round(535*K)),(round(1010*K),round(460*K)),(0,round(560*K))],np.int32)],1)
    ppl=cv2.dilate((R['termometro']|R['radar']).astype(np.uint8),np.ones((9,9),np.uint8))
    for k in R:
        if k in ('gorro','cachecol'): ppl|=cv2.dilate(R[k].astype(np.uint8),np.ones((9,9),np.uint8))
    import hlmask
    L=F.lum(B); cl=((L>175)&(m>0)).astype(np.uint8); cl=cv2.morphologyEx(cl,cv2.MORPH_CLOSE,np.ones((15,15),np.uint8))
    cl[ppl>0]=0
    # keep the people out: everything inside their tight boxes that isn't clearly cloud
    for x0,y0,x1,y1 in [(480,70,665,786),(725,110,935,786),(905,515,1190,786)]:
        cl[round(y0*K):round(y1*K),round(x0*K):round(x1*K)]=0
    plate=drift_plate(B,cl)
    fr=F.fall_scroll(plate,n=24,P=60.,direction=(1,0)); put(i,fr,soft(cv2.erode(cl,np.ones((7,7),np.uint8)),4),'lc',24)
elif i==5:   # the sun glows as it rises; clouds roll slowly
    g=np.zeros((H,W),np.float32); cv2.ellipse(g,(round(628*K),round(185*K)),(round(260*K),round(110*K)),0,0,360,1.,-1); g=cv2.GaussianBlur(g,(0,0),40)
    g[GY>round(200*K)]*=np.clip(1-(GY[GY>round(200*K)]-200*K)/90,0,1)
    fr=F.breathe(B,g,n=24,amp=.10); put(i,fr,np.clip(g*1.3,0,1),'lg',6)
elif i==6:   # steam from the tea
    fr=F.steam(B,round(563*K),round(370*K),height=120,width=40,alpha=.5,lean=-10)
    m=np.zeros((H,W),np.float32); cv2.ellipse(m,(round(560*K),round(325*K)),(60,95),0,0,360,1.,-1); m=soft(m,10)
    put(i,fr,m,'lt',4)
elif i==7:   # the sea moves gently beyond the beach
    sea=np.zeros((H,W),np.uint8); a=B; L=F.lum(a)
    cv2.fillPoly(sea,[np.array([P for P in [(round(700*K),round(360*K)),(1600,round(360*K)),(1600,round(555*K)),(round(1100*K),round(520*K)),(round(760*K),round(445*K))]],np.int32)],1)
    post=R.get('praia'); sea[cv2.dilate(R['termometro graus'],np.ones((5,5),np.uint8))>0]=0
    lamp=np.zeros((H,W),np.uint8); cv2.rectangle(lamp,(round(800*K),0),(round(890*K),H),1,-1); sea[lamp>0]=0
    fr=F.ripple(B,sea.astype(np.float32),n=16,near=2.0,far=.5,lam_near=50,lam_far=14,shine=.04); put(i,fr,soft(sea,1.5),'ls',6)
