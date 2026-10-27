"""Book 6 page 3: wipers sweeping (clearing the drizzle), scenery rushing past the side windows. usage: b6p3life.py [preview]"""
import sys, glob, os, pickle, math, numpy as np, cv2
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'; sys.path.insert(0,S)
import frames as F, windfx
W,H=1600,898; GX,GY=F.GX,F.GY
B=F.load('b6p3.jpg')
f=sorted(glob.glob(S+'gen/hlcache/pico_2_*.pkl'),key=os.path.getmtime)[-1]; R={k:m for k,m in pickle.load(open(f,'rb'))[1]}
SIDE=np.load(S+'gen/b6p3_side.npz'); SL,SR=SIDE['L'],SIDE['R']
WS=R['chuva'].astype(np.uint8)                        # windscreen glass, people and mirror cut out
L=F.lum(B)
def specks(m):                                        # painted raindrops: small bright dots on the glass
    loc=cv2.GaussianBlur(L,(0,0),4); d=((L-loc>14)&(m>0)).astype(np.uint8)
    n,lb,st,_=cv2.connectedComponentsWithStats(d); keep=[i for i in range(1,n) if 2<=st[i,4]<=60]
    return cv2.dilate(np.isin(lb,keep).astype(np.uint8),np.ones((3,3),np.uint8))
# ---------- side windows: scenery rushes backward ----------
def side(n=24,P=110,K=34):
    """every glass run of each side window shows its own outside view as a seamless band (no mirroring) scrolling backward,
    with a soft, mostly horizontal blur; the raindrops stay sharp on the glass"""
    out=[B.copy() for _ in range(n)]; mall=np.zeros((H,W),np.uint8)
    rita=cv2.dilate(R['rita'].astype(np.uint8),np.ones((9,9),np.uint8))
    for m,dirn in ((SL,-1),(SR&(1-rita),1)):
        loc=cv2.GaussianBlur(L,(0,0),4); d=((L-loc>22)&(m>0)).astype(np.uint8)
        nn,lb,st,_=cv2.connectedComponentsWithStats(d); drops=cv2.dilate(np.isin(lb,[k for k in range(1,nn) if 3<=st[k,4]<=40]).astype(np.uint8),np.ones((3,3),np.uint8))
        clean=cv2.inpaint(np.clip(B,0,255).astype(np.uint8),drops,5,cv2.INPAINT_TELEA).astype(np.float32)
        dl=np.where(drops[...,None]>0,B-clean,0)
        me=cv2.erode(m.astype(np.uint8),np.ones((5,5),np.uint8))
        rows=[]
        for y in range(H):
            xs_=np.nonzero(me[y])[0]
            if len(xs_)<10: continue
            for rr in np.split(xs_,np.nonzero(np.diff(xs_)>1)[0]+1):
                if len(rr)<10: continue
                xa,xb=rr[0],rr[-1]+1
                seg=cv2.resize(clean[y:y+1,xa:xb],(P+K,1),interpolation=cv2.INTER_LINEAR)[0]
                w=np.linspace(0,1,K)[:,None]; tile=seg[:P].copy(); tile[:K]=seg[P:P+K]*(1-w)+seg[:K]*w   # seamless wrap
                rows.append((y,xa,xb,tile))
        box=np.nonzero(me); y0,y1,x0,x1=max(0,box[0].min()-8),min(H,box[0].max()+9),max(0,box[1].min()-8),min(W,box[1].max()+9)
        mm=me[y0:y1,x0:x1].astype(np.float32)
        for k in range(n):
            layer=np.zeros((y1-y0,x1-x0,3),np.float32)
            for y,xa,xb,tile in rows:
                acc=0; xs=np.arange(xa,xb)
                for sft in np.linspace(-.5,.5,5):
                    off=(k+sft)*P/n*dirn
                    acc=acc+tile[np.mod(np.round((xs-xa)*P/(xb-xa)-off).astype(int),P)]
                layer[y-y0,xa-x0:xb-x0]=acc/5
            # soft, diffuse blur that stays inside the glass
            num=cv2.GaussianBlur(layer*mm[...,None],(0,0),sigmaX=11,sigmaY=3); den=cv2.GaussianBlur(mm,(0,0),sigmaX=11,sigmaY=3)[...,None]
            bl=num/np.maximum(den,1e-3)
            fr=out[k]; sub=fr[y0:y1,x0:x1]
            sub[:]=np.where(mm[...,None]>0,bl,sub)
            fr[me>0]+=dl[me>0]
        mall|=me
    mask=np.clip(cv2.GaussianBlur(mall.astype(np.float32),(0,0),1.),0,1)
    return out,mask
# ---------- wipers ----------
PIV=[((561,413),285,math.radians(3.4)),((930,416),168,math.radians(5.5))]
MAXA=math.radians(102); T=2.4
def theta(t,rest):                                    # up 0-.32, down .32-.64, rest after; eased
    u=(t/T)%1
    if u<.32: e=.5-.5*math.cos(math.pi*u/.32)
    elif u<.64: e=.5+.5*math.cos(math.pi*(u-.32)/.32)
    else: e=0
    return rest+(MAXA-rest)*e
def wipers(n=36):
    old=cv2.dilate(np.load(S+'gen/b6p3_oldwipers.npy').astype(np.uint8),np.ones((11,11),np.uint8))&cv2.dilate(WS,np.ones((15,15),np.uint8))
    # fill the old wipers with the glass just above them (same road and haze), then soften the seam
    up=np.roll(B,32,axis=0); base=B.copy(); base[old>0]=up[old>0]
    seam=cv2.dilate(old,np.ones((7,7),np.uint8))-cv2.erode(old,np.ones((3,3),np.uint8))
    bl=cv2.GaussianBlur(base,(0,0),2.5); base[seam>0]=bl[seam>0]
    drops=specks(WS); clear=cv2.inpaint(np.clip(base,0,255).astype(np.uint8),drops,4,cv2.INPAINT_TELEA).astype(np.float32)
    clear=np.clip(clear+.35*(clear-cv2.GaussianBlur(clear,(0,0),12)),0,255)*.97     # the swept glass reads a little crisper
    # time since the blade last crossed each pixel
    ts=np.linspace(0,T,721)[:-1]; last=np.full((H,W),np.inf,np.float32); sweep=np.zeros((H,W),np.uint8)
    lastt=[None,None]
    cross=[]
    for wi,((px,py),Lb,a0) in enumerate(PIV):
        phi=np.arctan2(-(GY-py),GX-px); r=np.hypot(GX-px,GY-py)
        inside=(r>Lb*.16)&(r<Lb*1.03)&(phi>=a0-.02)&(phi<=MAXA+.02); sweep|=inside.astype(np.uint8)
        th=np.array([theta(t,a0) for t in ts])
        up=ts[:len(ts)]; # crossing times: up and down halves
        iu=(ts/T<.32); idn=(ts/T>=.32)&(ts/T<.64)
        tup=np.interp(phi,th[iu],ts[iu]); tdn=np.interp(-phi,-th[idn],ts[idn])
        cross.append((inside,tup,tdn))
    out=[]
    for k in range(n):
        t=k*T/n; o=base.copy()
        dt=np.full((H,W),np.inf,np.float32)
        for inside,tup,tdn in cross:
            for tc in (tup,tdn):
                d=(t-tc)%T; dt=np.where(inside,np.minimum(dt,d),dt)
        a=np.where(np.isfinite(dt),np.exp(-dt/1.1)*.85,0)*WS
        o=o*(1-a[...,None])+clear*a[...,None]
        blade=np.zeros((H,W),np.float32)
        for s,wgt in ((-.4,.45),(0,1.),(.4,.45)):
            tt=t+s*T/n; layer=np.zeros((H*2,W*2),np.uint8)
            for (px,py),Lb,a0 in PIV:
                th=theta(tt,a0); c,sn=math.cos(th),-math.sin(th); qx,qy=-sn,c
                P=lambda r,off=0:(int(2*(px+c*r+qx*off)),int(2*(py+sn*r+qy*off)))
                cv2.line(layer,P(0),P(Lb*.97,-3),255,6,cv2.LINE_AA)                 # arm
                cv2.line(layer,P(Lb*.18,-6),P(Lb,-6),255,11,cv2.LINE_AA)            # rubber blade
                cv2.circle(layer,P(0),9,255,-1,cv2.LINE_AA)
            l=cv2.resize(layer,(W,H),interpolation=cv2.INTER_AREA).astype(np.float32)/255
            blade=np.maximum(blade,l*wgt)
        blade*=WS
        o=o*(1-blade[...,None]*.92)+np.float32([30,29,32])*blade[...,None]*.92
        out.append(o)
    mask=np.clip(cv2.GaussianBlur(((sweep|old)&cv2.dilate(WS,np.ones((3,3),np.uint8))).astype(np.float32),(0,0),1.),0,1)
    return out,mask
def put(fr,mask,name,dur):
    pa,box=F.save(fr,mask,'b6p3',name); windfx.add_layer('pico:2',F.loop(pa,box,dur),f'b6p3_{name}'); print(name,len(pa),box,flush=True)
if __name__=='__main__':
    sf,sm=side(); wf,wm=wipers()
    if len(sys.argv)>1:
        from PIL import Image
        strip=[]
        for k in range(0,36,4):
            c=wf[k]*wm[...,None]+B*(1-wm[...,None]); sk=k*24//36; c=sf[sk]*sm[...,None]+c*(1-sm[...,None])
            strip.append(Image.fromarray(np.clip(c[40:480],0,255).astype(np.uint8)).resize((800,220)))
        Sh=Image.new('RGB',(1600,220*5))
        for i,s in enumerate(strip): Sh.paste(s,((i%2)*800,(i//2)*220))
        Sh.save(S+'conv/p3life_strip.jpg',quality=85); sys.exit()
    windfx.add_layer('pico:2','','b6p3_lf')
    windfx.add_layer('pico:2','','b6p3_ls')
    ml=sm.copy(); ml[:,800:]=0; mr=sm.copy(); mr[:,:800]=0
    put(sf,ml,'lsl',1.2); put(sf,mr,'lsr',1.2); put(wf,wm,'lw',T)
