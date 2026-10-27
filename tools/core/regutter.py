"""Add a transparent gutter between frames in every sprite sheet so neighbouring frames never bleed in."""
import re, numpy as np
from PIL import Image
A='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4/'
G=6
h=open(A+'index.html').read(); done={}; changed=[]
pat=re.compile(r'<svg x="[\d.]+" y="[\d.]+" width="[\d.]+" height="[\d.]+" viewBox="0 0 (\d+) (\d+)"[^>]*>(.*?)</svg>',re.S)
def fix(m):
    fw,fh,inner=int(m.group(1)),int(m.group(2)),m.group(3)
    src=re.search(r'href="img/([^"]+)" width="(\d+)" height="(\d+)"',inner); name,sw,sh=src.group(1),int(src.group(2)),int(src.group(3))
    if sw%fw or sh%fh: return m.group(0)          # already guttered
    cols,rows=sw//fw,sh//fh
    if name not in done and Image.open(A+'img/'+name).size==(cols*(fw+G),rows*(fh+G)): done[name]=1
    if name not in done:
        im=Image.open(A+'img/'+name).convert('RGBA'); out=Image.new('RGBA',(cols*(fw+G),rows*(fh+G)),(0,0,0,0))
        for r in range(rows):
            for c in range(cols): out.paste(im.crop((c*fw,r*fh,(c+1)*fw,(r+1)*fh)),(c*(fw+G),r*(fh+G)))
        out.save(A+'img/'+name,quality=80,method=6); done[name]=1; changed.append(name)
    def tv(vals):
        res=[]
        for v in vals.split(';'):
            x,y=map(int,v.split(',')); c,r=-x//fw,-y//fh; res.append(f'{-c*(fw+G)},{-r*(fh+G)}')
        return ';'.join(res)
    inner=re.sub(r'width="%d" height="%d"'%(sw,sh),f'width="{cols*(fw+G)}" height="{rows*(fh+G)}"',inner)
    inner=re.sub(r'(type="translate" calcMode="discrete" values=")([^"]+)"',lambda q:q.group(1)+tv(q.group(2))+'"',inner)
    return m.group(0).replace(m.group(3),inner)
h2=pat.sub(fix,h); open(A+'index.html','w').write(h2); print(len(changed),'sheets guttered')
import json; json.dump(changed,open('/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/gen/guttered.json','w'))
