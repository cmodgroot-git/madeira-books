"""Falling rain overlays, stronger puddle splashes, livelier rainbow. usage: b5rain.py <page 0-7>"""
import sys, os, re, glob, pickle, numpy as np, cv2
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'; sys.path.insert(0,S)
import frames as F, windfx
from PIL import Image
W,H=1600,898; GX,GY=F.GX,F.GY
exec(open(S+'b5anim.py').read().split('i=int(sys.argv[1])')[0].split('import frames as F, windfx')[1])  # regions, soft, put, rain_rings
def streak_tile(T,count,length,width,slope,seed):
    rng=np.random.default_rng(seed); t=np.zeros((T*3,T*3),np.float32)
    for _ in range(count):
        x,y=rng.uniform(0,T,2); L=length*rng.uniform(.6,1.2); a=rng.uniform(.5,1)
        for ox in (0,T,2*T):
            for oy in (0,T,2*T):
                p0=(int(x+ox),int(y+oy)); p1=(int(x+ox+slope*L),int(y+oy+L))
                cv2.line(t,p0,p1,a,width,cv2.LINE_AA)
    return cv2.GaussianBlur(t[T:2*T,T:2*T],(0,0),.6)
def rain_layer(n,layers,keep):
    """RGBA rain: each layer scrolls an integer number of tiles per loop so it repeats seamlessly"""
    out=[]
    for k in range(n):
        A=np.zeros((H,W),np.float32)
        for T,count,length,width,slope,tiles_down,alpha,seed in layers:
            tile=streak_tile(T,count,length,width,slope,seed)
            dy=tiles_down*T*k/n; dx=slope*dy
            big=np.tile(tile,(H//T+2,W//T+2))
            ox=int(round(-dx))%T; oy=int(round(-dy))%T
            A=np.maximum(A,big[oy:oy+H,ox:ox+W]*alpha)
        out.append(A*keep)
    return out
i=int(sys.argv[1]); B=F.load(f'b5p{i+1}.jpg'); R=regions(i)
def people_keep(keys,grow=11):
    m=np.zeros((H,W),np.uint8)
    for k in keys: m|=R[k].astype(np.uint8)
    return 1-soft(cv2.dilate(m,np.ones((grow,grow),np.uint8)),3)
def save_rgba(frames_a,col,name,dur):
    base=f'b5p{i+1}'
    U=np.max(frames_a,0); ys,xs=np.nonzero(U>.01); x0,y0,x1,y1=xs.min(),ys.min(),xs.max()+1,ys.max()+1
    for f in os.listdir(F.I):
        if re.match(rf'{base}_{name}\d\d\.webp$',f): os.remove(F.I+f)
    w,h=int((x1-x0)*.75),int((y1-y0)*.75); pa=[]
    for k,a in enumerate(frames_a):
        rgb=np.zeros((y1-y0,x1-x0,3),np.uint8); rgb[:]=col
        p=f'{base}_{name}{k:02d}.webp'
        Image.fromarray(np.dstack([rgb,(np.clip(a[y0:y1,x0:x1],0,1)*255).astype(np.uint8)]),'RGBA').resize((w,h),Image.LANCZOS).save(F.I+p,quality=80,method=6); pa.append('img/'+p)
    windfx.add_layer(f'passeio:{i}',F.loop(pa,(int(x0),int(y0),int(x1-x0),int(y1-y0)),dur),f'{base}_{name}'); print(i,name,len(pa),flush=True)
LAY=[(180,20,31,1,.18,3,.23,11),(288,11,62,2,.22,5,.30,12)]   # far fine streaks, near longer ones (falls ~3-5 tiles per loop)
if i==1:
    keep=people_keep(['rita','guardachuva']); keep[GY>820]*=1   # rain in front of street, not on Rita/umbrella
    save_rgba(rain_layer(16,LAY,keep),(232,238,245),'lv',1.2)
    a=B; L=F.lum(a); pud=((L>135)&(a[...,2]>=a[...,0]-6)&(GY>560)&(GX>480)&(GX<1150)).astype(np.uint8)
    pud=cv2.morphologyEx(pud,cv2.MORPH_OPEN,np.ones((3,3),np.uint8)); pud&=~(R['rita']>0)
elif i==2:
    keep=people_keep(['cao molhado'],15)*(1-soft(cv2.dilate((F.lum(B)<0)|np.zeros((H,W),bool),np.ones((3,3))) ,1) if False else 1)
    ppl=sam_ppl=None
    save_rgba(rain_layer(16,LAY,people_keep(['cao molhado','paragem'],9)),(232,238,245),'lv',1.2)
    pud=R['pocas']
elif i==3:
    save_rgba(rain_layer(16,[(180,20,31,1,.45,3,.22,13),(288,11,62,2,.5,5,.29,14)],people_keep(['ana','porta','estacao'],9)),(232,238,245),'lv',1.2)
if i in (1,2):   # stronger splashes: brighter rings plus a little crown of light at each impact
    pud=cv2.erode(pud.astype(np.uint8),np.ones((5,5),np.uint8))
    rng=np.random.default_rng(3); ys,xs=np.nonzero(pud>0); n=24; drops=55 if i==1 else 95
    k=rng.choice(len(xs),drops,replace=False); pts=list(zip(xs[k],ys[k])); ph=rng.uniform(0,1,drops); Rm=30 if i==1 else 42
    fr=[]
    for f in range(n):
        dx=np.zeros((H,W),np.float32); dy=np.zeros((H,W),np.float32); lit=np.zeros((H,W),np.float32)
        for (x,y),p in zip(pts,ph):
            age=((f/n)+p)%1; r=Rm*age; a=3.2*(1-age)**1.4
            x0,x1,y0,y1=max(0,x-Rm-8),min(W,x+Rm+8),max(0,int(y-Rm*.42)-8),min(H,int(y+Rm*.42)+8)
            gx,gy=GX[y0:y1,x0:x1]-x,(GY[y0:y1,x0:x1]-y)/.42; rr=np.sqrt(gx*gx+gy*gy)+1e-3
            band=np.exp(-((rr-r)/6.)**2); s=a*band*np.sin(2*np.pi*(rr-r)/6.)
            dx[y0:y1,x0:x1]+=s*gx/rr; dy[y0:y1,x0:x1]+=s*gy/rr*.42
            lit[y0:y1,x0:x1]+=band*(1-age)**1.2*.45
            if age<.18: lit[y0:y1,x0:x1]+=np.exp(-(gx**2+(gy*.42)**2)/(2*3.5**2))*(1-age/.18)*1.2   # impact crown
        g=cv2.remap(B,GX+dx,GY+dy,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT)
        fr.append(np.clip(g+(255-g)*np.clip(lit,0,1)[...,None]*.8,0,255))
    put(i,fr,soft(cv2.dilate(pud,np.ones((7,7),np.uint8)),1.2),'lr',3)
if i==3:   # stormy sea: strong, quick ripples on the water right of the station
    a=B; hsv=cv2.cvtColor(np.clip(a,0,255).astype(np.uint8),cv2.COLOR_RGB2HSV)
    zone=np.zeros((H,W),np.uint8); cv2.fillPoly(zone,[np.array([(1110,560),(1600,560),(1600,720),(1110,740)],np.int32)],1)
    pal=cv2.dilate(R['vento'].astype(np.uint8),np.ones((15,15),np.uint8)); st=cv2.dilate(R['estacao'].astype(np.uint8),np.ones((9,9),np.uint8))
    sea=((zone>0)&((hsv[...,0]>70)&(hsv[...,0]<110)&(hsv[...,1]>25)|(F.lum(a)>175))&(pal==0)&(st==0)).astype(np.uint8)
    sea=cv2.morphologyEx(sea,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8)); sea=cv2.morphologyEx(sea,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    print('sea px',sea.sum())
    fr=F.ripple(B,sea.astype(np.float32),n=16,near=4.2,far=1.6,lam_near=55,lam_far=22,shine=.07); put(i,fr,soft(sea,1.2),'ls',3)
if i==5:
    windfx.add_layer('passeio:5','','b5p6_lb')
    for f in os.listdir(F.I):
        if re.match(r'b5p6_lb\d\d\.webp$',f): os.remove(F.I+f)
    sea=R['mar']; fr=F.ripple(B,sea.astype(np.float32),n=16,near=2.8,far=.8,lam_near=50,lam_far=16,shine=.05); put(i,fr,soft(sea,1.2),'ls',5)
