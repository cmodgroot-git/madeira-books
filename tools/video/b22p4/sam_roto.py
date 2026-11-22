# MobileSAM per frame, prompted by the current rotoscope (box + interior points); soft alpha from SAM logits
import sys,cv2,numpy as np,pickle,glob,torch
import os; sys.path[:0]=[os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','shim'),'/home/claude/work/MobileSAM']
from mobile_sam import sam_model_registry, SamPredictor
torch.set_num_threads(2)
p=SamPredictor(sam_model_registry['vit_t'](checkpoint='/home/claude/work/MobileSAM/weights/mobile_sam.pt').eval())
F=sorted(glob.glob('fr/*.png')); N=len(F); R=pickle.load(open('roto.pkl','rb'))
K=lambda r:cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*r+1,2*r+1))
out={'cabeca':[],'rita':[]}; log=[]
for t,f in enumerate(F):
    im=cv2.cvtColor(cv2.imread(f),cv2.COLOR_BGR2RGB); p.set_image(im)
    for k in out:
        ref=R[k][t]>127; ys,xs=np.nonzero(ref)
        box=np.array([xs.min()-6,ys.min()-6,xs.max()+6,ys.max()+6])
        core=cv2.erode(ref.astype(np.uint8),K(8)); cy,cx=np.nonzero(core)
        idx=np.linspace(0,len(cx)-1,6).astype(int) if len(cx)>6 else []
        pts=np.stack([cx[idx],cy[idx]],1) if len(idx) else None
        lg,sc,_=p.predict(point_coords=pts,point_labels=np.ones(len(pts)) if pts is not None else None,box=box,multimask_output=True,return_logits=True)
        best=None
        for i in range(3):
            m=lg[i]>0; iou=(m&ref).sum()/max(1,(m|ref).sum())
            if best is None or iou>best[0]: best=(iou,i)
        iou,i=best; a=1/(1+np.exp(-lg[i]/1.5))
        if iou<0.72: a=R[k][t].astype(np.float32)/255   # disagree -> keep the old cut
        out[k].append(a.astype(np.float32)); log.append((t,k,round(float(iou),3)))
    if t%12==0: print(t,log[-2:],flush=True)
pickle.dump(out,open('sam_out.pkl','wb')); print('low iou:',[l for l in log if l[2]<0.72])
