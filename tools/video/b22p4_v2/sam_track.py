# Track head, Rita and ball through the clip: flow-carried prior -> MobileSAM (box + interior points) each frame
import sys,cv2,numpy as np,pickle,glob,torch,time
sys.path[:0]=['/home/claude/madeira-books/tools/video/shim','/home/claude/work/MobileSAM']
from mobile_sam import sam_model_registry, SamPredictor
torch.set_num_threads(2)
p=SamPredictor(sam_model_registry['vit_t'](checkpoint='/home/claude/work/MobileSAM/weights/mobile_sam.pt').eval())
F=sorted(glob.glob('fr/*.png')); N=len(F); H,W=720,1280
W0=np.float32([[0.995,0,2.354],[0,0.995,1.163]])
R=pickle.load(open('../videotest/roto_final.pkl','rb')); B=pickle.load(open('../videotest/ballmatte.pkl','rb'))
seed={'cabeca':R['cabeca'][0].astype(np.float32)/255,'rita':R['rita'][0].astype(np.float32)/255,'bola':B[0]}
seed={k:cv2.warpAffine(v,W0,(W,H)) for k,v in seed.items()}
K=lambda r:cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*r+1,2*r+1))
dis=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM); yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
pad={'cabeca':8,'rita':10,'bola':10}; ero={'cabeca':8,'rita':8,'bola':5}
out={k:[] for k in seed}; log=[]; prevg=None; prev={k:v for k,v in seed.items()}
t0=time.time()
for t,f in enumerate(F):
    im=cv2.imread(f); g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    if t>0:
        fl=dis.calc(g,prevg,None)
        prior={k:cv2.remap(prev[k],xx+fl[...,0],yy+fl[...,1],cv2.INTER_LINEAR) for k in prev}
    else: prior=prev
    p.set_image(cv2.cvtColor(im,cv2.COLOR_BGR2RGB))
    for k in seed:
        ref=prior[k]>0.5
        if ref.sum()<30: ref=prev[k]>0.5
        ys,xs=np.nonzero(ref); q=pad[k]
        box=np.array([xs.min()-q,ys.min()-q,xs.max()+q,ys.max()+q])
        core=cv2.erode(ref.astype(np.uint8),K(ero[k])); cy,cx=np.nonzero(core)
        if len(cx)<6: cy,cx=ys,xs
        idx=np.linspace(0,len(cx)-1,6).astype(int); pts=np.stack([cx[idx],cy[idx]],1)
        lg,sc,_=p.predict(point_coords=pts,point_labels=np.ones(len(pts)),box=box,multimask_output=True,return_logits=True)
        best=max(range(3),key=lambda i:((lg[i]>0)&ref).sum()/max(1,((lg[i]>0)|ref).sum()))
        m=lg[best]>0; iou=(m&ref).sum()/max(1,(m|ref).sum())
        a=(1/(1+np.exp(-lg[best]/1.5))).astype(np.float32)
        lim=(0.6 if k!='bola' else 0.4)
        if iou<lim: a=prior[k].astype(np.float32)
        # keep the biggest piece
        n,l,st,_=cv2.connectedComponentsWithStats((a>0.5).astype(np.uint8))
        if n>2: a=a*cv2.dilate((l==1+st[1:,4].argmax()).astype(np.uint8),K(2))
        out[k].append(a); prev[k]=a; log.append((t,k,round(float(iou),2)))
    prevg=g
    if t%20==0: print(t,round(time.time()-t0),log[-3:],flush=True)
pickle.dump({k:[(a*255).astype(np.uint8) for a in v] for k,v in out.items()},open('track_sam.pkl','wb'))
print('low:',[l for l in log if l[2]<0.6]); print('done',round(time.time()-t0))
