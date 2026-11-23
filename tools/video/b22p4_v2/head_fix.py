# Re-run the head from frame 130: keep the head size steady (pick the SAM mask whose area matches the head's
# typical area), give the box extra room above for the curls, and prompt points across the whole head.
import sys,cv2,numpy as np,pickle,glob,torch
sys.path[:0]=['/home/claude/madeira-books/tools/video/shim','/home/claude/work/MobileSAM']
from mobile_sam import sam_model_registry, SamPredictor
torch.set_num_threads(2)
p=SamPredictor(sam_model_registry['vit_t'](checkpoint='/home/claude/work/MobileSAM/weights/mobile_sam.pt').eval())
F=sorted(glob.glob('fr/*.png')); N=len(F); H,W=720,1280
TR=pickle.load(open('track_sam.pkl','rb')); A=[a.astype(np.float32)/255 for a in TR['cabeca']]
S0=100; ref_area=np.median([(A[t]>0.5).sum() for t in range(60,S0)])
hh=[np.ptp(np.nonzero(A[t]>0.5)[0]) for t in range(60,S0)]; HREF=float(np.median(hh)); print('head height',HREF)
def clip(a):
    ys=np.nonzero(a>0.5)[0]
    if len(ys)==0: return a
    b=a.copy(); b[int(ys.min()+HREF*1.04):]=0; return b
dis=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM); yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
K=lambda r:cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*r+1,2*r+1))
prev=A[S0-1]; prevg=cv2.cvtColor(cv2.imread(F[S0-1]),cv2.COLOR_BGR2GRAY); log=[]
for t in range(S0,N):
    im=cv2.imread(F[t]); g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY); fl=dis.calc(g,prevg,None)
    prior=clip(cv2.remap(prev,xx+fl[...,0],yy+fl[...,1],cv2.INTER_LINEAR)); ref=prior>0.5
    # if the prior has shrunk, grow it back toward the typical size before prompting
    if ref.sum()<0.85*ref_area: ref=cv2.dilate(ref.astype(np.uint8),K(6))>0
    ys,xs=np.nonzero(ref); hgt=ys.max()-ys.min()
    box=np.array([xs.min()-14,ys.min()-int(0.18*hgt)-10,xs.max()+14,ys.max()+6])
    core=cv2.erode(ref.astype(np.uint8),K(6)); cy,cx=np.nonzero(core)
    idx=np.linspace(0,len(cx)-1,9).astype(int); pts=np.stack([cx[idx],cy[idx]],1)
    # negative points on the shirt: a row just below the chin, and the shoulders
    by=ys.max(); mx=int(xs.mean()); wd=xs.max()-xs.min()
    neg=np.array([[mx,by+35],[mx-int(0.6*wd),by+45],[mx+int(0.6*wd),by+45],[mx,by+80]])
    neg[:,0]=np.clip(neg[:,0],0,W-1); neg[:,1]=np.clip(neg[:,1],0,H-1)
    allp=np.vstack([pts,neg]); labs=np.r_[np.ones(len(pts)),np.zeros(len(neg))]
    p.set_image(cv2.cvtColor(im,cv2.COLOR_BGR2RGB))
    lg,sc,_=p.predict(point_coords=allp,point_labels=labs,box=box,multimask_output=True,return_logits=True)
    def score(i):
        m=lg[i]>0; iou=(m&ref).sum()/max(1,(m|ref).sum()); return iou-0.8*abs(m.sum()/ref_area-1)
    lg=np.stack([np.where(clip((l>0).astype(np.float32))>0,l,-10) for l in lg]); b=max(range(3),key=score); a=(1/(1+np.exp(-lg[b]/1.5))).astype(np.float32)
    ar=(a>0.5).sum()/ref_area
    if not (0.75<ar<1.3): a=prior
    n,l,st,_=cv2.connectedComponentsWithStats((a>0.5).astype(np.uint8))
    if n>2: a=a*cv2.dilate((l==1+st[1:,4].argmax()).astype(np.uint8),K(2))
    A[t]=a; prev=a; prevg=g; log.append((t,round(ar,2)))
    if t%30==0: print(t,log[-1],flush=True)
TR['cabeca']=[(a*255).astype(np.uint8) for a in A]; pickle.dump(TR,open('track_sam.pkl','wb')); print('done',ref_area)
