import re,sys
from PIL import Image, ImageDraw
A='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4/'
h=open(A+'index.html').read()
story=sys.argv[1]; out=sys.argv[2]
tiles=[]
for idx in range(9):
    i=h.find(f"'{story}:{idx}':"); 
    if i<0: continue
    s=h[i:h.find("\n",i)]
    img=re.search(r'href="(img/[^"]+\.jpg)"',s).group(1)
    clips=dict(re.findall(r'<clipPath id="(\w+)">(.*?)</clipPath>',s))
    im=Image.open(A+img).convert('RGB').resize((932,520)); d=ImageDraw.Draw(im); k=932/465.8
    cols=[(255,40,40),(40,220,40),(60,120,255),(255,200,0),(255,0,255),(0,230,230),(255,128,0),(160,80,255),(255,255,255)]
    for n,(keys,cid) in enumerate(re.findall(r"\$\{o\('([^']+)',`<use href=\"#\w+\" clip-path=\"url\(#(\w+)\)\"",s)):
        c=cols[n%len(cols)]
        for pts in re.findall(r'points="([^"]+)"',clips.get(cid,'')):
            P=[(float(a)*k,float(b)*k) for a,b in (t.split(',') for t in pts.split())]
            d.line(P+[P[0]],fill=c,width=3)
            d.text((P[0][0]+3,P[0][1]+3),keys,fill=c)
    for keys in re.findall(r"\$\{o\('([^']+)',`<g class=\"gaze",s): d.text((10,500),'gaze: '+keys,fill='yellow')
    d.text((8,8),f'{story}:{idx}',fill='yellow'); tiles.append(im)
S=Image.new('RGB',(932*2,520*((len(tiles)+1)//2)))
for i,t in enumerate(tiles): S.paste(t,((i%2)*932,(i//2)*520))
S.save(out,quality=80)
