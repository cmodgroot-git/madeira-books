import cv2,numpy as np,pickle,glob,json
F=sorted(glob.glob('fr/*.png')); fr=[cv2.imread(f) for f in F]; H,W=fr[0].shape[:2]
M=dict(pickle.load(open('/home/claude/work/b22/hlcache/jogo_3.pkl','rb')))
master=cv2.imread('/home/claude/work/b22/masters/b22p4.jpg'); master=cv2.resize(master,(W,H))
# align master -> frame 0 (Flow may reframe slightly)
g0=cv2.cvtColor(fr[0],cv2.COLOR_BGR2GRAY).astype(np.float32); gm=cv2.cvtColor(master,cv2.COLOR_BGR2GRAY).astype(np.float32)
Wm=np.eye(2,3,dtype=np.float32)
try: _,Wm=cv2.findTransformECC(gm,g0,Wm,cv2.MOTION_AFFINE,(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,100,1e-5),None,5)
except Exception as e: print('ecc fail',e)
print('master->frame0 affine',np.round(Wm,3).tolist())
def toF(m): return cv2.warpAffine(cv2.resize(m.astype(np.uint8)*255,(W,H)),Wm,(W,H))>127
ball0=toF(M['bola']); head0=toF(M['cabeca']); golo0=toF(M['golo'])&~ball0
# Rita: hand polygon on the master (1600x898), scaled
rp=np.array([(722,388),(760,388),(778,430),(800,470),(796,560),(790,640),(782,670),(745,672),(733,600),(726,520),(716,470),(712,420)],np.float32)
rm=np.zeros((898,1600),np.uint8); cv2.fillPoly(rm,[rp.astype(np.int32)],1); rita0=toF(rm.astype(bool))
gray=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) for f in fr]
dis=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
def sim_track(mask0,pad=6):
    out=[mask0]; m=mask0
    for t in range(1,len(fr)):
        fl=dis.calc(gray[t-1],gray[t],None)
        ys,xs=np.nonzero(cv2.erode(m.astype(np.uint8),np.ones((pad,pad),np.uint8)) if m.sum()>400 else m)
        if len(xs)<10: out.append(m); continue
        idx=np.random.default_rng(0).choice(len(xs),min(600,len(xs)),replace=False)
        p0=np.stack([xs[idx],ys[idx]],1).astype(np.float32); p1=p0+fl[ys[idx],xs[idx]]
        A,_=cv2.estimateAffinePartial2D(p0,p1,method=cv2.RANSAC,ransacReprojThreshold=2.0)
        if A is None: A=np.float32([[1,0,0],[0,1,0]])
        m=cv2.warpAffine(m.astype(np.uint8),A,(W,H),flags=cv2.INTER_NEAREST)>0; out.append(m)
    return out
def bg_track(mask0,excl):
    # camera motion from background features (people excluded), applied to the goal frame
    orb=cv2.ORB_create(3000); k0,d0=orb.detectAndCompute(gray[0],(~excl[0]).astype(np.uint8)*255)
    bf=cv2.BFMatcher(cv2.NORM_HAMMING,crossCheck=True); out=[mask0]
    for t in range(1,len(fr)):
        k1,d1=orb.detectAndCompute(gray[t],(~excl[t]).astype(np.uint8)*255)
        mt=sorted(bf.match(d0,d1),key=lambda x:x.distance)[:500]
        p0=np.float32([k0[x.queryIdx].pt for x in mt]); p1=np.float32([k1[x.trainIdx].pt for x in mt])
        Hm,_=cv2.findHomography(p0,p1,cv2.RANSAC,3.0)
        out.append(cv2.warpPerspective(mask0.astype(np.uint8),Hm,(W,H),flags=cv2.INTER_NEAREST)>0)
    return out
def ball_track(mask0):
    ys,xs=np.nonzero(mask0); cx,cy,r=xs.mean(),ys.mean(),np.sqrt(mask0.sum()/np.pi)
    x0,y0,x1,y1=xs.min(),ys.min(),xs.max()+1,ys.max()+1; tpl=gray[0][y0:y1,x0:x1]; tm=mask0[y0:y1,x0:x1].astype(np.uint8)
    out=[mask0]; v=np.zeros(2); pos=np.array([cx,cy])
    for t in range(1,len(fr)):
        best=None; pred=pos+v
        for s in np.linspace(0.6,1.25,14):
            T=cv2.resize(tpl,None,fx=s,fy=s); Tm=cv2.resize(tm,None,fx=s,fy=s,interpolation=cv2.INTER_NEAREST)
            th,tw=T.shape; R=int(max(60,np.linalg.norm(v)*2.5+40))
            ax,ay=int(max(0,pred[0]-R-tw/2)),int(max(0,pred[1]-R-th/2)); bx,by=int(min(W,pred[0]+R+tw/2)),int(min(H,pred[1]+R+th/2))
            roi=gray[t][ay:by,ax:bx]
            if roi.shape[0]<=th or roi.shape[1]<=tw: continue
            res=cv2.matchTemplate(roi,T,cv2.TM_CCOEFF_NORMED,mask=Tm)
            res=np.nan_to_num(res,nan=-1); _,mv,_,ml=cv2.minMaxLoc(res)
            if best is None or mv>best[0]: best=(mv,ax+ml[0]+tw/2,ay+ml[1]+th/2,s*r)
        mv,nx,ny,nr=best; np_=np.array([nx,ny]); v=0.6*v+0.4*(np_-pos); pos=np_
        m=np.zeros((H,W),np.uint8); cv2.circle(m,(int(nx),int(ny)),int(nr),1,-1); out.append(m>0)
        if t%12==0: print('ball',t,round(mv,2),int(nx),int(ny),round(nr,1))
    return out
T={}
T['cabeca']=sim_track(head0,3); print('head done')
T['rita']=sim_track(rita0,3); print('rita done')
T['bola']=ball_track(ball0)
# exclude people/ball for camera motion: dilated head-to-body area is unknown, so exclude a band around tracked items
excl=[cv2.dilate((T['cabeca'][t]|T['rita'][t]|T['bola'][t]).astype(np.uint8),np.ones((150,150),np.uint8))>0 for t in range(len(fr))]
goal=bg_track(golo0,excl); T['golo']=[goal[t]|T['bola'][t] for t in range(len(fr))]
pickle.dump(T,open('tracks.pkl','wb'))
# overlay video: dim outside, bright inside + outline, one pass per word
names={'bola':'bola','golo':'golo','cabeca':'cabeça','rita':'(Rita)'}
vw=cv2.VideoWriter('demo.mp4',cv2.VideoWriter_fourcc(*'mp4v'),24,(W,H))
for k in ['bola','cabeca','golo','rita']:
    for t,f in enumerate(fr):
        m=T[k][t]; o=(f*0.45).astype(np.uint8); o[m]=f[m]
        cs,_=cv2.findContours(m.astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE); cv2.drawContours(o,cs,-1,(80,230,255),3)
        cv2.putText(o,names[k],(30,60),cv2.FONT_HERSHEY_DUPLEX,1.6,(255,255,255),3); vw.write(o)
vw.release(); print('ok')
