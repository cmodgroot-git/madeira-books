import re, json, numpy as np
from PIL import Image, ImageDraw
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'
A=S+'artifact-files/87e1712e-5e90-4175-b828-2581544915d4/'
h=open(A+'index.html').read()
pat=re.compile(r'<svg x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)" viewBox="0 0 (\d+) (\d+)"[^>]*><image href="img/(\w+?)_sheet\.webp" width="(\d+)" height="(\d+)"><animateTransform[^>]*values="([^"]+)"[^>]*dur="([\d.]+)s"')
rows=[]; tiles=[]
for key in re.findall(r"\n(?:const PHOTOS=\{)?'(\w+:\d+)':",h):
    i=h.find(f"'{key}':"); line=h[i:h.find('\n',i)]
    img=re.search(r'<image id="\w+ph" href="img/([^"]+)"',line).group(1)
    base=np.asarray(Image.open(A+'img/'+img).convert('RGB').resize((1200,674)),np.float32)
    for m in pat.finditer(line):
        x,y,w,hh=[float(v) for v in m.groups()[:4]]; fw,fh=int(m.group(5)),int(m.group(6)); stem=m.group(7); dur=float(m.group(11))
        kind=stem.split('_')[1].rstrip('0123456789')
        if kind in ('lg','lt'): continue
        offs=[tuple(map(int,v.split(','))) for v in m.group(10).split(';')]
        sheet=Image.open(A+f'img/{stem}_sheet.webp').convert('RGBA')
        X0,Y0=round(x*1200/465.8),round(y*674/260); sz=(max(1,round(w*1200/465.8)),max(1,round(hh*674/260)))
        frames=[]
        for ox,oy in offs:
            fr=sheet.crop((-ox,-oy,-ox+fw,-oy+fh)).resize(sz,Image.BILINEAR); a=np.asarray(fr,np.float32)
            b=base[Y0:Y0+sz[1],X0:X0+sz[0]].copy(); al=a[...,3:4]/255
            b[:a.shape[0],:a.shape[1]]=a[...,:3]*al+b[:a.shape[0],:a.shape[1]]*(1-al); frames.append(b)
        n=len(frames)
        step=[np.abs(frames[(k+1)%n]-frames[k]).mean() for k in range(n)]
        span=np.abs(frames[n//2]-frames[0]).max(2)
        rows.append(dict(key=key,layer=stem,kind=kind,n=n,dur=dur,step_mean=round(float(np.mean(step)),2),step_max=round(float(np.max(step)),2),loop_jump=round(float(step[-1]),2),moving=round(float((span>12).mean()),3),box=[X0,Y0,sz[0],sz[1]]))
        # tile: frame0 | frame n/2 | motion heat
        def im(a): return Image.fromarray(np.clip(a,0,255).astype(np.uint8))
        heat=np.clip(span*4,0,255); hm=np.stack([heat,heat*0.2,heat*0.2],-1)*0.8+frames[0]*0.35
        t=Image.new('RGB',(3*300,200),'black')
        for j,a in enumerate([frames[0],frames[n//3],hm]):
            q=im(a); q.thumbnail((300,180)); t.paste(q,(j*300,20))
        ImageDraw.Draw(t).text((4,3),f"{key} {stem} {n}f {dur}s step {rows[-1]['step_mean']} max {rows[-1]['step_max']} loop {rows[-1]['loop_jump']}",fill=(255,255,0))
        tiles.append(t)
json.dump(rows,open(S+'conv/critique.json','w'),indent=0)
for s in range(0,len(tiles),10):
    sh=Image.new('RGB',(900,200*min(10,len(tiles)-s)))
    for j,t in enumerate(tiles[s:s+10]): sh.paste(t,(0,j*200))
    sh.save(S+f'conv/crit_{s//10}.jpg',quality=82)
print(len(tiles))
for r in rows: print(r)
