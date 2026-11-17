#!/usr/bin/env python3
"""Scene life for book 21: marina water (p1), moonlit sea and moon (p4), harbour water and the bulb (p8).
Frames are made by moving the painting's own pixels; packed as a 2-column sprite sheet with a
6 px gutter, shown through a nested <svg> window (discrete translate + crossfade to the next frame).
  life21.py build [page...] | preview  -> docs/img/b21p<N>_<stem>_sheet.webp and life18.json (svg snippets)"""
import os,sys,json,numpy as np,cv2
from PIL import Image
sys.path.insert(0,os.path.dirname(__file__)); import hlmask
DOC=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..','docs')); W,H=1600,898
GX,GY=np.meshgrid(np.arange(W,dtype=np.float32),np.arange(H,dtype=np.float32))
def ripple(B,mask,n=16,near=3.2,far=.35,lam_near=70.,lam_far=12.,shine=.05,edge=8):
    m=(mask>.3).astype(np.uint8); ys=np.nonzero(m)[0]; y0,y1=ys.min(),ys.max()
    t=np.clip((GY-y0)/max(1,y1-y0),0,1); amp=far+(near-far)*t**1.3; lam=lam_far+(lam_near-lam_far)*t
    col=np.clip((np.arange(H,dtype=np.float32)-y0)/max(1,y1-y0),0,1); lam_y=lam_far+(lam_near-lam_far)*col
    Phi=np.cumsum(2*np.pi/lam_y)[:,None].astype(np.float32)*np.ones((1,W),np.float32)
    fade=np.clip(cv2.distanceTransform(m,cv2.DIST_L2,5)/edge,0,1); amp=amp*fade; out=[]
    for i in range(n):
        s=i/n; p1=Phi+.6*np.sin(2*np.pi*GX/(3.1*lam))-2*np.pi*s; p2=.8*Phi+2*np.pi*GX/(2.3*lam)-4*np.pi*s
        dy=amp*(.65*np.sin(p1)+.35*np.sin(p2)); dx=amp*.45*np.cos(p2)
        f=cv2.remap(B,(GX+dx).astype(np.float32),(GY+dy).astype(np.float32),cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT)
        out.append(np.clip(f*(1+shine*fade[...,None]*(.4+.6*t[...,None])*np.sin(p1)[...,None]),0,255))
    return out
def sway(B,w,n=16,amp=2.5,lam=260.,gust=.35,vertical=.25):
    out=[]
    for i in range(n):
        s=i/n; g=np.sin(2*np.pi*(s-GX/lam))+gust*np.sin(2*np.pi*(2*s-GX/(lam*.45)+.3))
        out.append(cv2.remap(B,(GX-amp*w*g).astype(np.float32),(GY-amp*vertical*w*np.sin(2*np.pi*(s-GX/lam)+1.2)).astype(np.float32),cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT))
    return out
def region(i,key): return dict(hlmask.load(i))[key].astype(np.float32)
def pack(frames,alpha,i,stem,dur):
    ys,xs=np.nonzero(alpha>0.01); x0,y0,x1,y1=max(0,xs.min()-4),max(0,ys.min()-4),min(W,xs.max()+5),min(H,ys.max()+5)
    fw,fh=int(round((x1-x0)*.75)),int(round((y1-y0)*.75)); G=6; n=len(frames); rows=(n+1)//2
    sheet=Image.new('RGBA',(2*(fw+G),rows*(fh+G)),(0,0,0,0)); a=(np.clip(alpha[y0:y1,x0:x1],0,1)*255).astype(np.uint8)
    for k,f in enumerate(frames):
        im=Image.fromarray(np.dstack([np.clip(f[y0:y1,x0:x1],0,255).astype(np.uint8),a]),'RGBA').resize((fw,fh),Image.LANCZOS)
        sheet.paste(im,((k%2)*(fw+G),(k//2)*(fh+G)))
    name=f'img/b21p{i+1}_{stem}_sheet.webp'; sheet.save(os.path.join(DOC,name),quality=82,method=6)
    SW,SH=sheet.size; sx,sy=465.8/1600,260/898
    pos=[(-(k%2)*(fw+G),-(k//2)*(fh+G)) for k in range(n)]
    vals=';'.join(f'{x},{y}' for x,y in pos); vals2=';'.join(f'{x},{y}' for x,y in pos[1:]+pos[:1])
    kt=';'.join(f'{k/n:.4f}' for k in range(n))
    svg=(f'<svg x="{x0*sx:.2f}" y="{y0*sy:.2f}" width="{(x1-x0)*sx:.2f}" height="{(y1-y0)*sy:.2f}" viewBox="0 0 {fw} {fh}" preserveAspectRatio="none" overflow="hidden">'
         f'<image href="{name}" width="{SW}" height="{SH}"><animateTransform attributeName="transform" type="translate" calcMode="discrete" values="{vals}" keyTimes="{kt}" dur="{dur}s" repeatCount="indefinite"/></image>'
         f'<image href="{name}" width="{SW}" height="{SH}" opacity="0"><animateTransform attributeName="transform" type="translate" calcMode="discrete" values="{vals2}" keyTimes="{kt}" dur="{dur}s" repeatCount="indefinite"/>'
         f'<animate attributeName="opacity" values="0;1" dur="{dur/n:.4f}s" repeatCount="indefinite"/></image></svg>')
    print(name,sheet.size,os.path.getsize(os.path.join(DOC,name))//1024,'KB'); return svg
def layer(svgs): return '<g class="life">'+''.join(svgs)+'<rect class="beat" x="0" y="0" width="465.8" height="260" fill="#000" opacity=".002"><animate attributeName="opacity" values=".002;.003;.002" dur="10s" repeatCount="indefinite"/></rect></g><!--/life-->'
def breathe(B,g,n=16,amp=.12):
    out=[]
    for i in range(n):
        t=i/n; k=.5*(1-np.cos(2*np.pi*t))*.7+.3*.5*(1-np.cos(6*np.pi*t))   # a slow swell with a quicker flicker; whole cycles
        out.append(np.clip(B*(1+amp*k*g)[...,None],0,255))
    return out
def shift(B,dx,dy): return cv2.remap(B,GX-dx,GY-dy,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT)
def fall_scroll(B,n=24,P=70.0,direction=(0,1)):
    ux,uy=direction; L=(ux*ux+uy*uy)**.5; ux,uy=ux/L,uy/L; out=[]
    for i in range(n):
        ta=i/n; tb=(ta+.5)%1; wa=1-abs(2*ta-1); wb=1-abs(2*tb-1)
        out.append((wa*shift(B,ux*ta*P,uy*ta*P)+wb*shift(B,ux*tb*P,uy*tb*P))/(wa+wb))
    return out
def waterfall(B,m,n=24,P=240,seed=11):   # madeira-scene-life: streaks in the fall's own light colour
    m=(m>0).astype(np.uint8); ys,xs=np.nonzero(m); y0,y1=ys.min(),ys.max(); U=48
    noise=np.random.default_rng(seed).random((P,U)).astype(np.float32)
    tex=cv2.GaussianBlur(np.concatenate([noise]*3,0),(0,0),sigmaX=1.1,sigmaY=9)[P:2*P]; tex=(tex-tex.mean())/tex.std()
    span={y:(np.nonzero(m[y])[0].min(),np.nonzero(m[y])[0].max()+1) for y in range(y0,y1+1) if m[y].any()}
    col=np.percentile(B[m>0],85,axis=0); sm=np.clip(cv2.GaussianBlur(m.astype(np.float32),(0,0),1.3),0,1); out=[]
    for k in range(n):
        a=np.zeros((H,W),np.float32)
        for y,(xa,xb) in span.items():
            t=(y-y0)/max(1,y1-y0); v=(y-y0)*(1+.8*t)-k*P/n*(1+.6*t)
            a[y,xa:xb]=np.interp(np.linspace(0,U-1,xb-xa),np.arange(U),tex[int(np.floor(v))%P])
        a=np.clip(a*.5+.15,-.6,1.2)*sm; lt=np.clip(a,0,None)[...,None]*.55; dk=np.clip(-a,0,None)[...,None]*.18
        f=(B*(1-lt)+col*lt)*(1-dk)
        mist=np.zeros((H,W),np.float32); cv2.ellipse(mist,(int(xs[ys>y1-4].mean()),y1+4),(34,14),0,0,360,1.,-1); mist=cv2.GaussianBlur(mist,(0,0),7)
        pl=.28+.12*np.sin(4*np.pi*k/n); out.append(f*(1-mist[...,None]*pl)+np.float32([248,248,244])*mist[...,None]*pl)
    mist=np.zeros((H,W),np.float32); cv2.ellipse(mist,(int(xs[ys>y1-4].mean()),y1+4),(40,18),0,0,360,1.,-1)
    return out,np.clip(np.maximum(sm,cv2.GaussianBlur(mist,(0,0),7)*1.5),0,1)
def white(B,m,v=150,s=70):
    hsv=cv2.cvtColor(np.clip(B,0,255).astype(np.uint8),cv2.COLOR_RGB2HSV)
    w=((m>0)&(hsv[...,2]>v)&(hsv[...,1]<s)).astype(np.uint8); w=cv2.morphologyEx(w,cv2.MORPH_CLOSE,np.ones((9,5),np.uint8))
    n,lb,st,_=cv2.connectedComponentsWithStats(w); return np.isin(lb,[k for k in range(1,n) if st[k,4]>300]).astype(np.uint8)
def people(i,keys): 
    R=dict(hlmask.load(i)); m=np.zeros((H,W),np.uint8)
    for k in keys: m|=R[k].astype(np.uint8)
    return cv2.dilate(m,np.ones((15,15),np.uint8))
def pool_mask(m,minus,erode=5):
    m=cv2.erode((m>0).astype(np.uint8),np.ones((erode,erode),np.uint8)); m=m&(1-minus)
    return m.astype(np.float32)
def build(pages=None,preview=False):
    P=os.path.join(hlmask.WORK,'life21.json'); L={int(k):v for k,v in json.load(open(P)).items()} if os.path.exists(P) else {}
    want=lambda i: pages is None or i in pages
    def poly(pts): m=np.zeros((H,W),np.uint8); cv2.fillPoly(m,[np.array(pts,np.int32)],1); return m.astype(np.float32)
    # p1: the marina water moves (the people kept still)
    i=0
    if want(i):
        B=hlmask.master(i).astype(np.float32); m=cv2.erode(region(i,'porto').astype(np.uint8),np.ones((7,7),np.uint8)).astype(np.float32)
        L[i]=layer([pack(ripple(B,m,16,near=1.4,far=.5,lam_near=30.,lam_far=14.,shine=.05),np.clip(cv2.GaussianBlur(m,(0,0),2),0,1),i,'sea',8.0)])
    # p4: the moonlit sea moves and the moon glows
    i=3
    if want(i):
        B=hlmask.master(i).astype(np.float32); m=poly([(645,338),(1050,338),(1050,468),(1000,476),(830,448),(700,470),(650,425)])
        g=np.zeros((H,W),np.float32); cv2.circle(g,(887,85),70,1.,-1); g=cv2.GaussianBlur(g,(0,0),18)
        L[i]=layer([pack(ripple(B,m,16,near=1.8,far=.6,lam_near=34.,lam_far=14.,shine=.10),np.clip(cv2.GaussianBlur(m,(0,0),2),0,1),i,'sea',8.0),
                    pack(breathe(B,g,16,amp=.10),np.clip(g*1.4,0,1),i,'moon',7.0)])
    # p8: the harbour water in the window moves; the bulb breathes
    i=7
    if want(i):
        B=hlmask.master(i).astype(np.float32); m=poly([(1082,300),(1440,300),(1440,452),(1082,452)])
        g=np.zeros((H,W),np.float32); cv2.circle(g,(797,58),45,1.,-1); g=cv2.GaussianBlur(g,(0,0),12)
        L[i]=layer([pack(ripple(B,m,16,near=1.2,far=.5,lam_near=24.,lam_far=12.,shine=.10),np.clip(cv2.GaussianBlur(m,(0,0),2),0,1),i,'sea',8.0),
                    pack(breathe(B,g,16,amp=.08),np.clip(g*1.4,0,1),i,'bulb',6.0)])
    if not preview: json.dump(L,open(P,'w'))
    return L
if __name__=='__main__':
    a=sys.argv[1:]; pv='preview' in a; pg=[int(x)-1 for x in a if x.isdigit()] or None
    build(pg,pv)
