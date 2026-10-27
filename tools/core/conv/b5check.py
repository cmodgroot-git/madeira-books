import numpy as np, re, glob
from PIL import Image
A='artifact-files/87e1712e-5e90-4175-b828-2581544915d4/'
h=open(A+'index.html').read()
tiles=[]
for p,name,ks in [(1,'lc',(0,6)),(3,'lr',(0,8)),(4,'lw',(0,8)),(6,'lb',(0,12)),(8,'lf',(0,8))]:
    base=f'b5p{p}'; B=Image.open(f'gen/masters/{base}.jpg').convert('RGB')
    m=re.search(r'<image href="img/'+base+'_'+name+r'00\.webp" x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"',h)
    x,y,w,hh=[float(v) for v in m.groups()]; X,Y,Wd,Hd=x*1600/465.8,y*898/260,w*1600/465.8,hh*898/260
    row=[]
    for k in ks:
        f=Image.open(A+f'img/{base}_{name}{k:02d}.webp').convert('RGBA').resize((int(Wd),int(Hd)))
        c=B.copy(); c.paste(f,(int(X),int(Y)),f); row.append(c)
    d=np.abs(np.asarray(row[0],float)-np.asarray(row[1],float)).max(2); hm=Image.fromarray(np.clip(d*4,0,255).astype(np.uint8)).convert('RGB')
    tiles.append([r.resize((480,269)) for r in row]+[hm.resize((480,269))])
o=Image.new('RGB',(1440,269*len(tiles)))
for j,t in enumerate(tiles):
    for k,im in enumerate(t): o.paste(im,(k*480,j*269))
o.save('conv/b5anim.jpg',quality=82)
