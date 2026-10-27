import sys, re, numpy as np, cv2
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'; sys.path.insert(0,S)
import frames as F, windfx
from PIL import Image
A=S+'artifact-files/87e1712e-5e90-4175-b828-2581544915d4/'; G=6; W,H=1600,898; SX=1600/465.8; SY=898/260
key,old,new,stem=sys.argv[1:5]; img=stem[:4]
h=open(S+'published_old/index.html').read(); i=h.find(f"'{key}':"); line=h[i:h.find('\n',i)]
m=re.search(r'<svg x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)" viewBox="0 0 (\d+) (\d+)"[^>]*><image href="img/'+stem+r'_sheet\.webp"',line)
x,y,w,hh=[float(v) for v in m.groups()[:4]]; fw,fh=int(m.group(5)),int(m.group(6))
bx,by,bw,bh=int(round(x*SX)),int(round(y*SY)),int(round(w*SX)),int(round(hh*SY))
a0=np.asarray(Image.open(A+f'img/{stem}_sheet.webp').convert('RGBA'),np.float32)[0:fh,0:fw,3]/255
Bo=np.asarray(Image.open(S+'gen/masters/'+old).convert('RGB').resize((W,H)),np.float32); Bn=np.asarray(Image.open(S+'gen/masters/'+new).convert('RGB').resize((W,H)),np.float32)
mask=np.zeros((H,W),np.float32); mask[by:by+bh,bx:bx+bw]=cv2.resize(a0,(bw,bh))
# keep only pixels that still look like dark night sea (blue, not lit buildings/lamps)
L=F.lum(Bn); b,g,r=Bn[...,2],Bn[...,1],Bn[...,0]
sea=((b>r+10)&(L<150)).astype(np.float32); sea=cv2.GaussianBlur(cv2.morphologyEx(sea,cv2.MORPH_OPEN,np.ones((5,5),np.uint8)),(0,0),1.5)
mask=mask*sea; print(stem,'pixels',(mask>.3).sum())
fr=F.ripple(Bn,mask,n=16,near=2.6); pa,box=F.save(fr,mask,img,'ls'); windfx.add_layer(key,F.loop(pa,box,6.0),stem); print('ok',box)
