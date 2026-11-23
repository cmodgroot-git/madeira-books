import sys,cv2,numpy as np,pickle,glob,torch
sys.path[:0]=['/home/claude/madeira-books/tools/video/shim','/home/claude/work/MobileSAM']
from mobile_sam import sam_model_registry, SamPredictor
torch.set_num_threads(2)
p=SamPredictor(sam_model_registry['vit_t'](checkpoint='/home/claude/work/MobileSAM/weights/mobile_sam.pt').eval())
F=sorted(glob.glob('fr/*.png')); out=[]
for t,f in enumerate(F):
    im=cv2.imread(f); hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
    y=((hsv[...,0]>=18)&(hsv[...,0]<=35)&(hsv[...,1]>110)&(hsv[...,2]>110)).astype(np.uint8)
    y[:, :400]=0   # houses on the left are yellow too; the keeper is always right of x=400
    n,l,st,_=cv2.connectedComponentsWithStats(cv2.morphologyEx(y,cv2.MORPH_OPEN,np.ones((5,5),np.uint8)))
    if n<2: out.append(np.zeros(im.shape[:2],np.uint8)); continue
    i=1+st[1:,4].argmax(); x,yy,w,h=st[i,:4]; cy,cx=np.nonzero(l==i)
    box=np.array([x-w*0.9,yy-h*0.6,x+w*1.9,yy+h*2.6]).clip(0,[1279,719,1279,719][0])
    box=np.array([max(0,box[0]),max(0,box[1]),min(1279,box[2]),min(719,box[3])])
    idx=np.linspace(0,len(cx)-1,5).astype(int)
    p.set_image(cv2.cvtColor(im,cv2.COLOR_BGR2RGB))
    m,sc,_=p.predict(point_coords=np.stack([cx[idx],cy[idx]],1),point_labels=np.ones(5),box=box,multimask_output=True)
    k=int(np.argmax([mm.sum() if mm.sum()<w*h*8 else 0 for mm in m]))
    out.append((m[k]*255).astype(np.uint8))
    if t%40==0: print(t,int(m[k].sum()),flush=True)
pickle.dump(out,open('keeper.pkl','wb')); print('done')
