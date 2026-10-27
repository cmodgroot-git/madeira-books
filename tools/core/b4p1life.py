"""Book 4 page 1 (b4p1v2): the sea ripples and breaks gently; the waterfall falls behind the car (no spray: its foot is hidden)."""
import sys, glob, os, pickle, numpy as np, cv2
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'; sys.path.insert(0,S)
import frames as F, windfx
W,H=1600,898
B=F.load('b4p1v3.jpg')
f=sorted(glob.glob(S+'gen/hlcache/jantar_0_*.pkl'),key=os.path.getmtime)[-1]; R={k:m for k,m in pickle.load(open(f,'rb'))[1]}
car=cv2.dilate(R['carro'].astype(np.uint8),np.ones((9,9),np.uint8))
def poly(*p):
    m=np.zeros((H,W),np.uint8); cv2.fillPoly(m,[np.array(p,np.int32)],1); return m
# sea: its cut-out minus the rocks
sea=R['mar'].astype(np.uint8)&(F.lum(B)>70).astype(np.uint8)
sea=cv2.morphologyEx(sea,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
frs=F.ripple(B,sea,n=24,near=2.6,far=.4,lam_near=60.,lam_far=12.,shine=.05,edge=6)
ms=np.clip(cv2.GaussianBlur(sea.astype(np.float32),(0,0),1.2),0,1)
# waterfall: bright, low-saturation pixels in its column, above the car
hsv=cv2.cvtColor(np.clip(B,0,255).astype(np.uint8),cv2.COLOR_RGB2HSV)
col=poly((1105,0),(1215,0),(1215,460),(1110,460))
m=((hsv[...,2]>150)&(hsv[...,1]<70)&(col>0)&(car==0)).astype(np.uint8)
m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((9,5),np.uint8)); m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
n,lb,st,_=cv2.connectedComponentsWithStats(m); m=np.isin(lb,[i for i in range(1,n) if st[i,4]>400]).astype(np.uint8)
ys,xs=np.nonzero(m); y0,y1=ys.min(),ys.max(); P=240; U=48
tex=cv2.GaussianBlur(np.concatenate([np.random.default_rng(11).random((P,U)).astype(np.float32)]*3,0),(0,0),sigmaX=1.1,sigmaY=9)[P:2*P]; tex=(tex-tex.mean())/tex.std()
span={y:(np.nonzero(m[y])[0].min(),np.nonzero(m[y])[0].max()+1) for y in range(y0,y1+1) if m[y].any()}
cl=np.percentile(B[m>0],85,axis=0); sm=np.clip(cv2.GaussianBlur(m.astype(np.float32),(0,0),1.3),0,1)*(1-car)
frw=[]
for k in range(24):
    a=np.zeros((H,W),np.float32)
    for y,(xa,xb) in span.items():
        t=(y-y0)/max(1,y1-y0); v=(y-y0)*(1+.8*t)-k*P/24*(1+.6*t)
        a[y,xa:xb]=np.interp(np.linspace(0,U-1,xb-xa),np.arange(U),tex[int(np.floor(v))%P])
    a=np.clip(a*.5+.15,-.6,1.2)*sm; lt=np.clip(a,0,None)[...,None]*.55; dk=np.clip(-a,0,None)[...,None]*.18
    frw.append((B*(1-lt)+cl*lt)*(1-dk))
if len(sys.argv)>1:
    from PIL import Image
    o=B*.35; o[(m|sea)>0]=B[(m|sea)>0]; Image.fromarray(np.clip(o,0,255).astype(np.uint8)).resize((1200,674)).save(S+'car2/b4p1mask.jpg',quality=85); sys.exit()
pa,box=F.save(frs,ms,'b4p1','ls'); windfx.add_layer('jantar:0',F.loop(pa,box,6.0),'b4p1_ls')
pa,box=F.save(frw,sm,'b4p1','lf'); windfx.add_layer('jantar:0',F.loop(pa,box,1.5),'b4p1_lf'); print('ok')
