"""layerview.py <key> <stem> : composite raw frame files of a layer (pre-repack) and save strip + heat + gif"""
import sys,re,glob,numpy as np
from PIL import Image
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'; A=S+'artifact-files/87e1712e-5e90-4175-b828-2581544915d4/'
key,stem=sys.argv[1],sys.argv[2]
h=open(A+'index.html').read(); i=h.find(f"'{key}':"); l=h[i:h.find('\n',i)]
img=re.search(r'<image id="\w+ph" href="img/([^"]+)"',l).group(1)
m=re.search(r'<image href="img/'+stem+r'00\.webp" x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"',l)
x,y,w,hh=[float(v) for v in m.groups()]
base=Image.open(S+'gen/masters/'+img.replace('.jpg','.jpg')).convert('RGB').resize((1600,898))
X,Y,Wd,Hd=round(x*1600/465.8),round(y*898/260),round(w*1600/465.8),round(hh*898/260)
fr=[]
for f in sorted(glob.glob(A+f'img/{stem}[0-9][0-9].webp')):
    q=Image.open(f).convert('RGBA').resize((Wd,Hd)); b=base.copy(); b.paste(q,(X,Y),q); fr.append(b)
crop=tuple(map(int,sys.argv[3].split(','))) if len(sys.argv)>3 else (X,Y,X+Wd,Y+Hd)
c=[f.crop(crop) for f in fr]
c[0].save(S+f'conv/{stem}.gif',save_all=True,append_images=c[1:],duration=int(6000/len(c)),loop=0)
a=[np.asarray(q,np.float32) for q in c]; d=np.abs(a[len(a)//4]-a[0]).max(2)
heat=Image.fromarray(np.clip(d*6,0,255).astype(np.uint8))
wq=min(600,c[0].width); r=wq/c[0].width; s=[q.resize((wq,int(q.height*r))) for q in (c[0],c[len(c)//4],heat.convert('RGB'))]
o=Image.new('RGB',(wq,s[0].height*3)); [o.paste(q,(0,j*q.height)) for j,q in enumerate(s)]; o.save(S+f'conv/{stem}_view.jpg',quality=88)
print(len(fr), crop)
