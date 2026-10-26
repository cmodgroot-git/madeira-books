#!/usr/bin/env python3
"""Scene life for book 17: harbour sea shimmer (p6), candle flicker (p8).
Frames are made by moving the painting's own pixels; packed as a 2-column sprite sheet with a
6 px gutter, shown through a nested <svg> window (discrete translate + crossfade to the next frame).
  life17.py build   -> docs/img/b17p<N>_<stem>_sheet.webp and life17.json (svg snippets)"""
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
    name=f'img/b17p{i+1}_{stem}_sheet.webp'; sheet.save(os.path.join(DOC,name),quality=82,method=6)
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
def build():
    L={}
    # p6: the harbour sea behind the car pound, a slow shimmer (Rita's head and the cranes' piers kept still)
    i=5; B=hlmask.master(i).astype(np.float32); m=np.zeros((H,W),np.float32)
    cv2.fillPoly(m,[np.array([(0,226),(1600,226),(1600,279),(0,279)],np.int32)],1.)
    hsv=cv2.cvtColor(B.astype(np.uint8),cv2.COLOR_RGB2HSV); sea=((hsv[...,0]>=40)&(hsv[...,0]<=120)&(hsv[...,2]>=110)).astype(np.float32)
    band=m.copy(); m=cv2.morphologyEx(m*sea,cv2.MORPH_CLOSE,np.ones((9,25),np.uint8))*band; m[:, 455:690]=0
    for px in (447,705,1190,1247,1315,1362): m[:,px-9:px+10]=0
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    fr=ripple(B,m,24,near=1.0,far=.5,lam_near=18,lam_far=10,shine=.08); L[i]=layer([pack(fr,cv2.GaussianBlur(m,(0,0),1.2),i,'sea',5.0)])
    # p8: candle flames flicker softly
    i=7; B=hlmask.master(i).astype(np.float32); g=np.zeros((H,W),np.float32); cv2.ellipse(g,(905,612),(80,38),0,0,360,1.,-1); g=cv2.GaussianBlur(g,(0,0),18)
    fr=breathe(B,g,16,amp=.14); L[i]=layer([pack(fr,np.clip(g*1.6,0,1),i,'candles',1.6)])
    json.dump(L,open(os.path.join(hlmask.WORK,'life17.json'),'w'))
    return L
if __name__=='__main__': build()
