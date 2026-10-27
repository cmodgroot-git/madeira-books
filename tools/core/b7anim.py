"""Book 7 scene life. usage: b7anim.py <page 0-7> [preview]"""
import sys, glob, os, pickle, numpy as np, cv2
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'; sys.path.insert(0,S)
import frames as F, windfx, vehlife
W,H=1600,898; GX,GY=F.GX,F.GY
def regions(i):
    f=sorted(glob.glob(S+f'gen/hlcache/seixal_{i}_*.pkl'),key=os.path.getmtime)[-1]
    return {k:m for k,m in pickle.load(open(f,'rb'))[1]}
def soft(m,b=1.5): return np.clip(cv2.GaussianBlur(m.astype(np.float32),(0,0),b),0,1)
def poly(*p):
    m=np.zeros((H,W),np.uint8); cv2.fillPoly(m,[np.array(p,np.int32)],1); return m
PREV=len(sys.argv)>2
def put(i,fr,mask,name,dur):
    if PREV:
        from PIL import Image
        mm=np.clip(mask,0,1)[...,None]; a=[np.clip(fr[k]*mm+B*(1-mm),0,255).astype(np.uint8) for k in (0,len(fr)//2)]
        Image.fromarray(np.concatenate(a,0)).resize((800,900)).save(S+f'conv/b7a_{i}_{name}.jpg',quality=82); print('preview',name); return
    base=f'b7p{i+1}'; pa,box=F.save(fr,mask,base,name)
    windfx.add_layer(f'seixal:{i}',F.loop(pa,box,dur),f'{base}_{name}'); print(i,name,len(pa),box,flush=True)
def people(R,keys):
    m=np.zeros((H,W),np.uint8)
    for k in keys:
        if k in R: m|=R[k].astype(np.uint8)
    return cv2.dilate(m,np.ones((15,15),np.uint8))
def seamask(y0,y1,x0=0,x1=W,extra=None):
    """sea pixels: bluish/teal or white foam, within a box"""
    a=B; r,g,b=a[...,0],a[...,1],a[...,2]; L=F.lum(a)
    m=(((b>r+4)|(g>r+4)|(L>200))&(GY>=y0)&(GY<y1)&(GX>=x0)&(GX<x1)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8)); m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
    if extra is not None: m&=extra
    return m
def waterfall(B,m,n=24,P=240,seed=11):
    """falling water drawn from the painting's own colours: soft vertical streaks that speed up as they fall,
    each row mapped across the fall's width so streaks follow its shape; spray breathes where it meets the sea"""
    m=(m>0).astype(np.uint8); ys,xs=np.nonzero(m); y0,y1=ys.min(),ys.max()
    rng=np.random.default_rng(seed); U=48
    noise=rng.random((P,U)).astype(np.float32)
    tex=cv2.GaussianBlur(np.concatenate([noise]*3,0),(0,0),sigmaX=1.1,sigmaY=9)[P:2*P]     # long thin streaks, periodic in v
    tex=(tex-tex.mean())/tex.std()
    # where each row's span starts/ends
    span={y:(np.nonzero(m[y])[0].min(),np.nonzero(m[y])[0].max()+1) for y in range(y0,y1+1) if m[y].any()}
    col=np.percentile(B[m>0],85,axis=0)                       # the fall's light colour
    base=B.copy(); out=[]
    soft_m=np.clip(cv2.GaussianBlur(m.astype(np.float32),(0,0),1.3),0,1)
    for k in range(n):
        f=base.copy(); a=np.zeros((H,W),np.float32)
        for y,(xa,xb) in span.items():
            t=(y-y0)/max(1,y1-y0)
            v=(y - y0)*(1+0.8*t) - k*P/n*(1.0+0.6*t)            # accelerating fall: streaks stretch and speed up lower down
            row=tex[int(np.floor(v))%P]
            u=np.linspace(0,U-1,xb-xa); a[y,xa:xb]=np.interp(u,np.arange(U),row)
        a=np.clip(a*.5+.15,-.6,1.2)*soft_m
        light=np.clip(a,0,None)[...,None]*.55; dark=np.clip(-a,0,None)[...,None]*.18
        f=f*(1-light)+col*light; f=f*(1-dark)
        # spray at the foot of the fall
        cx=int(np.mean(np.nonzero(m[y1-3])[0])) if m[y1-3].any() else int(xs.mean())
        mist=np.zeros((H,W),np.float32); cv2.ellipse(mist,(cx,y1+4),(34,14),0,0,360,1.,-1); mist=cv2.GaussianBlur(mist,(0,0),7)
        pulse=.28+.12*np.sin(2*np.pi*k/n*2)
        f=f*(1-mist[...,None]*pulse)+np.float32([248,248,244])*mist[...,None]*pulse
        out.append(f)
    mm=np.clip(soft_m+np.clip(cv2.GaussianBlur(cv2.dilate(m,np.ones((3,3),np.uint8)).astype(np.float32),(0,0),2),0,1),0,1)
    spray=np.zeros((H,W),np.float32); cv2.ellipse(spray,(int(xs.mean()),y1+4),(48,24),0,0,360,1.,-1)
    return out,np.clip(np.maximum(mm,cv2.GaussianBlur(spray,(0,0),6)*1.5),0,1)
i=int(sys.argv[1]); B=F.load(f'b7p{i+1}.jpg'); R=regions(i)
if i==0:   # steam rises from Ana's coffee, leaning away from her face
    fr=F.steam(B,640,402,height=105,width=36,alpha=.5,lean=34)
    m=np.zeros((H,W),np.float32); cv2.ellipse(m,(672,335),(70,85),0,0,360,1.,-1); put(i,fr,soft(m,10),'lt',4)
elif i==1:   # waves beyond the wall, the pool ripples gently
    ppl=people(R,['senhor','ana'])
    sea=seamask(215,440,560,W)&(1-ppl); fr=F.ripple(B,sea.astype(np.float32),n=16,near=2.8,far=.8,lam_near=50,lam_far=14,shine=.05)
    put(i,fr,soft(sea,1.2),'ls',5)
    pool=poly((790,450),(1060,440),(1340,450),(1380,500),(1300,560),(1000,570),(790,530))&seamask(430,580,780,1400)&(1-ppl)
    fr=F.ripple(B,pool.astype(np.float32),n=16,near=1.2,far=.6,lam_near=40,lam_far=16,shine=.04); put(i,fr,soft(pool,1.2),'lp',6)
elif i==2:   # the waterfall falls; the sea moves around the surfers
    fr,mw=waterfall(B,R['cascata']); put(i,fr,mw,'lw',1.5)
    ppl=people(R,['joao','surfistas','prancha','praia areia'])
    sea=seamask(330,760)&(1-ppl)&(1-cv2.dilate(R['praia areia'].astype(np.uint8),np.ones((5,5),np.uint8)))
    girls=poly((30,300),(130,100),(330,100),(390,330),(390,898),(80,898))|poly((290,330),(355,160),(475,150),(545,320),(640,400),(640,470),(560,560),(540,898),(310,898))
    hand=np.zeros((H,W),np.uint8); cv2.ellipse(hand,(585,345),(70,100),0,0,360,1,-1); dog=poly((480,630),(560,590),(715,590),(735,700),(710,875),(485,875))
    sea&=(1-cv2.dilate(girls|hand|dog,np.ones((15,15),np.uint8)))
    fr=F.ripple(B,sea.astype(np.float32),n=16,near=2.2,far=.6,lam_near=50,lam_far=14,shine=.05); put(i,fr,soft(sea,1.2),'ls',5)
elif i==3:   # surf washes around João's legs
    w=cv2.erode(R['agua'].astype(np.uint8),np.ones((3,3),np.uint8))
    fr=F.ripple(B,w.astype(np.float32),n=16,near=2.4,far=.7,lam_near=50,lam_far=14,shine=.05); put(i,fr,soft(w,1.2),'ls',5)
elif i in (4,5,6):   # the sea behind the scene
    keys={4:['remar','prancha','cao ladrava','gaivotas','areia'],5:['levantou','gritou','palmas'],6:['rita','poncha','limao','balcao','bar']}[i]
    ppl=people(R,keys)
    if i==4: sea=seamask(330,450,100,W)&(1-ppl)&(1-poly((180,80),(390,80),(390,620),(180,620)))
    elif i==5: sea=cv2.erode(R['mar'].astype(np.uint8),np.ones((3,3),np.uint8))&(1-ppl)
    else: sea=seamask(200,560,380,W)&(1-ppl)&(1-people(R,['joao']) if 'joao' in R else 1)
    if i==6:
        jo=np.zeros((H,W),np.uint8); cv2.rectangle(jo,(880,50),(1300,898),1,-1); dg=np.zeros((H,W),np.uint8); cv2.rectangle(dg,(1270,540),(1600,820),1,-1)
        an=np.zeros((H,W),np.uint8); cv2.rectangle(an,(600,100),(900,680),1,-1); sea&=(1-jo)&(1-dg)&(1-an)
    fr=F.ripple(B,sea.astype(np.float32),n=16,near=2.4 if i==5 else 2.0,far=.6,lam_near=50,lam_far=14,shine=.05); put(i,fr,soft(sea,1.2),'ls',5)
elif i==7:   # the car rides an uneven road: the whole view through the glass bumps and settles a few px, no blur
    d=np.load(S+'gen/b7p8_win.npz'); w=np.load(S+'gen/b7p8_ws.npz')
    fill=lambda m: cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_CLOSE,np.ones((15,15),np.uint8))
    ws=poly((245,78),(1372,72),(1432,300),(1438,358),(205,358),(212,200))
    glass=ws|fill(d['L1'])|fill(d['L2'])|poly((1405,180),(1462,180),(1468,420),(1410,420))|poly((1488,180),(1555,180),(1555,450),(1490,450))
    ppl=cv2.dilate(np.load(S+'gen/b7p8_ppl.npy').astype(np.uint8),np.ones((7,7),np.uint8))
    belt=np.zeros((H,W),np.uint8); cv2.line(belt,(1590,288),(1452,458),1,40)
    mir=cv2.dilate(w['MIR'].astype(np.uint8),np.ones((7,7),np.uint8))
    glass=cv2.erode(glass,np.ones((3,3),np.uint8))&(1-ppl)&(1-belt)&(1-mir)
    # plate: fill a band outside the glass from the glass itself, so shifting never pulls in frame pixels
    band=cv2.dilate(glass,np.ones((17,17),np.uint8))&(1-glass)
    plate=cv2.inpaint(np.clip(B,0,255).astype(np.uint8),band,7,cv2.INPAINT_TELEA).astype(np.float32)
    n=40; T=4.0; out=[]
    def bump(t,t0,a,f=7.,dmp=6.):
        u=t-t0
        return 0 if u<0 else a*np.exp(-dmp*u)*np.sin(2*np.pi*f*u+np.pi/2)
    for k in range(n):
        t=k/n*T
        dy=sum(bump(t+o,t0,a) for o in (0,T) for t0,a in ((0.55,2.6),(2.35,1.6),(3.3,0.9)))+.35*np.sin(2*np.pi*t*3/T)
        rot=np.deg2rad(.06*np.sin(2*np.pi*t/T)+.05*sum(bump(t+o,0.55,1.)*1 for o in (0,T)))
        cx,cy=800,300; c,sn=np.cos(rot),np.sin(rot)
        mx=cx+(GX-cx)*c-(GY-cy)*sn; my=cy+(GX-cx)*sn+(GY-cy)*c-dy
        fr=cv2.remap(plate,mx.astype(np.float32),my.astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
        out.append(fr)
    gm=np.clip(cv2.GaussianBlur(glass.astype(np.float32),(0,0),.8),0,1)
    put(i,out,gm,'lb',T)
