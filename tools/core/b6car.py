"""Book 6 pages 2 and 3 (b6p2v5, b6p3v4: same car, view from the middle of the back seat).
Outside view rides the road; side windows pass (sharp front, blurred back, 70%); p2 tunnel lights pulse toward the car;
p3 wipers sweep. usage: b6car.py 2|3 [check|preview]"""
import sys, glob, os, pickle, math, numpy as np, cv2
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'; sys.path.insert(0,S)
import frames as F, windfx, vehbump
W,H=1600,898; GX,GY=F.GX,F.GY
pg=int(sys.argv[1]); mode=sys.argv[2] if len(sys.argv)>2 else ''
name={2:'b6p2v6.jpg',3:'b6p3v5.jpg'}[pg]; key={2:'pico:1',3:'pico:2'}[pg]; stem={2:'b6p2',3:'b6p3'}[pg]
B=F.load(name)
def poly(*p):
    m=np.zeros((H,W),np.uint8); cv2.fillPoly(m,[np.array(p,np.int32)],1); return m
def line(p,q,w):
    m=np.zeros((H,W),np.uint8); cv2.line(m,p,q,1,w); return m
cache=S+f'gen/{stem}v_ppl.npz'
if os.path.exists(cache): PPL=np.load(cache)['P']
else:
    import hlmask; Pp=hlmask.predictor(); Pp.set_image(np.clip(B,0,255).astype(np.uint8))
    def sm(box,pos,neg=()):
        pts=list(pos)+list(neg); lab=[1]*len(pos)+[0]*len(neg)
        ms,sc,_=Pp.predict(point_coords=np.array(pts,float),point_labels=np.array(lab),box=np.array(box,float),multimask_output=True)
        return ms[int(np.argmax([x.sum() for x in ms]))].astype(np.uint8)
    if pg==2:
        ppl=[sm([205,140,735,700],[(420,200),(330,470),(620,560)]),sm([1000,140,1415,850],[(1150,210),(1000,560),(1320,470)]),
             sm([220,260,475,512],[(340,350)]),sm([1112,260,1385,512],[(1240,350)])]
    else:
        ppl=[sm([230,95,770,690],[(450,150),(330,480),(700,560)]),sm([840,100,1440,850],[(1130,170),(950,600),(1300,560)]),
             sm([280,325,530,545],[(400,400)]),sm([1095,325,1320,545],[(1200,400)])]
    PPL=np.zeros((H,W),np.uint8)
    for m in ppl: PPL|=m
    np.savez_compressed(cache,P=PPL)
if pg==2: cv2.ellipse(PPL,(1170,215),(118,92),0,0,360,1,-1); cv2.ellipse(PPL,(430,230),(110,95),0,0,360,1,-1)
else: cv2.ellipse(PPL,(1120,200),(110,100),0,0,360,1,-1); cv2.ellipse(PPL,(455,215),(125,105),0,0,360,1,-1)
PPL=cv2.dilate(PPL,np.ones((9,9),np.uint8))
hsv=cv2.cvtColor(np.clip(B,0,255).astype(np.uint8),cv2.COLOR_RGB2HSV); s_,v_=hsv[...,1].astype(int),hsv[...,2].astype(int)
if pg==2:
    BELTS=line((140,272),(232,425),40)|line((1468,282),(1378,430),40)
    MIR=poly((700,108),(900,108),(900,182),(700,182))|line((800,80),(800,115),20)
    SMIR=poly((150,355),(225,345),(235,440),(155,440))|poly((1375,350),(1450,355),(1445,440),(1370,440))
    PL=[poly((0,25),(80,35),(100,90),(95,485),(0,495)), poly((152,92),(298,60),(332,105),(318,250),(255,310),(212,440),(160,462))]
    PR=[poly((1520,35),(1600,25),(1600,495),(1528,485)), poly((1288,92),(1442,60),(1470,250),(1462,462),(1405,462),(1388,300),(1300,250))]
    WSC=poly((352,100),(1240,100),(1255,362),(335,362)); keep=(v_>95)
    fl,bl,fr_,br=330,0,1270,1600
else:
    BELTS=line((140,262),(240,440),40)|line((1462,262),(1372,445),40)
    MIR=poly((715,105),(885,105),(885,172),(715,172))|line((800,55),(800,110),22)
    SMIR=poly((185,375),(262,372),(262,455),(190,455))|poly((1310,372),(1390,372),(1385,455),(1310,455))
    PL=[poly((0,40),(80,50),(105,100),(100,570),(0,580)), poly((160,95),(205,85),(300,150),(300,330),(250,450),(240,530),(150,540),(140,300))]
    PR=[poly((1515,40),(1600,30),(1600,600),(1520,580)), poly((1250,90),(1395,85),(1450,250),(1440,450),(1430,520),(1360,470),(1300,330))]
    WSC=poly((380,98),(1222,98),(1245,395),(355,395)); keep=(v_>105)&(s_<70)
    fl,bl,fr_,br=300,0,1250,1600
def glassonly(m):
    g=(m&keep&(1-BELTS)&(1-PPL)&(1-SMIR)).astype(np.uint8)
    g=cv2.morphologyEx(g,cv2.MORPH_OPEN,np.ones((5,5),np.uint8)); g=cv2.morphologyEx(g,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))&m&(1-PPL)&(1-BELTS)
    g=cv2.erode(g,np.ones((3,3),np.uint8))
    n,lb,st,_=cv2.connectedComponentsWithStats(g); return np.isin(lb,[i for i in range(1,n) if st[i,4]>300]).astype(np.uint8)
SL=glassonly(PL[0]|PL[1]); SR=glassonly(PR[0]|PR[1])
WS=(WSC&(1-MIR)&(1-PPL)).astype(np.uint8)
B2=B.copy(); car=None; outside=None; sweep=np.zeros((H,W),np.uint8)
if pg==2:
    f=sorted(glob.glob(S+'gen/hlcache/pico_1_*.pkl'),key=os.path.getmtime)[-1]; R={k:m for k,m in pickle.load(open(f,'rb'))[1]}
    L=F.lum(B); bright=((L>185)&(R['luzes']>0)).astype(np.uint8); n,lb,st,cen=cv2.connectedComponentsWithStats(bright)
    pts=[tuple(cen[k]) for k in range(1,n) if st[k,4]>3]; vp=(810,262)
    dd=np.array([np.hypot(p[0]-vp[0],p[1]-vp[1]) for p in pts]); ph=-(dd/max(dd.max(),1))
    def outside(img,t):
        g=np.zeros((H,W),np.float32)
        for (x,y),p,dv in zip(pts,ph,dd):
            cv2.circle(g,(int(x),int(y)),int(3+dv/80),float(.55*.5*(1-np.cos(2*np.pi*(t*3/1.6+p*3)))),-1)
        return img*(1+cv2.GaussianBlur(g,(0,0),3)[...,None])
else:
    band=poly((630,352),(1025,352),(1025,394),(630,394))
    old=((F.lum(B)<95)&(band>0)).astype(np.uint8); old=cv2.dilate(old,np.ones((7,7),np.uint8))&band&WS
    up=np.roll(B,32,axis=0); B2[old>0]=up[old>0]
    seam=cv2.dilate(old,np.ones((7,7),np.uint8))-cv2.erode(old,np.ones((3,3),np.uint8)); blr=cv2.GaussianBlur(B2,(0,0),2.5); B2[seam>0]=blr[seam>0]
    WS=(WS|old).astype(np.uint8)
    PIV=[((640,386),195,math.atan2(13,193)),((842,388),180,math.atan2(23,173))]; MAXA=math.radians(102); TW=2.4
    def theta(t,rest):
        u=(t/TW)%1
        e=(.5-.5*math.cos(math.pi*u/.32)) if u<.32 else (.5+.5*math.cos(math.pi*(u-.32)/.32)) if u<.64 else 0
        return rest+(MAXA-rest)*e
    ts=np.linspace(0,TW,721)[:-1]; cross=[]
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
GLASS=(WS|SL|SR).astype(np.uint8)
if mode=='check':
    from PIL import Image
    o=B*.3; o[GLASS>0]=B[GLASS>0]; o[(SL|SR)>0]=o[(SL|SR)>0]*.5+np.array([255,0,0])*.5
    Image.fromarray(np.clip(o,0,255).astype(np.uint8)).resize((1200,674)).save(S+f'car2/{stem}glass.jpg',quality=85); sys.exit()
N,T=48,4.8
fr=vehbump.build(B2,GLASS,[(SL,-1,fl,bl),(SR,1,fr_,br)],outside=outside,car=car,N=N,T=T)
alpha=np.clip(cv2.GaussianBlur(GLASS.astype(np.float32),(0,0),.8),0,1)
if pg==3: alpha=np.maximum(alpha,np.clip(cv2.GaussianBlur((sweep&cv2.dilate(WS,np.ones((3,3),np.uint8))).astype(np.float32),(0,0),1.),0,1))
if mode=='preview':
    import imageio.v2 as iio
    from PIL import Image
    big=[np.clip(f*alpha[...,None]+B*(1-alpha[...,None]),0,255).astype(np.uint8) for f in fr]
    iio.mimsave(S+f'car2/{stem}_preview.mp4',[np.asarray(Image.fromarray(b).resize((1200,674))) for b in big]*2,fps=N/T,quality=8,macro_block_size=2)
    sys.exit()
pa,box=F.save(fr,alpha,stem,'lb'); windfx.add_layer(key,F.loop(pa,box,T),stem+'_lb'); print('lb',len(pa),box)
