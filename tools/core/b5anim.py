"""Book 5 scene life. usage: b5anim.py <page 0-7>"""
import sys, glob, pickle, numpy as np, cv2
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'; sys.path.insert(0,S)
import frames as F, windfx
W,H=1600,898; GX,GY=F.GX,F.GY
def regions(i):
    f=sorted(glob.glob(S+f'gen/hlcache/passeio_{i}_*.pkl'),key=lambda p:__import__('os').path.getmtime(p))[-1]
    return {k:m for k,m in pickle.load(open(f,'rb'))[1]}
def soft(m,b=1.5): return np.clip(cv2.GaussianBlur(m.astype(np.float32),(0,0),b),0,1)
def put(i,fr,mask,name,dur):
    base=f'b5p{i+1}'; pa,box=F.save(fr,mask,base,name)
    windfx.add_layer(f'passeio:{i}',F.loop(pa,box,dur),f'{base}_{name}'); print(i,name,len(pa),box,flush=True)
def rain_rings(B,mask,n=24,drops=60,R=34,lam=7.,amp=2.2,squash=.42,seed=1):
    """raindrops landing in puddles: small outward rings that bend the painted water, each on its own phase"""
    rng=np.random.default_rng(seed); ys,xs=np.nonzero(mask>.5); k=rng.choice(len(xs),drops,replace=False)
    pts=list(zip(xs[k],ys[k])); ph=rng.uniform(0,1,drops); out=[]
    for i in range(n):
        dx=np.zeros((H,W),np.float32); dy=np.zeros((H,W),np.float32); lit=np.zeros((H,W),np.float32)
        for (x,y),p in zip(pts,ph):
            age=((i/n)+p)%1; r=R*age; a=amp*(1-age)**1.5
            x0,x1,y0,y1=max(0,x-R-8),min(W,x+R+8),max(0,int(y-R*squash)-8),min(H,int(y+R*squash)+8)
            gx,gy=GX[y0:y1,x0:x1]-x,(GY[y0:y1,x0:x1]-y)/squash; rr=np.sqrt(gx*gx+gy*gy)+1e-3
            band=np.exp(-((rr-r)/lam)**2); s=a*band*np.sin(2*np.pi*(rr-r)/lam)
            dx[y0:y1,x0:x1]+=s*gx/rr; dy[y0:y1,x0:x1]+=s*gy/rr*squash; lit[y0:y1,x0:x1]+=band*(1-age)*.09
        f=cv2.remap(B,GX+dx,GY+dy,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT)*(1+lit[...,None])
        out.append(np.clip(f,0,255))
    return out
i=int(sys.argv[1]); B=F.load(f'b5p{i+1}.jpg'); R=regions(i)
if i==0:   # clouds drift slowly across the grey sky (cable cars painted out of the scrolling plate)
    sky=R['ceu cinzento nuvens']; tel=cv2.dilate(R['teleferico'],np.ones((15,15),np.uint8))
    ys,xs=np.nonzero(sky); x0,x1,y0,y1=max(0,xs.min()-80),min(W,xs.max()+80),max(0,ys.min()-10),min(H,ys.max()+40)
    hole=((sky==0)|(tel>0)).astype(np.uint8); hole=cv2.dilate(hole,np.ones((7,7),np.uint8))
    plate=B.copy(); crop=cv2.inpaint(np.clip(B[y0:y1,x0:x1],0,255).astype(np.uint8),hole[y0:y1,x0:x1],15,cv2.INPAINT_TELEA)
    plate[y0:y1,x0:x1]=crop   # only sky pixels feed the drifting clouds
    fr=F.fall_scroll(plate,n=24,P=60.,direction=(1,0)); m=soft(cv2.erode(sky,np.ones((3,3),np.uint8)))
    put(i,fr,m,'lc',24)
elif i in (1,2):   # rain landing in the puddles
    if i==2: pud=R['pocas']
    else:
        a=B; L=F.lum(a); pud=((L>135)&(a[...,2]>=a[...,0]-6)&(GY>560)&(GX>480)&(GX<1150)).astype(np.uint8)
        pud=cv2.morphologyEx(pud,cv2.MORPH_OPEN,np.ones((3,3),np.uint8)); pud&=~(R['rita']>0)
    pud=cv2.erode(pud.astype(np.uint8),np.ones((5,5),np.uint8))
    fr=rain_rings(B,pud,drops=40 if i==1 else 70,R=26 if i==1 else 38)
    put(i,fr,soft(pud,1.2),'lr',3)
elif i==3:   # strong gusts in the palms
    w=soft(R['vento'],4)*np.clip((898-GY)/700,0,1)**.6
    fr=F.sway(B,w,n=16,amp=5.,lam=300.,gust=.55,vertical=.3)
    put(i,fr,np.clip(soft(R['vento']>0,2)*1.3,0,1),'lw',4)
elif i==4:   # rain running down the café window
    m=R['montra'].copy(); m[GY>560]=0; m=cv2.erode(m,np.ones((5,5),np.uint8))
    fr=F.fall_scroll(B,n=24,P=90.,direction=(0,1)); put(i,fr,soft(m,2),'lr',6)
elif i==5:   # the rainbow glows softly; the sea moves
    rb=soft(R['arcoiris'],6); g=F.lum(B)[...,None]
    fr=[np.clip(B+(B-g)*(.55*.5*(1-np.cos(2*np.pi*k/24)))*rb[...,None],0,255) for k in range(24)]   # colours deepen and fade, no brightening
    put(i,fr,np.clip(rb*1.4,0,1),'lb',12)
    sea=R['mar']; fr=F.ripple(B,sea.astype(np.float32),n=16,near=2.0,far=.5,lam_near=50,lam_far=14,shine=.04); put(i,fr,soft(sea,1.2),'ls',6)
elif i==7:   # a gentle breeze in the hydrangeas and trees
    hsv=cv2.cvtColor(np.clip(B,0,255).astype(np.uint8),cv2.COLOR_RGB2HSV)
    ppl=cv2.dilate((R['homens empurram']|R['carrodecesto']|R['rita']).astype(np.uint8),np.ones((25,25),np.uint8))
    area=np.zeros((H,W),np.uint8); cv2.fillPoly(area,[np.array([(0,0),(330,0),(330,560),(0,620)],np.int32)],1); cv2.fillPoly(area,[np.array([(1130,0),(1600,0),(1600,620),(1130,560)],np.int32)],1)
    leaf=((hsv[...,1]>40)&(area>0)&~(ppl>0)).astype(np.uint8)
    church=np.zeros((H,W),np.uint8); cv2.rectangle(church,(1080,0),(1330,260),1,-1); leaf[church>0]=0
    w=soft(cv2.morphologyEx(leaf,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8)),5); w[ppl>0]=0; w[cv2.dilate(church,np.ones((31,31),np.uint8))>0]=0
    fr=F.sway(B,w,n=16,amp=2.2,lam=320.); put(i,fr,np.clip(soft(w>.05,2)*1.2,0,1),'lf',6)
