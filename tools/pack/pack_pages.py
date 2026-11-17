#!/usr/bin/env python3
"""Pack each book's page pictures into one stacked JPEG (docs/img/pages/<book>.<hash>.jpg) to stay under the artifact's
511-file limit. Rewrites every photos/<id>.<hash>.js that still points at single page JPEGs:
  <image id="Xph" href="img/bNpK.jpg" .../>  ->  <svg id="Xph" ... viewBox="0 Y 1200 674"><image href="img/pages/…" width="1200" height="H"/></svg>
and updates PHF in docs/index.html. Idempotent; run after every book build (before publishing).
Prints the files to publish and the files to remove (old photos js, single page JPEGs no longer used by any photos js)."""
import re,glob,os,io,json,hashlib,sys
from PIL import Image
DOC=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','docs'); DOC=os.path.abspath(DOC)
PAT=re.compile(r'<image id="([^"]+ph)" href="(img/[^"]+\.jpg)" x="0" y="0" width="465\.8" height="260" preserveAspectRatio="none"/>')
def h10(b): return hashlib.sha1(b).hexdigest()[:10]
H=open(f'{DOC}/index.html',encoding='utf8').read(); i=H.index('PHF=')+4; PHF,e=json.JSONDecoder().raw_decode(H,i)
os.makedirs(f'{DOC}/img/pages',exist_ok=True)
publish=[];remove=[];atlases={}
for sid,rel in sorted(PHF.items()):
    t=open(f'{DOC}/{rel}',encoding='utf8').read(); m=PAT.findall(t)
    if not m: continue
    hrefs=[]; [hrefs.append(h) for _,h in m if h not in hrefs]
    key=tuple(hrefs)
    if key not in atlases:
        ims=[Image.open(f'{DOC}/{h}').convert('RGB') for h in hrefs]; assert all(im.size==(1200,674) for im in ims),sid
        A=Image.new('RGB',(1200,674*len(ims)));[A.paste(im,(0,674*k)) for k,im in enumerate(ims)]
        b=io.BytesIO(); A.save(b,'JPEG',quality=88,optimize=True,progressive=True); data=b.getvalue()
        stem=re.match(r'img/(b\d+)p',hrefs[0]).group(1); name=f'img/pages/{stem}.{h10(data)}.jpg'
        if not os.path.exists(f'{DOC}/{name}'): open(f'{DOC}/{name}','wb').write(data); publish.append(name)
        atlases[key]=name
    name=atlases[key]; N=len(hrefs)
    def rep(mm):
        k=hrefs.index(mm.group(2))
        return (f'<svg id="{mm.group(1)}" x="0" y="0" width="465.8" height="260" viewBox="0 {k*674} 1200 674" preserveAspectRatio="none" overflow="hidden">'
                f'<image href="{name}" width="1200" height="{N*674}"/></svg>')
    t2=PAT.sub(rep,t); b=t2.encode('utf8'); new=f'photos/{sid}.{h10(b)}.js'
    open(f'{DOC}/{new}','wb').write(b); remove.append(rel); publish.append(new); PHF[sid]=new
    os.remove(f'{DOC}/{rel}')
H=H[:i]+json.dumps(PHF,ensure_ascii=False)+H[e:]; open(f'{DOC}/index.html','w',encoding='utf8').write(H)
# single page JPEGs that no photos js uses any more
used=set()
for rel in PHF.values(): used|=set(re.findall(r'href="(img/[^"]+\.jpg)"',open(f'{DOC}/{rel}',encoding='utf8').read()))
for f in glob.glob(f'{DOC}/img/b*p*.jpg'):
    r=os.path.relpath(f,DOC)
    if r not in used: remove.append(r); os.remove(f)
json.dump({'publish':publish,'remove':remove},open('/tmp/pack_plan.json','w'),indent=0)
print('atlases',len(atlases),'publish',len(publish),'remove',len(remove))
