"""Book 6 page 2 (b6p2v4, same car as page 3): tunnel. Outside view bumps with the road, tunnel lights pulse toward the car,
side windows pass (sharp front, blurred back, 70%). usage: b6p2bump.py [preview]"""
import sys, glob, os, pickle, numpy as np, cv2
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'; sys.path.insert(0,S)
import frames as F, windfx, vehbump
W,H=1600,898
B=F.load('b6p2v4.jpg')
def poly(*p):
    m=np.zeros((H,W),np.uint8); cv2.fillPoly(m,[np.array(p,np.int32)],1); return m
f=sorted(glob.glob(S+'gen/hlcache/pico_1_*.pkl'),key=os.path.getmtime)[-1]; R={k:m for k,m in pickle.load(open(f,'rb'))[1]}
import hlmask; Pp=hlmask.predictor(); Pp.set_image(np.clip(B,0,255).astype(np.uint8))
def sm(box,pos,neg=()):
    pts=list(pos)+list(neg); lab=[1]*len(pos)+[0]*len(neg)
    ms,sc,_=Pp.predict(point_coords=np.array(pts,float),point_labels=np.array(lab),box=np.array(box,float),multimask_output=True)
    return ms[int(np.argmax([x.sum() for x in ms]))].astype(np.uint8)
hl=sm([75,460,350,640],[(210,520),(120,530),(300,530)],[(250,660)]); hr=sm([1290,460,1600,640],[(1450,520),(1350,530),(1550,530)],[(1450,660)])
rita=sm([1080,160,1450,898],[(1170,330),(1125,320),(1250,250),(1280,450)],[(1000,450)])
PPL=cv2.dilate((R['ana']|rita|hl|hr).astype(np.uint8),np.ones((9,9),np.uint8))
def line(p,q,w):
    m=np.zeros((H,W),np.uint8); cv2.line(m,p,q,1,w); return m
BELTS=line((8,312),(182,458),40)|line((1592,292),(1432,462),40)
dk=(F.lum(B)<90).astype(np.uint8)
def clean(m):
    g=(m&(1-BELTS)&(1-PPL)&(1-cv2.dilate(dk,np.ones((3,3),np.uint8)))).astype(np.uint8)
    return cv2.erode(cv2.morphologyEx(g,cv2.MORPH_OPEN,np.ones((5,5),np.uint8)),np.ones((3,3),np.uint8))
SL=clean(poly((0,62),(88,80),(116,100),(130,140),(124,220),(116,320),(106,420),(98,465),(0,480)))|clean(poly((152,178),(168,196),(188,262),(198,330),(202,445),(164,470),(150,330)))
SRp=clean(poly((1408,248),(1440,188),(1452,250),(1458,350),(1462,455),(1410,462)))|clean(poly((1476,165),(1490,122),(1508,112),(1528,140),(1545,240),(1556,350),(1558,455),(1474,458)))
MIR=poly((715,90),(905,90),(910,165),(712,165))
WSC=(poly((230,75),(1380,75),(1386,390),(224,390))&(1-MIR)&(1-PPL)).astype(np.uint8)
GLASS=(SL|SRp|WSC).astype(np.uint8)
L=F.lum(B); bright=((L>185)&(R['luzes']>0)).astype(np.uint8); n,lb,st,cen=cv2.connectedComponentsWithStats(bright)
pts=[tuple(cen[k]) for k in range(1,n) if st[k,4]>3]; vp=(920,258)
dd=np.array([np.hypot(p[0]-vp[0],p[1]-vp[1]) for p in pts]); ph=-(dd/max(dd.max(),1))
def outside(img,t):
    g=np.zeros((H,W),np.float32)
    for (x,y),p,dv in zip(pts,ph,dd):
        cv2.circle(g,(int(x),int(y)),int(3+dv/80),float(.55*.5*(1-np.cos(2*np.pi*(t*3/1.6+p*3)))),-1)
    return img*(1+cv2.GaussianBlur(g,(0,0),3)[...,None])
N,T=48,4.8
fr=vehbump.build(B,GLASS,[(SL,-1,212,0),(SRp,1,1425,1600)],outside=outside,N=N,T=T)
alpha=np.clip(cv2.GaussianBlur(GLASS.astype(np.float32),(0,0),.8),0,1)
if len(sys.argv)>1:
    import imageio.v2 as iio
    from PIL import Image
    big=[np.clip(f*alpha[...,None]+B*(1-alpha[...,None]),0,255).astype(np.uint8) for f in fr]
    iio.mimsave(S+'b6/p2_preview.mp4',[np.asarray(Image.fromarray(b).resize((1200,674))) for b in big]*2,fps=N/T,quality=8,macro_block_size=2)
    o=B*.3; o[GLASS>0]=B[GLASS>0]; Image.fromarray(np.clip(o,0,255).astype(np.uint8)).resize((960,539)).save(S+'conv/b6p2glass.jpg',quality=85)
    sys.exit()
for st_ in ('b6p2_lsl','b6p2_lsr','b6p2_ll','b6p2_lb'): windfx.add_layer('pico:1','',st_)
pa,box=F.save(fr,alpha,'b6p2','lb'); windfx.add_layer('pico:1',F.loop(pa,box,T),'b6p2_lb'); print('lb',len(pa),box)
