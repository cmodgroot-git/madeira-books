import re, sys, numpy as np
from PIL import Image
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'; A=S+'artifact-files/87e1712e-5e90-4175-b828-2581544915d4/'; G=6
def heat(idx,key,base,sdir):
    s=open(idx).read(); i=s.find(f"'{key}':"); line=s[i:s.find('\n',i)]
    B=np.asarray(Image.open(base).convert('RGB').resize((800,449)),np.float32); hmax=np.zeros((449,800),np.float32)
    for m in re.finditer(r'<svg x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)" viewBox="0 0 (\d+) (\d+)"[^>]*><image href="img/([^"]+_sheet\.webp)" width="(\d+)" height="(\d+)"',line):
        x,y,w,h=[float(v) for v in m.groups()[:4]]; fw,fh=int(m.group(5)),int(m.group(6)); sw,sh=int(m.group(8)),int(m.group(9))
        sx,sy=800/465.8,449/260; X,Y,Wd,Hd=int(x*sx),int(y*sy),max(1,int(w*sx)),max(1,int(h*sy))
        sheet=Image.open(sdir+m.group(7)).convert('RGBA'); cols,rows=sw//(fw+G),sh//(fh+G); fr=[]
        for r in range(rows):
            for c in range(cols):
                f=np.asarray(sheet.crop((c*(fw+G),r*(fh+G),c*(fw+G)+fw,r*(fh+G)+fh)).resize((Wd,Hd)),np.float32)
                if f[...,3].max()==0: continue
                a=f[...,3:]/255; comp=f[...,:3]*a+B[Y:Y+Hd,X:X+Wd][:f.shape[0],:f.shape[1]]*(1-a); fr.append(comp.mean(2))
        if len(fr)>1:
            st=np.stack(fr); d=st.max(0)-st.min(0); hmax[Y:Y+d.shape[0],X:X+d.shape[1]]=np.maximum(hmax[Y:Y+d.shape[0],X:X+d.shape[1]],d)
    g=Image.fromarray(B.mean(2).astype(np.uint8)).convert('RGB'); hm=Image.fromarray(np.clip(hmax*5,0,255).astype(np.uint8)).convert('RGB')
    return Image.blend(g,hm,.7)
key,old,new=sys.argv[1:4]
o=heat(S+'published_old/index.html',key,A+'img/'+old,S+'published_old/img/'); n=heat(A+'index.html',key,A+'img/'+new,A+'img/')
s=Image.new('RGB',(1600,449)); s.paste(o,(0,0)); s.paste(n,(800,0)); s.save(S+'city2/heat_'+key.replace(':','_')+'.jpg',quality=85)
