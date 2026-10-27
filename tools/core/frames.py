import json, os, re, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'
A=S+'artifact-files/87e1712e-5e90-4175-b828-2581544915d4/'; I=A+'img/'; M=S+'gen/masters/'
W,H=1600,898; K=W/1200
def load(name): return np.asarray(Image.open(M+name).convert('RGB'),np.float32)
def rgb(p): return np.asarray(Image.open(p).convert('RGB').resize((W,H),Image.LANCZOS),np.float32)
def poly_mask(polys,scale=K):
    m=Image.new('L',(W,H),0); d=ImageDraw.Draw(m)
    for q in polys: d.polygon([(x*scale,y*scale) for x,y in q],fill=255)
    return np.asarray(m)>0
def soften(m,grow=3,blur=1.5):
    im=Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.MedianFilter(5)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(grow))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(blur)),np.float32)/255
def lum(B): return B@np.float32([.299,.587,.114])
def sat(B): return B.max(2)-B.min(2)
DIS=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
G8=lambda a:cv2.cvtColor(np.clip(a,0,255).astype(np.uint8),cv2.COLOR_RGB2GRAY)
def flow(a,b): return DIS.calc(G8(a),G8(b),None)
GX,GY=np.meshgrid(np.arange(W,dtype=np.float32),np.arange(H,dtype=np.float32))
def warp(im,f,s): return cv2.remap(im,GX-s*f[...,0],GY-s*f[...,1],cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT)
def morph(a,b,s,fab=None,fba=None):
    fab=flow(a,b) if fab is None else fab; fba=flow(b,a) if fba is None else fba
    return (1-s)*warp(a,fab,s)+s*warp(b,fba,1-s)
def cycle(keys,steps):
    out=[]
    for i in range(len(keys)):
        a,b=keys[i],keys[(i+1)%len(keys)]; fab,fba=flow(a,b),flow(b,a)
        out+=[morph(a,b,j/steps,fab,fba) for j in range(steps)]
    return out
def water_cycle(B,variants,amp=.45,steps=7): return cycle([B]+[morph(B,v,amp) for v in variants],steps)
def shift(B,dx,dy): return cv2.remap(B,GX-dx,GY-dy,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT)
def fall_scroll(B,n=24,P=70.0,direction=(0,1)):
    ux,uy=direction; L=(ux*ux+uy*uy)**.5; ux,uy=ux/L,uy/L; out=[]
    for i in range(n):
        ta=i/n; tb=(ta+.5)%1; wa=1-abs(2*ta-1); wb=1-abs(2*tb-1)
        out.append((wa*shift(B,ux*ta*P,uy*ta*P)+wb*shift(B,ux*tb*P,uy*tb*P))/(wa+wb))
    return out
def breathe(B,g,n=16,amp=.08):
    return [B*(1+amp*0.5*(1-np.cos(2*np.pi*i/n))*g)[...,None] for i in range(n)]
def twinkle(B,dots,n=24,amp=.45,r=5,seed=7):
    rng=np.random.default_rng(seed); out=[]
    ph=rng.uniform(0,1,len(dots)); spd=rng.integers(1,3,len(dots))
    for i in range(n):
        gain=np.zeros((H,W),np.float32)
        for (x,y),p,s in zip(dots,ph,spd):
            cv2.circle(gain,(int(x*K),int(y*K)),r,float(amp*0.5*(1-np.cos(2*np.pi*(s*i/n+p)))),-1)
        gain=cv2.GaussianBlur(gain,(0,0),r*.6); out.append(B*(1+gain[...,None]))
    return out
def save(frames,mask,base,name):
    ys,xs=np.nonzero(mask>.01)
    if len(xs)<50: return None,None
    x0,y0,x1,y1=xs.min(),ys.min(),xs.max()+1,ys.max()+1
    a=(mask[y0:y1,x0:x1]*255).astype(np.uint8); w,h=max(1,int((x1-x0)*.75)),max(1,int((y1-y0)*.75)); paths=[]
    for f in os.listdir(I):
        if re.match(rf'{base}_{name}\d\d\.webp$',f): os.remove(I+f)
    for i,f in enumerate(frames):
        p=f'{base}_{name}{i:02d}.webp'
        Image.fromarray(np.dstack([np.clip(f[y0:y1,x0:x1],0,255).astype(np.uint8),a]),'RGBA').resize((w,h),Image.LANCZOS).save(I+p,quality=78,method=6)
        paths.append('img/'+p)
    return paths,(int(x0),int(y0),int(x1-x0),int(y1-y0))
def loop(srcs,box,dur):
    if not srcs: return ''
    n=len(srcs); sx,sy=465.8/1600,260/898; x,y,w,h=box[0]*sx,box[1]*sy,box[2]*sx,box[3]*sy
    img=lambda s,extra='':f'<image href="{s}" x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" preserveAspectRatio="none"{extra}'
    e=.0005; cut=(n-1)/n; out=img(srcs[0])+'/>'
    for i in range(1,n):
        a,b=(i-1)/n,i/n
        p=[(0,0),(a,0),(b,1),(cut+e,1),(cut+2*e,0),(1,0)] if i<n-1 else [(0,0),(a,0),(b,1),(1,0)]
        out+=img(srcs[i],' opacity="0"')+(f'><animate attributeName="opacity" values="{";".join(f"{v:g}" for _,v in p)}" '
               f'keyTimes="{";".join(f"{t:.4f}" for t,_ in p)}" dur="{dur}s" repeatCount="indefinite"/></image>')
    return out
def insert(index_html,key,layer):
    lines=open(index_html).read().split('\n')
    i=[n for n,l in enumerate(lines) if re.match(r"^(?:const PHOTOS=\{)?'"+re.escape(key)+"':",l)]
    assert len(i)==1,key; l=lines[i[0]]
    l=re.sub(r'<g class="life">.*?</g><!--/life-->','',l)
    m=re.search(r'(<image id="[^"]+ph"[^>]*/>)',l); assert m
    beat=('<rect class="beat" x="0" y="0" width="465.8" height="260" fill="#000" opacity=".002">'
          '<animate attributeName="opacity" values=".002;.003;.002" dur="10s" repeatCount="indefinite"/></rect>')
    l=l[:m.end()]+f'<g class="life">{layer}{beat}</g><!--/life-->'+l[m.end():]
    lines[i[0]]=l; open(index_html,'w').write('\n'.join(lines))

# ---------- ripple: travelling surface waves, strong near the viewer, calm toward the horizon ----------
def ripple(B,mask,n=16,near=3.2,far=0.35,lam_near=70.,lam_far=12.,shine=.05,edge=8):
    m=(mask>0.3).astype(np.uint8); ys=np.nonzero(m)[0]
    if len(ys)==0: return [B.copy() for _ in range(n)]
    y0,y1=ys.min(),ys.max(); t=np.clip((GY-y0)/max(1,y1-y0),0,1)
    amp=far+(near-far)*t**1.3; lam=lam_far+(lam_near-lam_far)*t
    col=np.clip((np.arange(H,dtype=np.float32)-y0)/max(1,y1-y0),0,1); lam_y=lam_far+(lam_near-lam_far)*col
    Phi=np.cumsum(2*np.pi/lam_y)[:,None].astype(np.float32)*np.ones((1,W),np.float32)
    dt=cv2.distanceTransform(m,cv2.DIST_L2,5); fade=np.clip(dt/edge,0,1); amp=amp*fade
    out=[]
    for i in range(n):
        s=i/n
        p1=Phi+0.6*np.sin(2*np.pi*GX/(3.1*lam))-2*np.pi*s
        p2=0.8*Phi+2*np.pi*GX/(2.3*lam)-2*np.pi*2*s
        dy=amp*(0.65*np.sin(p1)+0.35*np.sin(p2)); dx=amp*0.45*np.cos(p2)
        f=cv2.remap(B,(GX+dx).astype(np.float32),(GY+dy).astype(np.float32),cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT)
        if shine: f=f*(1+shine*fade[...,None]*(0.4+0.6*t[...,None])*np.sin(p1)[...,None])
        out.append(np.clip(f,0,255))
    return out

# ---------- sway: wind in leaves, hair, cloth; w = per-pixel strength (0..1), amp in master px ----------
def sway(B,w,n=16,amp=2.5,lam=260.,gust=.35,vertical=.25):
    out=[]
    for i in range(n):
        s=i/n
        g=np.sin(2*np.pi*(s-GX/lam))+gust*np.sin(2*np.pi*(2*s-GX/(lam*.45)+.3))
        dx=amp*w*g; dy=amp*vertical*w*np.sin(2*np.pi*(s-GX/lam)+1.2)
        out.append(cv2.remap(B,(GX-dx).astype(np.float32),(GY-dy).astype(np.float32),cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT))
    return out

# ---------- steam: soft white wisps rising and curling from (cx, cy), looping ----------
def steam(B,cx,cy,height=150,width=46,n=24,strands=3,alpha=.62,seed=3,lean=0.):
    rng=np.random.default_rng(seed); out=[]
    ph=[rng.uniform(0,1) for _ in range(strands)]; off=[(s-(strands-1)/2)*width*0.32 for s in range(strands)]
    for i in range(n):
        layer=np.zeros((H,W),np.float32)
        for s in range(strands):
            for k in range(70):
                u=(k/70+ i/n + ph[s])%1.0                       # 0 at cup, 1 at top
                yv=cy-u*height
                xv=cx+lean*u+off[s]*(1-u*.5)+np.sin(u*7.0+ph[s]*6.28+i/n*6.28)*width*0.32*u
                a=np.sin(np.pi*u)**1.4*(1-u*.35)
                r=2.2+5*u
                cv2.circle(layer,(int(xv),int(yv)),int(r),float(a),-1,lineType=cv2.LINE_AA)
        layer=cv2.GaussianBlur(layer,(0,0),3.5); layer=np.clip(layer,0,1)*alpha
        out.append(B*(1-layer[...,None])+np.float32([255,252,246])*layer[...,None])
    return out

# ---------- spill: wave water pouring over a rock wall into a pool, timed to the wave peak ----------
def _pulse(t,a,b,c,d):   # 0 before a, ramps to 1 by b, holds to c, falls to 0 by d (all in loop time, wraps)
    t=t%1; u=lambda x:(x-a)%1
    tt=u(t); B_,C_,D_=u(b),u(c),u(d)
    if tt<B_: v=tt/B_
    elif tt<C_: v=1
    elif tt<D_: v=1-(tt-C_)/(D_-C_)
    else: v=0
    return float(v*v*(3-2*v))
def spill(B,sea,pool,inlets,foam_box,intensity=.6,n=24,t_peak=0.,seed=5):
    """inlets: list of (x0,x1) master-px column ranges where water pours over the rocks.
    foam_box: (x0,y0,x1,y1) crop of painted white spray used as the foam texture.
    intensity: 0.3 calm, 0.6 normal, 1.0 storm (story weather)."""
    rng=np.random.default_rng(seed); out=[]
    fx0,fy0,fx1,fy1=foam_box; tex=B[fy0:fy1,fx0:fx1]
    tex=cv2.resize(tex,(W,int(H*1.0)),interpolation=cv2.INTER_CUBIC)
    tex=np.concatenate([tex,tex[::-1]],0)                     # seamless vertical tile
    wht=np.clip((lum(tex)-150)/80,0,1)                          # how white each texel is
    sea=sea.astype(bool); pool=pool.astype(bool)
    pour=np.zeros((H,W),np.float32); spots=[]
    for x0,x1 in inlets:
        w_=(x1-x0)*(.5+.5*intensity); xc=(x0+x1)/2; x0,x1=int(xc-w_/2),int(xc+w_/2)
        for x in range(max(0,x0),min(W,x1)):
            ys=np.nonzero(sea[:,x])[0]; yp=np.nonzero(pool[:,x])[0]
            if not len(ys) or not len(yp): continue
            edge=min(1,(x-x0)/25,(x1-x)/25)
            pour[ys.max()-12:yp.min()+10,x]=edge
        yp=np.nonzero(pool[:,int(xc)])[0]
        if len(yp): spots.append((xc,yp.min()+8,w_))
    streak=np.zeros(W,np.float32)
    for k in range(6): streak+=np.sin(GX[0]*(2*np.pi/rng.uniform(18,60))+rng.uniform(0,6.3))*rng.uniform(.3,1)
    streak=np.clip(.55+.25*streak/3,0,1)[None,:]
    pour=cv2.GaussianBlur(pour,(0,0),3)*streak
    for i in range(n):
        t=i/n; a_pour=_pulse(t,t_peak-.04,t_peak+.08,t_peak+.2,t_peak+.36)*min(1,.35+.65*intensity)
        sp=int((t*n)*18)%tex.shape[0]                           # foam scrolls down over the rocks
        T=np.roll(tex,sp,axis=0)[:H]; Wt=np.roll(wht,sp,axis=0)[:H]
        A=pour*a_pour*(.45+.55*Wt)
        foam=np.zeros((H,W),np.float32)
        for xc,yc,w_ in spots:                                  # foam spreading out into the pool
            age=((t-(t_peak+.06))%1); life=.55*(.6+.4*intensity)
            if age<life:
                r=w_*.35+age/life*w_*(.8+1.2*intensity); ry=r*.32
                d=((GX-xc)/r)**2+((GY-yc-ry*.6)/ry)**2
                ring=np.clip(1-d,0,1)**.7*(1-age/life)**1.3
                lace=np.clip((Wt-.25)*1.6,0,1)
                foam=np.maximum(foam,ring*lace*pool)
        A=np.clip(np.maximum(A,foam*min(1,.4+.6*intensity)),0,.92)[...,None]
        out.append(B*(1-A)+np.maximum(T,225)*A)
    return out, pour
