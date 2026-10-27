import re, sys, numpy as np, cv2
from PIL import Image
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'; A=S+'artifact-files/87e1712e-5e90-4175-b828-2581544915d4/'; G=6
s=open(A+'index.html').read()
pages={'manha:0':'b1p1','manha:2':'b1p3','manha:3':'b1p4','sabado:0':'b2p1','sabado:1':'b2p2','passeio:0':'b5p1'}
for key,n in pages.items():
    Bo=np.asarray(Image.open(S+f'gen/masters/{n}.jpg').convert('RGB').resize((1600,898)),np.float32)
    Bn=np.asarray(Image.open(S+f'gen/masters/{n}v2.jpg').convert('RGB').resize((1600,898)),np.float32)
    i=s.find(f"'{key}':"); line=s[i:s.find('\n',i)]
    for m in re.finditer(r'<svg x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)" viewBox="0 0 (\d+) (\d+)"[^>]*><image href="img/([^"]+)_sheet\.webp" width="(\d+)" height="(\d+)"',line):
        stem=m.group(7)
        if stem.endswith('_ls'): continue
        x,y,w,h=[float(v) for v in m.groups()[:4]]; fw,fh=int(m.group(5)),int(m.group(6)); sw,sh=int(m.group(8)),int(m.group(9))
        bx,by,bw,bh=int(round(x*1600/465.8)),int(round(y*898/260)),int(round(w*1600/465.8)),int(round(h*898/260))
        old=np.asarray(Image.open(S+f'published_old/img/{stem}_sheet.webp').convert('RGBA'),np.float32).copy()
        assert old.shape[:2]==(sh,sw),(stem,old.shape,sw,sh)
        co=cv2.resize(Bo[by:by+bh,bx:bx+bw],(fw,fh),interpolation=cv2.INTER_AREA); cn=cv2.resize(Bn[by:by+bh,bx:bx+bw],(fw,fh),interpolation=cv2.INTER_AREA)
        dlt=cn-co
        for r in range(sh//(fh+G)):
            for c in range(sw//(fw+G)):
                f=old[r*(fh+G):r*(fh+G)+fh, c*(fw+G):c*(fw+G)+fw]; f[...,:3]=np.clip(f[...,:3]+dlt,0,255)
        Image.fromarray(old.astype(np.uint8),'RGBA').save(A+f'img/{stem}_sheet.webp',quality=80,method=6); print(key,stem,'fixed')
