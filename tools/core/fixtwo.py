import re, sys, numpy as np, cv2
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'; sys.path.insert(0,S)
from PIL import Image
A=S+'artifact-files/87e1712e-5e90-4175-b828-2581544915d4/'; G=6; W,H=1600,898; SX=1600/465.8; SY=898/260
s=open(A+'index.html').read()
def sheets(key):
    i=s.find(f"'{key}':"); line=s[i:s.find('\n',i)]
    for m in re.finditer(r'<svg x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)" viewBox="0 0 (\d+) (\d+)"[^>]*><image href="img/([^"]+)_sheet\.webp" width="(\d+)" height="(\d+)"',line):
        x,y,w,h=[float(v) for v in m.groups()[:4]]
        yield (int(round(x*SX)),int(round(y*SY)),int(round(w*SX)),int(round(h*SY))),int(m.group(5)),int(m.group(6)),m.group(7),int(m.group(8)),int(m.group(9))
def edit(stem,fw,fh,sw,sh,fn):
    arr=np.asarray(Image.open(A+f'img/{stem}_sheet.webp').convert('RGBA'),np.float32).copy()
    for r in range(sh//(fh+G)):
        for c in range(sw//(fw+G)):
            f=arr[r*(fh+G):r*(fh+G)+fh,c*(fw+G):c*(fw+G)+fw]; f[...,3]=fn(f[...,3])
    Image.fromarray(arr.astype(np.uint8),'RGBA').save(A+f'img/{stem}_sheet.webp',quality=80,method=6)
# book 4 page 2: keep the two women perfectly still
import hlmask
B=np.asarray(Image.open(S+'gen/masters/b4p2v2.jpg').convert('RGB').resize((W,H)))
P=hlmask.predictor(); P.set_image(B)
def sm(box,pos):
    ms,sc,_=P.predict(point_coords=np.array(pos,float),point_labels=np.ones(len(pos)),box=np.array(box,float),multimask_output=True)
    return ms[int(np.argmax([m.sum() for m in ms]))].astype(np.uint8)
ppl=sm([0,330,280,898],[(120,450),(140,700),(60,600)])|sm([180,330,560,898],[(330,450),(330,700),(250,800)])
ppl=cv2.dilate(ppl,np.ones((15,15),np.uint8)).astype(np.float32); ppl=np.clip(cv2.GaussianBlur(ppl,(0,0),3)*1.5,0,1)
Image.fromarray((ppl*255).astype(np.uint8)).save(S+'city2/b4p2_ppl.png')
for (bx,by,bw,bh),fw,fh,stem,sw,sh in sheets('jantar:1'):
    keep=1-cv2.resize(ppl[by:by+bh,bx:bx+bw],(fw,fh))
    if (keep<.99).sum()==0: continue
    edit(stem,fw,fh,sw,sh,lambda a,k=keep: a*k); print(stem,'women held still')
# book 5 page 8: feather the foliage layer's edges
for (bx,by,bw,bh),fw,fh,stem,sw,sh in sheets('passeio:7'):
    if not stem.endswith('_lf'): continue
    a0=np.asarray(Image.open(A+f'img/{stem}_sheet.webp').convert('RGBA'))[0:fh,0:fw,3]
    inside=(a0>8).astype(np.uint8); inside[0,:]=inside[-1,:]=inside[:,0]=inside[:,-1]=0
    ramp=np.clip(cv2.distanceTransform(inside,cv2.DIST_L2,5)/22.,0,1); ramp=ramp*ramp*(3-2*ramp)
    edit(stem,fw,fh,sw,sh,lambda a,r=ramp: a*r); print(stem,'edges feathered')
