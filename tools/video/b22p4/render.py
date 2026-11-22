import cv2,numpy as np,pickle,glob
F=sorted(glob.glob('fr/*.png')); fr=[cv2.imread(f).astype(np.float32)/255 for f in F]; H,W=fr[0].shape[:2]; N=len(fr)
R={k:[a.astype(np.float32)/255 for a in v] for k,v in pickle.load(open('roto_final.pkl','rb')).items()}
names={'bola':'bola','cabeca':'cabeça','golo':'golo','rita':'Rita'}
def look(f,a,s):
    """s: highlight strength 0..1 (fades in/out). Subtle: gentle dim + desaturate outside, slight lift inside, soft warm rim."""
    g=f.mean(2,keepdims=True); out_=(f*0.725+g*0.275)*0.62         # outside: 20% darker, 30% less colour
    in_=np.clip((f-0.5)*1.06+0.5+0.03,0,1)                               # inside: a touch brighter
    A=cv2.GaussianBlur(a,(0,0),1.2)[...,None]
    o=in_*A+out_*(1-A)
    rim=np.clip(cv2.GaussianBlur(a,(0,0),7)-a,0,1)[...,None]*1.6   # soft halo just outside the edge
    o=o+rim*np.float32([0.78,0.93,1.0])*0.3                    # warm white (BGR)
    return f*(1-s)+o*s
from PIL import Image,ImageDraw,ImageFont
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',30)
def label(img,txt,alpha):
    im=Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB)); d=ImageDraw.Draw(im,'RGBA')
    d.text((28,H-58),txt,font=font,fill=(255,255,255,int(200*alpha)),stroke_width=2,stroke_fill=(0,0,0,int(90*alpha)))
    return cv2.cvtColor(np.array(im),cv2.COLOR_RGB2BGR)
vw=cv2.VideoWriter('demo_raw.mp4',cv2.VideoWriter_fourcc(*'mp4v'),24,(W,H))
for k in ['bola','cabeca','golo','rita']:
    for t in range(N):
        s=min(1,t/8,(N-1-t)/8+0.25); s=max(0,s)
        o=(np.clip(look(fr[t],R[k][t],s),0,1)*255).astype(np.uint8); vw.write(label(o,names[k],s))
vw.release()
# close-up check sheet: thin outline of the matte at 2x
rows=[]
for k in ['bola','cabeca','rita']:
    cells=[]
    for t in [0,24,48,72,95]:
        a=R[k][t]; ys,xs=np.nonzero(a>0.5); cx,cy=int(xs.mean()),int(ys.mean()); h=110 if k!='rita' else 150
        x0,y0=max(0,cx-h),max(0,cy-h); c=(fr[t][y0:y0+2*h,x0:x0+2*h]*255).astype(np.uint8).copy()
        cs,_=cv2.findContours((a[y0:y0+2*h,x0:x0+2*h]>0.5).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        c=cv2.resize(c,(440,440),interpolation=cv2.INTER_CUBIC); cs=[(x*440/(2*h)).astype(np.int32) for x in cs]
        cv2.drawContours(c,cs,-1,(0,255,255),1,cv2.LINE_AA); cv2.putText(c,f'{k} {t}',(8,24),0,0.7,(255,255,255),2); cells.append(c)
    rows.append(np.hstack(cells))
cv2.imwrite('roto_sheet.jpg',np.vstack(rows),[cv2.IMWRITE_JPEG_QUALITY,85])
