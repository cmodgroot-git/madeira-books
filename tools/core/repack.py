import re, os, math, json
from PIL import Image
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'
A=S+'artifact-files/87e1712e-5e90-4175-b828-2581544915d4/'; I=A+'img/'
h=open(A+'index.html').read()
stems=sorted(set(re.findall(r'href="img/(\w+?)00\.webp"',h)))
removed=[]; made=[]
for st in stems:
    m=re.search(r'<image href="img/'+st+r'00\.webp" x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"[^>]*/>((?:<image href="img/'+st+r'\d\d\.webp".*?</image>)+)',h)
    if not m: print('skip',st); continue
    x,y,w,hh=m.group(1),m.group(2),m.group(3),m.group(4)
    dur=re.search(r'dur="([\d.]+)s"',m.group(5)).group(1)
    files=[st+'00.webp']+re.findall(r'href="img/('+st+r'\d\d\.webp)"',m.group(5))
    ims=[Image.open(I+f).convert('RGBA') for f in files]; fw,fh=ims[0].size; n=len(ims)
    cols=1
    while math.ceil(n/cols)*fh>15000 or cols*fw<math.ceil(n/cols)*fh/4: cols+=1
    cols=min(cols,n); rows=math.ceil(n/cols)
    while cols*fw>15000: cols-=1; rows=math.ceil(n/cols)
    sh=Image.new('RGBA',(cols*fw,rows*fh),(0,0,0,0))
    for k,im in enumerate(ims): sh.paste(im,((k%cols)*fw,(k//cols)*fh))
    sp=st+'_sheet.webp'; sh.save(I+sp,quality=80,method=6); made.append(sp)
    tr=lambda k:f"{-(k%cols)*fw},{-(k//cols)*fh}"
    kt=";".join(f"{i/n:.4f}" for i in range(n))
    va=";".join(tr(k) for k in range(n)); vb=";".join(tr((k+1)%n) for k in range(n))
    slot=float(dur)/n
    svg=(f'<svg x="{x}" y="{y}" width="{w}" height="{hh}" viewBox="0 0 {fw} {fh}" preserveAspectRatio="none" overflow="hidden">'
         f'<image href="img/{sp}" width="{cols*fw}" height="{rows*fh}"><animateTransform attributeName="transform" type="translate" calcMode="discrete" values="{va}" keyTimes="{kt}" dur="{dur}s" repeatCount="indefinite"/></image>'
         f'<image href="img/{sp}" width="{cols*fw}" height="{rows*fh}" opacity="0"><animateTransform attributeName="transform" type="translate" calcMode="discrete" values="{vb}" keyTimes="{kt}" dur="{dur}s" repeatCount="indefinite"/>'
         f'<animate attributeName="opacity" values="0;1" dur="{slot:.4f}s" repeatCount="indefinite"/></image></svg>')
    h=h[:m.start()]+svg+h[m.end():]
    for f in files: os.remove(I+f); removed.append(f)
open(A+'index.html','w').write(h)
json.dump({'made':made,'removed':removed},open(S+'gen/repack.json','w'))
print(len(made),'sheets',len(removed),'frames removed',sum(os.path.getsize(I+f) for f in made)//1024,'KB')
