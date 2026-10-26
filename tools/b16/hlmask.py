#!/usr/bin/env python3
"""Cut book 16 tap regions with Segment Anything and build the page SVG entries.
  hlmask.py cut <page>     # one page per process (vit_h needs ~6 GB); caches masks
  hlmask.py sheet          # per-word review sheet
Paths: WORK (scratch) holds masters/ and hlcache/."""
import sys,os,io,base64,pickle,numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,os.path.dirname(__file__))
from hl_book16 import SPEC
WORK=os.environ.get('WORK','/tmp/claude-0/-home-user-madeira-books/11c1ecef-e1df-5fad-8f8e-68eb719ae5fc/scratchpad/b16')
SAMCK=os.path.join(os.path.dirname(WORK),'sam','vit_h.pth')
W,H=1600,898
def master(i): return np.array(Image.open(f'{WORK}/masters/b16p{i+1}.jpg').convert('RGB'))
_P=None
def predictor(img):
    global _P
    if _P is None:
        from segment_anything import sam_model_registry,SamPredictor
        _P=SamPredictor(sam_model_registry['vit_h'](checkpoint=SAMCK))
    _P.set_image(img); return _P
def sam_mask(P,box,pos=(),neg=(),pick='best'):
    pts=list(pos)+list(neg); lab=[1]*len(pos)+[0]*len(neg)
    ms,sc,_=P.predict(point_coords=np.array(pts,float) if pts else None,point_labels=np.array(lab) if pts else None,box=np.array(box,float),multimask_output=True)
    k=int(np.argmax([m.sum() for m in ms])) if pick=='big' else int(np.argmax(sc))
    m=ms[k].astype(np.uint8); n,lb,st,_=cv2.connectedComponentsWithStats(m)
    if n>2: m=np.isin(lb,[j for j in range(1,n) if st[j,4]>0.04*st[1:,4].max()]).astype(np.uint8)
    return m
def shape(P,s):
    m=np.zeros((H,W),np.uint8); t=s[0]
    if t=='sam': return sam_mask(P,*s[1:])
    if t=='rect': cv2.rectangle(m,(s[1],s[2]),(s[3],s[4]),1,-1)
    elif t=='ell': cv2.ellipse(m,(s[1],s[2]),(s[3],s[4]),0,0,360,1,-1)
    elif t=='poly': cv2.fillPoly(m,[np.array(s[1],np.int32)],1)
    return m
def region(P,shapes):
    plus=np.zeros((H,W),np.uint8); minus=plus.copy(); post=plus.copy()
    for s in shapes:
        if s[0]=='sub': minus|=cv2.dilate(shape(P,s[1]),np.ones((5,5),np.uint8))
        elif s[0]=='post': post|=shape(P,s[1])
        else: plus|=shape(P,s)
    m=(plus&(1-minus))|post
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8)); m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    return m
def cut(i):
    img=master(i); P=predictor(img); out=[]
    for keys,shapes in SPEC[i]:
        out.append((keys,region(P,shapes))); print(i,keys,int(out[-1][1].sum()),flush=True)
    os.makedirs(f'{WORK}/hlcache',exist_ok=True)
    pickle.dump(out,open(f'{WORK}/hlcache/golfe_{i}.pkl','wb'))
def load(i): return pickle.load(open(f'{WORK}/hlcache/golfe_{i}.pkl','rb'))
def sheet():
    f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',22); tiles=[]
    for i in SPEC:
        img=master(i).astype(np.float32)
        for keys,m in load(i):
            t=img*0.22; t[m>0]=img[m>0]
            t=t.astype(np.uint8); c,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); cv2.drawContours(t,c,-1,(255,40,40),2)
            im=Image.fromarray(t).resize((640,359)); ImageDraw.Draw(im).text((8,6),f'p{i+1} {keys}',font=f,fill=(255,255,0),stroke_width=2,stroke_fill=(0,0,0)); tiles.append(im)
    rows=(len(tiles)+3)//4; s=Image.new('RGB',(640*4,359*rows))
    for j,t in enumerate(tiles): s.paste(t,((j%4)*640,(j//4)*359))
    s.save(f'{WORK}/review_sheet.jpg',quality=82); print(len(tiles),'tiles')
def mask_png(m):
    ys,xs=np.nonzero(m); x0,y0,x1,y1=max(0,xs.min()-3),max(0,ys.min()-3),min(W,xs.max()+4),min(H,ys.max()+4)
    fl=cv2.GaussianBlur(m[y0:y1,x0:x1].astype(np.float32),(0,0),0.9)
    im=Image.fromarray((np.clip(fl,0,1)*255).astype(np.uint8)).resize((max(1,(x1-x0)//2),max(1,(y1-y0)//2)),Image.LANCZOS).quantize(16).convert('L')
    b=io.BytesIO(); im.save(b,'PNG',optimize=True); return base64.b64encode(b.getvalue()).decode(),(x0,y0,x1,y1),(xs.min(),ys.min(),xs.max(),ys.max())
if __name__=='__main__':
    c=sys.argv[1]
    if c=='cut': cut(int(sys.argv[2]))
    elif c=='sheet': sheet()
