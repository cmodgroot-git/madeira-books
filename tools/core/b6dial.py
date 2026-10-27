"""Repaint the thermometer dial faces in book 6 (p5: 3 °C, p8: 25 °C) with a clean Celsius scale."""
import math, sys, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
LO,HI,SWEEP=-10,40,270
def ang(t): return math.radians(225-(t-LO)/(HI-LO)*SWEEP)   # 225° (lower left) clockwise to -45°
def dial(src,out,cx,cy,rx,ry,temp,orig=None):
    a=np.asarray(Image.open(orig or src).convert('RGB')).copy(); H,W=a.shape[:2]
    face=np.zeros((H,W),np.uint8); cv2.ellipse(face,(cx,cy),(rx,ry),0,0,360,1,-1)
    L=a.astype(np.float32)@np.float32([.299,.587,.114]); med=np.median(L[face>0])
    ink=((L<med-38)&(face>0)).astype(np.uint8); ink=cv2.dilate(ink,np.ones((5,5),np.uint8))
    clean=cv2.inpaint(a,ink,9,cv2.INPAINT_TELEA)
    # smooth the inpaint a little inside the face so the old marks don't ghost through
    blur=cv2.GaussianBlur(clean,(0,0),2.2); f3=cv2.GaussianBlur(face.astype(np.float32),(0,0),1.5)[...,None]
    base=np.where(face[...,None]>0,(clean*.45+blur*.55),a).astype(np.float32)
    # draw the scale on a supersampled square, then squash to the face ellipse
    Z=4; R=min(rx,ry); N=int(2*R*Z); im=Image.new('L',(N,N),0); d=ImageDraw.Draw(im); c=N/2
    red=Image.new('L',(N,N),0); dr=ImageDraw.Draw(red)
    ro=R*Z*.90
    for t in range(LO,HI+1):
        th=ang(t); major=t%10==0; mid=t%5==0
        ri=ro-(R*Z*(.17 if major else .11 if mid else .065))
        d.line([(c+ro*math.cos(th),c-ro*math.sin(th)),(c+ri*math.cos(th),c-ri*math.sin(th))],fill=255,width=int(Z*(1.9 if major else 1.3 if mid else .9)))
    d.arc([c-ro,c-ro,c+ro,c+ro],start=-225,end=45,fill=255,width=int(Z*1.1))
    fs=int(R*Z*.165); fnt=ImageFont.truetype(FONT,fs)
    for t in range(LO,HI+1,10):
        th=ang(t); rn=ro-R*Z*.31; s=str(t).replace('-','−')
        d.text((c+rn*math.cos(th),c-rn*math.sin(th)),s,font=fnt,fill=255,anchor='mm')
    d.text((c,c+R*Z*.64),'°C',font=ImageFont.truetype(FONT,int(fs*.9)),fill=255,anchor='mm')
    th=ang(temp); tip=ro-R*Z*.04; tail=R*Z*.16; w=R*Z*.055
    px,py=math.cos(th),-math.sin(th); qx,qy=-py,px
    dr.polygon([(c+px*tip,c+py*tip),(c+qx*w,c+qy*w),(c-px*tail,c-py*tail),(c-qx*w,c-qy*w)],fill=255)
    pin=Image.new('L',(N,N),0); ImageDraw.Draw(pin).ellipse([c-R*Z*.075,c-R*Z*.075,c+R*Z*.075,c+R*Z*.075],fill=255)
    def place(m):
        m=np.asarray(m.resize((2*rx,2*ry),Image.LANCZOS),np.float32)/255; m=cv2.GaussianBlur(m,(0,0),.45)
        full=np.zeros((H,W),np.float32); full[cy-ry:cy+ry,cx-rx:cx+rx]=m; return full[...,None]*face[...,None]
    INK=np.float32([52,44,40]); RED=np.float32([196,38,30])
    o=base*(1-place(im)*.88)+INK*place(im)*.88
    o=o*(1-place(red))+RED*place(red)
    o=o*(1-place(pin))+np.float32([45,40,38])*place(pin)
    Image.fromarray(np.clip(o,0,255).astype(np.uint8)).save(out,quality=95)
if __name__=='__main__':
    p=int(sys.argv[1]); M=S+f'gen/masters/b6p{p}.jpg'; O=S+f'gen/masters/b6p{p}_orig.jpg'
    import os, shutil
    if not os.path.exists(O): shutil.copy(M,O)
    args={5:(308,358,53,68,3),8:(1076,131,90,99,25)}[p]
    dial(O,M,*args,orig=O)
