#!/usr/bin/env python3
"""Scene life for book 16: pond ripples (p5), bay shimmer (p6), flag flutter (p7).
Frames are made by moving the painting's own pixels; packed as a 2-column sprite sheet with a
6 px gutter, shown through a nested <svg> window (discrete translate + crossfade to the next frame).
  life16.py build   -> docs/img/b16p<N>_<stem>_sheet.webp and life16.json (svg snippets)"""
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
    name=f'img/b16p{i+1}_{stem}_sheet.webp'; sheet.save(os.path.join(DOC,name),quality=82,method=6)
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
def build():
    L={}
    # p5: the pond, calm ripples (ducks and people already cut out of the region)
    i=4; B=hlmask.master(i).astype(np.float32); m=region(i,'lago')
    inner=np.zeros((H,W),np.float32); cv2.ellipse(inner,(738,680),(540,94),0,0,360,1.,-1); m=m*inner   # water inside the stone rim
    m=cv2.erode(m,np.ones((5,5),np.uint8)); fr=ripple(B,m,16,near=2.4,far=1.0,lam_near=60,lam_far=30,shine=.04)
    L[i]=layer([pack(fr,cv2.GaussianBlur(m,(0,0),1.5),i,'pond',6.0)])
    # p6: the bay, a slow shimmer
    i=5; B=hlmask.master(i).astype(np.float32); m=region(i,'baia'); m=cv2.erode(m,np.ones((5,5),np.uint8))
    fr=ripple(B,m,24,near=1.2,far=.5,lam_near=24,lam_far=10,shine=.07); L[i]=layer([pack(fr,cv2.GaussianBlur(m,(0,0),1.2),i,'bay',5.0)])
    # p7: the flag, cloth only; weight 0 at the pole rising to 1 at the free edge
    i=6; B=hlmask.master(i).astype(np.float32); m=region(i,'bandeira'); cloth=m*(GX>752)*(GY<640)
    cloth=cv2.erode(cloth,np.ones((3,3),np.uint8)); w=np.clip((GX-752)/55,0,1)*cloth
    w=cv2.GaussianBlur(w,(0,0),2); fr=sway(B,w,16,amp=4.0,lam=75,gust=.5,vertical=.6)
    a=cv2.GaussianBlur(cv2.dilate(cloth,np.ones((9,9),np.uint8)),(0,0),1.2)
    L[i]=layer([pack(fr,a,i,'flag',1.5)])
    json.dump(L,open(os.path.join(hlmask.WORK,'life16.json'),'w'))
    # motion map check: max change between frames
    return L
if __name__=='__main__': build()
