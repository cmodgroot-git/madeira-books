"""Carry existing animation sheets over to an edited picture. Glow/steam sheets: each frame is re-lit by the
ratio new/old picture (exact for brightness-only effects). Sea sheets (_ls): rebuilt with frames.ripple on the new
picture, using the old water alpha minus anything that changed (new buildings, yachts). usage: citylayers.py key old new"""
import sys, re, numpy as np, cv2
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'; sys.path.insert(0,S)
import frames as F, windfx
from PIL import Image
A=S+'artifact-files/87e1712e-5e90-4175-b828-2581544915d4/'
G=6; W,H=1600,898; SX=1600/465.8; SY=898/260
key,old,new=sys.argv[1:4]; img=old.split('.')[0][:4]
Bo=np.asarray(Image.open(S+'gen/masters/'+old).convert('RGB').resize((W,H)),np.float32)
Bn=np.asarray(Image.open(S+'gen/masters/'+new).convert('RGB').resize((W,H)),np.float32)
chg=(np.abs(Bo-Bn).mean(2)>18).astype(np.uint8); chg=cv2.dilate(chg,np.ones((7,7),np.uint8))
h=open(A+'index.html').read(); i=h.find(f"'{key}':"); line=h[i:h.find('\n',i)]
pat=re.compile(r'<svg x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)" viewBox="0 0 (\d+) (\d+)"[^>]*><image href="img/([^"]+)_sheet\.webp" width="(\d+)" height="(\d+)"(.*?)</svg>',re.S)
for m in pat.finditer(line):
    x,y,w,hh=[float(v) for v in m.groups()[:4]]; fw,fh=int(m.group(5)),int(m.group(6)); stem=m.group(7); sw,sh=int(m.group(8)),int(m.group(9))
    cols,rows=sw//(fw+G),sh//(fh+G); n=len(re.search(r'values="([^"]+)"',m.group(10)).group(1).split(';')) if 'values=' in m.group(10) else cols*rows
    bx0,by0,bw,bh=int(round(x*SX)),int(round(y*SY)),int(round(w*SX)),int(round(hh*SY))
    sheet=Image.open(A+f'img/{stem}_sheet.webp').convert('RGBA'); arr=np.asarray(sheet,np.float32).copy()
    if stem.endswith('_ls'):
        a0=arr[0:fh,0:fw,3]/255; mask=np.zeros((H,W),np.float32)
        mask[by0:by0+bh,bx0:bx0+bw]=cv2.resize(a0,(bw,bh)); mask=mask*(1-chg)
        dur=float(re.search(r'dur="([\d.]+)s"',m.group(10)).group(1)) if 'dur=' in m.group(10) else 6
        fr=F.ripple(Bn,mask,n=16,near=2.6)
        pa,box=F.save(fr,mask,img,'ls'); windfx.add_layer(key,F.loop(pa,box,6.0),stem); print(stem,'rebuilt',box); continue
    co=cv2.resize(Bo[by0:by0+bh,bx0:bx0+bw],(fw,fh),interpolation=cv2.INTER_AREA); cn=cv2.resize(Bn[by0:by0+bh,bx0:bx0+bw],(fw,fh),interpolation=cv2.INTER_AREA)
    ratio=(cn+1)/(co+1)
    for r in range(rows):
        for c in range(cols):
            y0,x0=r*(fh+G),c*(fw+G); f=arr[y0:y0+fh,x0:x0+fw]
            f[...,:3]=np.clip(f[...,:3]*ratio,0,255)
    Image.fromarray(arr.astype(np.uint8),'RGBA').save(A+f'img/{stem}_sheet.webp',quality=80,method=6); print(stem,'relit',cols*rows)
