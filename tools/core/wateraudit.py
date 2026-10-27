import re, numpy as np, json
from PIL import Image, ImageDraw
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'; A=S+'artifact-files/87e1712e-5e90-4175-b828-2581544915d4/'; G=6
s=open(A+'index.html').read()
keys=re.findall(r"\n(?:const PHOTOS=\{)?'(\w+:\d+)':",s)
rows=[]; tiles=[]
for key in keys:
    i=s.find(f"'{key}':"); line=s[i:s.find('\n',i)]
    sid,pg=key.split(':'); img=re.search(r'id="%s%sph" href="img/([^"]+)"'%(sid,pg),line).group(1)
    B=np.asarray(Image.open(A+'img/'+img).convert('RGB').resize((800,449)),np.float32); hmax=np.zeros((449,800),np.float32); any_=False
    for m in re.finditer(r'<svg x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)" viewBox="0 0 (\d+) (\d+)"[^>]*><image href="img/([^"]+)_sheet\.webp" width="(\d+)" height="(\d+)"(.*?)</svg>',line,re.S):
        stem=m.group(7); kind=stem.split('_')[-1]
        x,y,w,h=[float(v) for v in m.groups()[:4]]; fw,fh=int(m.group(5)),int(m.group(6)); sw,sh=int(m.group(8)),int(m.group(9))
        dur=re.search(r'dur="([\d.]+)s"',m.group(10)); dur=float(dur.group(1)) if dur else None
        sheet=Image.open(A+f'img/{stem}_sheet.webp').convert('RGBA'); cols,rows_=sw//(fw+G),sh//(fh+G)
        sx,sy=800/465.8,449/260; X,Y,Wd,Hd=int(x*sx),int(y*sy),max(1,int(w*sx)),max(1,int(h*sy))
        fr=[]
        for r in range(rows_):
            for c in range(cols):
                f=np.asarray(sheet.crop((c*(fw+G),r*(fh+G),c*(fw+G)+fw,r*(fh+G)+fh)).resize((Wd,Hd)),np.float32)
                if f[...,3].max()==0: continue
                a=f[...,3:]/255; bb=B[Y:Y+Hd,X:X+Wd]; f=f[:bb.shape[0],:bb.shape[1]]; a=a[:bb.shape[0],:bb.shape[1]]
                fr.append((f[...,:3]*a+bb*(1-a)).mean(2))
        if len(fr)<2: continue
        st=np.stack(fr); steps=[np.abs(st[k+1]-st[k]).mean() for k in range(len(st)-1)]; seam=np.abs(st[0]-st[-1]).mean()
        d=st.max(0)-st.min(0); hmax[Y:Y+d.shape[0],X:X+d.shape[1]]=np.maximum(hmax[Y:Y+d.shape[0],X:X+d.shape[1]],d); any_=True
        rows.append(dict(key=key,stem=stem,frames=len(fr),dur=dur,step=round(float(np.mean(steps)),2),seam=round(float(seam),2),seamratio=round(float(seam/max(np.mean(steps),1e-3)),2),stepcv=round(float(np.std(steps)/max(np.mean(steps),1e-3)),2)))
    if any_:
        g=Image.fromarray(B.mean(2).astype(np.uint8)).convert('RGB').resize((400,224)); hm=Image.fromarray(np.clip(hmax*5,0,255).astype(np.uint8)).convert('RGB').resize((400,224))
        t=Image.blend(g,hm,.75); ImageDraw.Draw(t).text((4,4),key,fill=(255,255,0)); tiles.append(t)
json.dump(rows,open(S+'city2/audit.json','w'),indent=0)
for k in range(0,len(tiles),20):
    sh=Image.new('RGB',(2000,224*4))
    for j,t in enumerate(tiles[k:k+20]): sh.paste(t,((j%5)*400,(j//5)*224))
    sh.save(S+f'city2/audit{k//20}.jpg',quality=80)
print(len(rows),'layers',len(tiles),'pages')
