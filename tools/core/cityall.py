"""Move a page to an edited picture: sea sheets (_ls) rebuilt with ripple on the new picture (old water alpha minus
changed pixels); sheets painted from the picture get the picture's change added frame by frame; overlay sheets
(rain, streaks) that don't come from the picture are left alone. usage: cityall.py key oldmaster newmaster"""
import sys, re, numpy as np, cv2
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'; sys.path.insert(0,S)
import frames as F, windfx
from PIL import Image
A=S+'artifact-files/87e1712e-5e90-4175-b828-2581544915d4/'; G=6; W,H=1600,898; SX=1600/465.8; SY=898/260
key,old,new=sys.argv[1:4]; img=re.match(r'b\dp\d',old).group(0)
Bo=np.asarray(Image.open(S+'gen/masters/'+old).convert('RGB').resize((W,H)),np.float32)
Bn=np.asarray(Image.open(S+'gen/masters/'+new).convert('RGB').resize((W,H)),np.float32)
chg=cv2.dilate((np.abs(Bo-Bn).mean(2)>18).astype(np.uint8),np.ones((7,7),np.uint8))
h=open(A+'index.html').read(); i=h.find(f"'{key}':"); line=h[i:h.find('\n',i)]
pat=re.compile(r'<svg x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)" viewBox="0 0 (\d+) (\d+)"[^>]*><image href="img/([^"]+)_sheet\.webp" width="(\d+)" height="(\d+)"')
for m in pat.finditer(line):
    x,y,w,hh=[float(v) for v in m.groups()[:4]]; fw,fh=int(m.group(5)),int(m.group(6)); stem=m.group(7); sw,sh=int(m.group(8)),int(m.group(9))
    bx,by,bw,bh=int(round(x*SX)),int(round(y*SY)),int(round(w*SX)),int(round(hh*SY))
    arr=np.asarray(Image.open(A+f'img/{stem}_sheet.webp').convert('RGBA'),np.float32).copy()
    co=cv2.resize(Bo[by:by+bh,bx:bx+bw],(fw,fh),interpolation=cv2.INTER_AREA); cn=cv2.resize(Bn[by:by+bh,bx:bx+bw],(fw,fh),interpolation=cv2.INTER_AREA)
    if stem.endswith('_ls'):
        a0=arr[0:fh,0:fw,3]/255; mask=np.zeros((H,W),np.float32); mask[by:by+bh,bx:bx+bw]=cv2.resize(a0,(bw,bh)); mask*=(1-chg)
        if (mask>.3).sum()<200: windfx.add_layer(key,'',stem); print(stem,'removed (sea gone)'); continue
        fr=F.ripple(Bn,mask,n=16,near=2.6); pa,box=F.save(fr,mask,img,'ls'); windfx.add_layer(key,F.loop(pa,box,6.0),stem); print(stem,'rebuilt'); continue
    f0=arr[0:fh,0:fw]; sel=f0[...,3]>128
    sim=np.abs(f0[...,:3]-co)[sel].mean() if sel.sum()>50 else 999
    if sim>25: print(stem,'overlay, kept (%.0f)'%sim); continue
    d=cn-co
    for r in range(sh//(fh+G)):
        for c in range(sw//(fw+G)):
            f=arr[r*(fh+G):r*(fh+G)+fh,c*(fw+G):c*(fw+G)+fw]; f[...,:3]=np.clip(f[...,:3]+d,0,255)
    Image.fromarray(arr.astype(np.uint8),'RGBA').save(A+f'img/{stem}_sheet.webp',quality=80,method=6); print(stem,'carried (%.0f)'%sim)
