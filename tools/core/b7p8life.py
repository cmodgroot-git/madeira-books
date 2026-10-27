"""Book 7 page 8: the car rides an uneven road (whole outside view bumps a few px); scenery passes the side windows,
sharp at each window's front edge and increasingly blurred toward its back edge. usage: b7p8life.py [preview]"""
import sys, os, numpy as np, cv2
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'; sys.path.insert(0,S)
import frames as F, windfx
W,H=1600,898; GX,GY=F.GX,F.GY
B=F.load('b7p8.jpg')
def poly(*p):
    m=np.zeros((H,W),np.uint8); cv2.fillPoly(m,[np.array(p,np.int32)],1); return m
def line(p,q,w):
    m=np.zeros((H,W),np.uint8); cv2.line(m,p,q,1,w); return m
# people and seats in front of the glass
if os.path.exists(S+'gen/b7p8k_ppl.npz'):
    d=np.load(S+'gen/b7p8k_ppl.npz'); PPL=d['P']
else:
    import hlmask; P=hlmask.predictor(); P.set_image(np.clip(B,0,255).astype(np.uint8))
    def sm(box,pos,neg=()):
        pts=list(pos)+list(neg); lab=[1]*len(pos)+[0]*len(neg)
        ms,sc,_=P.predict(point_coords=np.array(pts,float),point_labels=np.array(lab),box=np.array(box,float),multimask_output=True)
        return ms[int(np.argmax([x.sum() for x in ms]))].astype(np.uint8)
    rita=sm([150,140,720,898],[(300,250),(250,400),(450,600)],[(100,300)])
    ana=sm([890,150,1460,898],[(1160,280),(1150,450),(1300,300),(1250,220)],[(1500,300)])
    hr1=sm([150,410,440,620],[(290,470),(200,520)],[(290,380)]); hr2=sm([1240,400,1560,640],[(1400,470),(1300,520),(1500,520)],[(1400,380)])
    PPL=(rita|ana|hr1|hr2).astype(np.uint8); np.savez_compressed(S+'gen/b7p8k_ppl.npz',P=PPL)
ppl=cv2.dilate(PPL,np.ones((5,5),np.uint8))
BELTL=line((12,275),(198,425),38); BELTR=line((1590,282),(1440,425),38)
L1=poly((62,135),(85,95),(115,82),(140,92),(150,135),(140,250),(128,380),(118,470),(40,480),(38,420),(45,300),(55,190))
L2=poly((152,140),(160,124),(186,190),(210,280),(222,330),(212,390),(200,480),(124,480),(131,380),(142,250))
R1=poly((1425,190),(1442,150),(1452,230),(1462,330),(1468,410),(1400,410),(1405,300),(1415,240))
R2=poly((1472,140),(1485,103),(1505,97),(1520,110),(1535,200),(1550,320),(1560,420),(1560,490),(1500,490),(1480,420),(1474,300),(1468,200))
WSC=poly((245,78),(1372,72),(1432,300),(1438,358),(205,358),(212,200))
MIR=poly((720,85),(890,85),(895,150),(720,150))|line((805,60),(805,95),14)
clean=lambda m: (cv2.erode(m,np.ones((3,3),np.uint8))&(1-ppl)&(1-BELTL)&(1-BELTR)&(1-MIR)).astype(np.uint8)
r_,g_,b_=B[...,0],B[...,1],B[...,2]; Lum=F.lum(B); sat=B.max(2)-B.min(2)
_hsv=cv2.cvtColor(np.clip(B,0,255).astype(np.uint8),cv2.COLOR_RGB2HSV); _h,_s,_v=_hsv[...,0].astype(int),_hsv[...,1].astype(int),_hsv[...,2].astype(int)
GL_L=(((_h>=16)&(_h<=60)&(_s>35)&(_v>80))|((_v>105)&(_s<48)&((_h>=40)|(_h<=1)))).astype(np.uint8)   # yellow-green plants, grey road and its white line
GL_R=((b_>=g_-2)&(Lum>85)).astype(np.uint8)                              # pink-purple sky and sea
def glassonly(m,c):
    g=cv2.morphologyEx((m&c).astype(np.uint8),cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    g=cv2.morphologyEx(g,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))&m
    g=cv2.morphologyEx(g,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))&m
    n,lb,st,_=cv2.connectedComponentsWithStats(g); return np.isin(lb,[i for i in range(1,n) if st[i,4]>300]).astype(np.uint8)
L1,L2,R1,R2,WSC=[clean(m) for m in (L1,L2,R1,R2,WSC)]
L1,L2=glassonly(L1,GL_L),glassonly(L2,GL_L); R1,R2=glassonly(R1,GL_R),glassonly(R2,GL_R)
LINE=(((_v>150)&(_s<45))&((L1|L2)>0)&(GY>330)).astype(np.uint8)              # the white road-edge line: continuous along travel, so it stays crisp
LINE=cv2.morphologyEx(LINE,cv2.MORPH_OPEN,np.ones((2,2),np.uint8)); n_,lb_,st_,_=cv2.connectedComponentsWithStats(LINE)
LINE=cv2.dilate(np.isin(lb_,[i for i in range(1,n_) if st_[i,2]>25]).astype(np.uint8),np.ones((5,5),np.uint8))
# fit a straight band to the painted line in each pane and keep it as a soft, anti-aliased static stroke
LINEA=np.zeros((H,W),np.float32)
for pane in ((L1|L2),):
    ys_,xs_=np.nonzero(LINE&L1)
    if len(xs_)<30: continue
    A_=np.vstack([xs_,np.ones_like(xs_)]).T; k_,c_=np.linalg.lstsq(A_,ys_,rcond=None)[0]
    res=ys_-(k_*xs_+c_); half=max(3.,np.percentile(np.abs(res),90))
    big=np.zeros((H*4,W*4),np.uint8); x0_,x1_=xs_.min()-30,240
    cv2.line(big,(int(x0_*4),int((k_*x0_+c_)*4)),(int(x1_*4),int((k_*x1_+c_)*4)),255,int(half*2*4),cv2.LINE_AA)
    band_=cv2.resize(big,(W,H),interpolation=cv2.INTER_AREA).astype(np.float32)/255
    LINEA=np.maximum(LINEA,band_*pane)
LINEA=cv2.GaussianBlur(LINEA,(0,0),.7)
SIDE_L=L1|L2; SIDE_R=R1|R2; GLASS=WSC|SIDE_L|SIDE_R
# plate: extend the glass content outward so bumps never pull in frame pixels
band=cv2.dilate(GLASS,np.ones((21,21),np.uint8))&(1-GLASS)
PLATE=cv2.inpaint(np.clip(B,0,255).astype(np.uint8),band,9,cv2.INPAINT_TELEA).astype(np.float32)
OPA=float(os.environ.get('OPA','0.7'))
N=40; T=4.0
def bump(t,t0,a,f=7.,dmp=6.):
    u=t-t0
    return 0. if u<0 else a*np.exp(-dmp*u)*np.sin(2*np.pi*f*u+np.pi/2)
def jolt(t):
    dy=sum(bump(t+o,t0,a) for o in (0,T) for t0,a in ((0.55,2.6),(2.35,1.6),(3.3,0.9)))+.35*np.sin(2*np.pi*t*3/T)
    rot=np.deg2rad(.06*np.sin(2*np.pi*t/T)+.05*sum(bump(t+o,0.55,1.) for o in (0,T)))
    return dy,rot
SIG=[0,2,4,7,11,16]
def side_frames(mask,dirn,front,back,cycles=2,P=150,K=50):
    """scenery of each glass row as a seamless band moving toward the back; blur grows from front edge to back edge"""
    rows=[]
    for y in range(H):
        xs=np.nonzero(mask[y])[0]
        if len(xs)<6: continue
        for rr in np.split(xs,np.nonzero(np.diff(xs)>1)[0]+1):
            if len(rr)<6: continue
            xa,xb=rr[0],rr[-1]+1
            seg=cv2.resize(PLATE[y:y+1,xa:xb],(P+K,1),interpolation=cv2.INTER_LINEAR)[0]
            wgt=np.linspace(0,1,K)[:,None]; tile=seg[:P].copy(); tile[:K]=seg[P:P+K]*(1-wgt)+seg[:K]*wgt
            rows.append((y,xa,xb,tile))
    ys,xs=np.nonzero(mask); y0,y1,x0,x1=ys.min()-4,ys.max()+5,max(0,xs.min()-30),min(W,xs.max()+31)
    mm=mask[y0:y1,x0:x1].astype(np.float32)
    tpos=np.clip((front-(GX[y0:y1,x0:x1]))/(front-back),0,1) if front>back else np.clip((GX[y0:y1,x0:x1]-front)/(back-front),0,1)
    sig=1+15*tpos**1.3
    out=[]
    for k in range(N):
        lay=PLATE[y0:y1,x0:x1].copy()
        for y,xa,xb,tile in rows:
            xx=np.arange(xa,xb); off=k*cycles*P/N*dirn
            lay[y-y0,xa-x0:xb-x0]=tile[np.mod(np.round((xx-xa)*P/(xb-xa)-off).astype(int),P)]
        stack=[]
        for s in SIG:
            if s==0: stack.append(lay); continue
            num=cv2.GaussianBlur(lay*mm[...,None],(0,0),sigmaX=s,sigmaY=.6); den=cv2.GaussianBlur(mm,(0,0),sigmaX=s,sigmaY=.6)[...,None]
            stack.append(num/np.maximum(den,1e-3))
        idx=np.interp(sig,SIG,np.arange(len(SIG))); lo=np.floor(idx).astype(int); hi=np.minimum(lo+1,len(SIG)-1); fr=(idx-lo)[...,None]
        st=np.stack(stack,0); res=np.take_along_axis(st,lo[None,...,None].repeat(3,-1),0)[0]*(1-fr)+np.take_along_axis(st,hi[None,...,None].repeat(3,-1),0)[0]*fr
        full=PLATE.copy(); sub=full[y0:y1,x0:x1]; sub[:]=np.where(mm[...,None]>0,res,sub); out.append(full)
    return out
SL=side_frames(SIDE_L,-1,front=225,back=35)      # left windows: front edge toward the windscreen (right), back edge at the left
SR=side_frames(SIDE_R,+1,front=1400,back=1562)   # right windows: front edge at the left, back edge at the right
frames=[]
for k in range(N):
    t=k/N*T; img=PLATE.copy()
    for M_,FR_ in ((SIDE_L,SL[k]),(SIDE_R,SR[k])):
        img[M_>0]=PLATE[M_>0]*(1-OPA)+FR_[M_>0]*OPA      # moving blurred view over the still painting
    img=img*(1-LINEA[...,None])+PLATE*LINEA[...,None]
    dy,rot=jolt(t); cx,cy=800,300; c,s=np.cos(rot),np.sin(rot)
    mx=cx+(GX-cx)*c-(GY-cy)*s; my=cy+(GX-cx)*s+(GY-cy)*c-dy
    frames.append(cv2.remap(img,mx.astype(np.float32),my.astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT))
GM=np.clip(cv2.GaussianBlur(GLASS.astype(np.float32),(0,0),.8),0,1)
if len(sys.argv)>1:
    import imageio.v2 as iio
    from PIL import Image
    big=[np.clip(f*GM[...,None]+B*(1-GM[...,None]),0,255).astype(np.uint8) for f in frames]
    iio.mimsave(S+'b7/p8_preview.mp4',[np.asarray(Image.fromarray(b).resize((1200,674))) for b in big]*3,fps=N/T,quality=8,macro_block_size=2)
    Image.fromarray(np.concatenate([big[k][40:540,0:260] for k in (0,10,20,30)]+[big[k][40:540,1340:1600] for k in (0,10,20,30)],1)).save(S+'conv/p8sides.jpg',quality=90)
    sys.exit()
windfx.add_layer('seixal:7','','b7p8_lb')
pa,box=F.save(frames,GM,'b7p8','lb'); windfx.add_layer('seixal:7',F.loop(pa,box,T),'b7p8_lb'); print('lb',len(pa),box)
