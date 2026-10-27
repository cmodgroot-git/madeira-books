"""Book 6 page 3: foggy viaduct. Outside view bumps with the road, side windows pass (sharp front, blurred back, 70%),
wipers (on the car) sweep over it every 2.4 s. usage: b6p3bump.py [preview]"""
import sys, glob, os, pickle, math, numpy as np, cv2
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'; sys.path.insert(0,S)
import frames as F, windfx, vehbump
W,H=1600,898; GX,GY=F.GX,F.GY
B=F.load('b6p3v3.jpg')
f=sorted(glob.glob(S+'gen/hlcache/pico_2_*.pkl'),key=os.path.getmtime)[-1]; R={k:m for k,m in pickle.load(open(f,'rb'))[1]}
WS=R['chuva'].astype(np.uint8)
hsv=cv2.cvtColor(np.clip(B,0,255).astype(np.uint8),cv2.COLOR_RGB2HSV); h_,s_,v_=[hsv[...,i].astype(int) for i in range(3)]
tan=((h_<=18)&(s_>38)).astype(np.uint8)                                  # belts, pillars, trim
dark=(v_<70).astype(np.uint8)
SIDE=np.load(S+'gen/b6p3_side.npz'); rita=cv2.dilate(R['rita'].astype(np.uint8),np.ones((9,9),np.uint8))
def glassonly(m):
    g=(m>0).astype(np.uint8)&(1-tan)&(1-dark)&(1-rita)
    g=cv2.morphologyEx(g,cv2.MORPH_OPEN,np.ones((3,3),np.uint8)); g=cv2.morphologyEx(g,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))&(m>0)&(1-rita)
    n,lb,st,_=cv2.connectedComponentsWithStats(g); return np.isin(lb,[i for i in range(1,n) if st[i,4]>300]).astype(np.uint8)
SL,SR=glassonly(SIDE['L']),glassonly(SIDE['R'])
# old painted wipers -> filled from the glass just above them; drawn again on the car
old=cv2.dilate(np.load(S+'gen/b6p3_oldwipers.npy').astype(np.uint8),np.ones((11,11),np.uint8))&cv2.dilate(WS,np.ones((15,15),np.uint8))
up=np.roll(B,32,axis=0); B2=B.copy(); B2[old>0]=up[old>0]
seam=cv2.dilate(old,np.ones((7,7),np.uint8))-cv2.erode(old,np.ones((3,3),np.uint8)); bl=cv2.GaussianBlur(B2,(0,0),2.5); B2[seam>0]=bl[seam>0]
GLASS=(WS|old|SL|SR).astype(np.uint8)&(1-rita)
PIV=[((561,413),285,math.radians(3.4)),((930,416),168,math.radians(5.5))]; MAXA=math.radians(102); TW=2.4
def theta(t,rest):
    u=(t/TW)%1
    e=(.5-.5*math.cos(math.pi*u/.32)) if u<.32 else (.5+.5*math.cos(math.pi*(u-.32)/.32)) if u<.64 else 0
    return rest+(MAXA-rest)*e
ts=np.linspace(0,TW,721)[:-1]; cross=[]; sweep=np.zeros((H,W),np.uint8)
for (px,py),Lb,a0 in PIV:
    phi=np.arctan2(-(GY-py),GX-px); r=np.hypot(GX-px,GY-py)
    inside=(r>Lb*.16)&(r<Lb*1.03)&(phi>=a0-.02)&(phi<=MAXA+.02); sweep|=inside.astype(np.uint8)
    th=np.array([theta(t,a0) for t in ts]); iu=(ts/TW<.32); idn=(ts/TW>=.32)&(ts/TW<.64)
    cross.append((inside,np.interp(phi,th[iu],ts[iu]),np.interp(-phi,-th[idn],ts[idn])))
WSf=WS.astype(np.float32)
def car(img,t):
    dt=np.full((H,W),np.inf,np.float32)
    for inside,tup,tdn in cross:
        for tc in (tup,tdn): dt=np.where(inside,np.minimum(dt,(t-tc)%TW),dt)
    a=np.where(np.isfinite(dt),np.exp(-dt/1.1)*.85,0)*WSf
    clear=np.clip(img+.35*(img-cv2.GaussianBlur(img,(0,0),12)),0,255)*.97
    o=img*(1-a[...,None])+clear*a[...,None]
    blade=np.zeros((H,W),np.float32)
    for sft,wgt in ((-.4,.45),(0,1.),(.4,.45)):
        tt=t+sft*TW/36; layer=np.zeros((H*2,W*2),np.uint8)
        for (px,py),Lb,a0 in PIV:
            th=theta(tt,a0); c,sn=math.cos(th),-math.sin(th); qx,qy=-sn,c
            P=lambda r,off=0:(int(2*(px+c*r+qx*off)),int(2*(py+sn*r+qy*off)))
            cv2.line(layer,P(0),P(Lb*.97,-3),255,6,cv2.LINE_AA); cv2.line(layer,P(Lb*.18,-6),P(Lb,-6),255,11,cv2.LINE_AA); cv2.circle(layer,P(0),9,255,-1,cv2.LINE_AA)
        blade=np.maximum(blade,cv2.resize(layer,(W,H),interpolation=cv2.INTER_AREA).astype(np.float32)/255*wgt)
    blade*=WSf
    return o*(1-blade[...,None]*.92)+np.float32([30,29,32])*blade[...,None]*.92
N,T=48,4.8
fr=vehbump.build(B2,GLASS,[(SL,-1,215,0),(SR,1,1408,1562)],car=car,N=N,T=T)
alpha=np.clip(cv2.GaussianBlur(GLASS.astype(np.float32),(0,0),.8),0,1)
alpha=np.maximum(alpha,np.clip(cv2.GaussianBlur((sweep&cv2.dilate(WS,np.ones((3,3),np.uint8))).astype(np.float32),(0,0),1.),0,1))
if len(sys.argv)>1:
    import imageio.v2 as iio
    from PIL import Image
    big=[np.clip(f*alpha[...,None]+B*(1-alpha[...,None]),0,255).astype(np.uint8) for f in fr]
    iio.mimsave(S+'b6/p3_preview.mp4',[np.asarray(Image.fromarray(b).resize((1200,674))) for b in big]*2,fps=N/T,quality=8,macro_block_size=2)
    Image.fromarray(np.concatenate([big[k][40:520,0:260] for k in (0,12,24,36)]+[big[k][40:520,1380:1600] for k in (0,12,24,36)],1)).save(S+'conv/b6p3sides.jpg',quality=88)
    sys.exit()
for st in ('b6p3_lsl','b6p3_lsr','b6p3_lw'): windfx.add_layer('pico:2','',st)
pa,box=F.save(fr,alpha,'b6p3','lb'); windfx.add_layer('pico:2',F.loop(pa,box,T),'b6p3_lb'); print('lb',len(pa),box)
