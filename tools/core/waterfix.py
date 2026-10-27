import re, sys, glob, os, pickle, numpy as np, cv2
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'; sys.path.insert(0,S)
import frames as F, windfx, hlmask
from PIL import Image
A=S+'artifact-files/87e1712e-5e90-4175-b828-2581544915d4/'; G=6; W,H=1600,898; SX=1600/465.8; SY=898/260
def page(key):
    s=open(A+'index.html').read(); i=s.find(f"'{key}':"); line=s[i:s.find('\n',i)]; sid,pg=key.split(':')
    img=re.search(r'id="%s%sph" href="img/([^"]+)"'%(sid,pg),line).group(1); return line,img
def sheets(key):
    line,_=page(key)
    for m in re.finditer(r'<svg x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)" viewBox="0 0 (\d+) (\d+)"[^>]*><image href="img/([^"]+)_sheet\.webp" width="(\d+)" height="(\d+)"',line):
        x,y,w,h=[float(v) for v in m.groups()[:4]]
        yield (int(round(x*SX)),int(round(y*SY)),int(round(w*SX)),int(round(h*SY))),int(m.group(5)),int(m.group(6)),m.group(7),int(m.group(8)),int(m.group(9))
def edit(stem,fw,fh,sw,sh,fn):
    arr=np.asarray(Image.open(A+f'img/{stem}_sheet.webp').convert('RGBA'),np.float32).copy()
    for r in range(sh//(fh+G)):
        for c in range(sw//(fw+G)):
            f=arr[r*(fh+G):r*(fh+G)+fh,c*(fw+G):c*(fw+G)+fw]; f[...,3]=fn(f[...,3])
    Image.fromarray(np.clip(arr,0,255).astype(np.uint8),'RGBA').save(A+f'img/{stem}_sheet.webp',quality=80,method=6)
def master(img):
    for n in (S+'gen/masters/'+img, A+'img/'+img):
        if os.path.exists(n): return np.asarray(Image.open(n).convert('RGB').resize((W,H)))
P=None
def people(img,boxes):
    global P
    if P is None: P=hlmask.predictor()
    P.set_image(master(img)); m=np.zeros((H,W),np.uint8)
    for b in boxes:
        cx,cy=(b[0]+b[2])/2,(b[1]+b[3])/2
        ms,sc,_=P.predict(point_coords=np.array([[cx,cy],[cx,b[1]+(b[3]-b[1])*.25]],float),point_labels=np.array([1,1]),box=np.array(b,float),multimask_output=True)
        m|=ms[int(np.argmax([x.sum() for x in ms]))].astype(np.uint8)
    m=cv2.dilate(m,np.ones((15,15),np.uint8)).astype(np.float32); return np.clip(cv2.GaussianBlur(m,(0,0),3)*1.5,0,1)
def hold(key,boxes,skip=()):
    _,img=page(key); p=people(img,boxes); Image.fromarray((p*255).astype(np.uint8)).resize((800,449)).save(S+f'city2/ppl_{key.replace(":","_")}.png')
    for (bx,by,bw,bh),fw,fh,stem,sw,sh in sheets(key):
        if any(k in stem for k in skip): continue
        keep=1-cv2.resize(p[by:by+bh,bx:bx+bw],(fw,fh))
        if keep.min()>.99: continue
        edit(stem,fw,fh,sw,sh,lambda a,k=keep: a*k); print(key,stem,'people held still')
def feather(key,suffixes,px=22):
    for (bx,by,bw,bh),fw,fh,stem,sw,sh in sheets(key):
        if not any(stem.endswith(s) for s in suffixes): continue
        a0=np.asarray(Image.open(A+f'img/{stem}_sheet.webp').convert('RGBA'))[0:fh,0:fw,3]
        inside=(a0>8).astype(np.uint8); inside[0,:]=inside[-1,:]=inside[:,0]=inside[:,-1]=0
        r=np.clip(cv2.distanceTransform(inside,cv2.DIST_L2,5)/px,0,1); r=r*r*(3-2*r)
        edit(stem,fw,fh,sw,sh,lambda a,r=r: a*r); print(key,stem,'feathered')
def sea_rebuild(key,stem,area,extra_sub=None,near=2.4):
    _,img=page(key); B=master(img).astype(np.float32)
    r,g,b=B[...,0],B[...,1],B[...,2]; L=F.lum(B)
    m=((b>r+8)&(L>55)&(L<235)).astype(np.uint8)&area
    bright=((L>215)&(F.sat(B)<30)).astype(np.uint8)                   # ships, yachts, white buildings stay still
    m&=1-cv2.dilate(bright,np.ones((9,9),np.uint8))
    if extra_sub is not None: m&=1-extra_sub
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8)); n,lb,st,_=cv2.connectedComponentsWithStats(m)
    m=np.isin(lb,[k for k in range(1,n) if st[k,4]>400]).astype(np.float32); m=np.clip(cv2.GaussianBlur(m,(0,0),1.3),0,1)
    fr=F.ripple(B,m,n=16,near=near); pa,box=F.save(fr,m,img[:4],'ls'); windfx.add_layer(key,F.loop(pa,box,6.0),stem); print(key,stem,'sea rebuilt',box)
def rect(x0,y0,x1,y1): m=np.zeros((H,W),np.uint8); m[y0:y1,x0:x1]=1; return m
job=sys.argv[1]
if job=='sea':
    f=sorted(glob.glob(S+'gen/hlcache/manha_1_*.pkl'),key=os.path.getmtime)[-1]; R={k:v for k,v in pickle.load(open(f,'rb'))[1]}
    nav=cv2.dilate(R['navio'].astype(np.uint8),np.ones((15,15),np.uint8))
    sea_rebuild('manha:1','b1p2_ls',(R['mar']>0).astype(np.uint8),nav)
    sea_rebuild('manha:3','b1p4_ls',rect(330,230,760,420),near=1.6)
if job=='people':
    hold('jantar:7',[[200,230,640,898],[700,0,1010,898],[1000,220,1400,898]],skip=('lg',))
    hold('jantar:6',[[180,0,880,898],[860,0,1560,898]],skip=('lg',))
    hold('sabado:3',[[470,230,770,898],[860,230,1160,898],[1120,440,1460,898]])
    hold('sabado:4',[[840,90,1060,700],[1030,90,1270,700],[1060,480,1300,700]])
    hold('sabado:5',[[430,0,760,898],[740,0,1090,898],[700,560,900,898]])
    hold('sabado:6',[[300,100,620,898],[580,100,920,898],[1060,550,1300,800]])
    hold('manha:3',[[680,0,1300,898]],skip=('ls',))
if job=='foliage':
    for k in ['domingo:1','domingo:2','domingo:3','domingo:4','domingo:6']: feather(k,('_lb',))
