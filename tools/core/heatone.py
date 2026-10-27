import re, sys, numpy as np
from PIL import Image, ImageDraw
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'; A=S+'artifact-files/87e1712e-5e90-4175-b828-2581544915d4/'; G=6
s=open(A+'index.html').read()
def heat(key,only=None):
    i=s.find(f"'{key}':"); line=s[i:s.find('\n',i)]; sid,pg=key.split(':')
    img=re.search(r'id="%s%sph" href="img/([^"]+)"'%(sid,pg),line).group(1)
    B=np.asarray(Image.open(A+'img/'+img).convert('RGB').resize((1600,898)),np.float32); hm=np.zeros((898,1600),np.float32)
    for m in re.finditer(r'<svg x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)" viewBox="0 0 (\d+) (\d+)"[^>]*><image href="img/([^"]+)_sheet\.webp" width="(\d+)" height="(\d+)"',line):
        stem=m.group(7)
        if only and only not in stem: continue
        x,y,w,h=[float(v) for v in m.groups()[:4]]; fw,fh=int(m.group(5)),int(m.group(6)); sw,sh=int(m.group(8)),int(m.group(9))
        X,Y,Wd,Hd=int(x*1600/465.8),int(y*898/260),max(1,int(w*1600/465.8)),max(1,int(h*898/260))
        sheet=Image.open(A+f'img/{stem}_sheet.webp').convert('RGBA'); fr=[]
        for r in range(sh//(fh+G)):
            for c in range(sw//(fw+G)):
                f=np.asarray(sheet.crop((c*(fw+G),r*(fh+G),c*(fw+G)+fw,r*(fh+G)+fh)).resize((Wd,Hd)),np.float32)
                if f[...,3].max()==0: continue
                bb=B[Y:Y+Hd,X:X+Wd]; f=f[:bb.shape[0],:bb.shape[1]]; a=f[...,3:]/255; fr.append((f[...,:3]*a+bb*(1-a)).mean(2))
        if len(fr)>1: st=np.stack(fr); d=st.max(0)-st.min(0); hm[Y:Y+d.shape[0],X:X+d.shape[1]]=np.maximum(hm[Y:Y+d.shape[0],X:X+d.shape[1]],d)
    g=Image.fromarray(B.mean(2).astype(np.uint8)).convert('RGB'); h=Image.fromarray(np.clip(hm*5,0,255).astype(np.uint8)).convert('RGB')
    t=Image.blend(g,h,.75); ImageDraw.Draw(t).text((8,8),key+(' '+only if only else ''),fill=(255,255,0)); return t
keys=sys.argv[2:]; out=sys.argv[1]
ims=[heat(*k.split('/')) for k in keys]
S2=Image.new('RGB',(1600,898*((len(ims)+1)//2)//2*1)) if False else None
W=800; Hh=449; sh=Image.new('RGB',(W*2,Hh*((len(ims)+1)//2)))
for j,t in enumerate(ims): sh.paste(t.resize((W,Hh)),((j%2)*W,(j//2)*Hh))
sh.save(S+'city2/'+out,quality=85)
