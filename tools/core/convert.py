"""Convert every page's scene life to painted frames (frames.py). usage: convert.py [keys...]"""
import sys, re, json, numpy as np, cv2
sys.path.insert(0,'/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad')
import frames as F, life
from PIL import Image, ImageDraw, ImageFilter
S=F.S; A=F.A; K=F.K; W,H=F.W,F.H
src=open(S+'life_all.py').read()
blocks=dict(re.findall(r"\n '(\w+:\d+)': \('(b\dp\d)'",src))
blocks.update({'manha:2':'b1p3','manha:8':'b1p9'})
def block(key):
    i=src.find(f" '{key}':"); j=src.find("\n '",i+5); return src[i:j] if i>=0 else ''
STILL=json.load(open(S+'gen/still.json')); SURF=json.load(open(S+'gen/surf.json'))
DONE={'jantar:1','domingo:5'}
FAR={'manha:0','manha:1','manha:3','manha:4','manha:7','manha:8','sabado:0','sabado:1','sabado:2','sabado:7','domingo:7','jantar:0','jantar:2','jantar:5'}
LEVADA={'domingo:2':((355,324),40),'domingo:3':((352,202),64),'domingo:4':((-140,234),40)}
EXTRA={  # things the old inline builders had
 'manha:8':{'sea':[[(770,288),(830,262),(972,258),(972,372),(868,370),(805,348),(772,322)]],
            'glow':[(913,121,46),(400,300,90)],'tw':[((700,180,860,330),170,True,22,9)]},
 'manha:2':{'glow':[(330,230,200)]},
}
SEEDS={'jantar:6':[(220,330),(800,330),(1350,400),(1420,460)],'manha:7':[(1450,320),(1350,280),(1550,420)],'jantar:3': [(600, 220), (960, 240), (1300, 220), (1520, 400)], 'jantar:4': [(600, 210), (1000, 200), (1400, 340)], 'jantar:5': [(200, 360), (1400, 400), (900, 300)], 'jantar:2': [(1200, 380), (1500, 450), (1400, 560)], 'manha:1': [(1120, 464), (1400, 404), (1500, 324)]}
SEA={'jantar:6': [(98, 142), (968, 142), (968, 161), (1110, 188), (1110, 375), (98, 375)], 'manha:7': [(930, 159), (1200, 159), (1200, 394), (930, 248)], 'jantar:5': [(0, 210), (938, 210), (1012, 248), (1200, 248), (1200, 480), (0, 480)], 'jantar:3': [(330, 131), (1200, 131), (1200, 360), (750, 360), (330, 315)], 'jantar:2': [(750, 199), (1200, 199), (1200, 442), (938, 442), (938, 352), (750, 315)], 'manha:1': [(840, 248), (1200, 165), (1200, 420), (1088, 450), (975, 420), (900, 525), (750, 525), (660, 390), (712, 315)], 'jantar:4': [(150, 129), (1200, 124), (1200, 322), (750, 322), (150, 248)]}  # whole visible sea (old particle regions were patches)
SEA_HOLES={'manha:1':[(889, 315), (1046, 315), (1046, 428), (889, 428)]}
THR={'jantar:4':16,'jantar:5':18}
SEA_EXCL={'jantar:2':[[(518, 248), (788, 285), (1200, 315), (1200, 674), (518, 674)]],'jantar:3':[[(352, 112), (758, 112), (758, 674), (352, 674)]],'domingo:7':[[(0, 0), (1200, 0), (1200, 159), (0, 159)]],'jantar:6':[[(570, 300), (840, 300), (840, 420), (570, 420)]],'manha:1':[[(925,222),(1165,222),(1165,255),(925,255)],[(885,318),(1045,318),(1045,430),(885,430)],[(965,322),(1010,322),(1200,430),(1200,505),(1150,505)]]}
RAMP={'jantar:2':2.0}
NPYX={'sabado:3':'gen/still_b2p4_dog.npy'}
TW={'sabado:7':[((770,350,1110,480),170,True,26,10)],'jantar:7':[((560,0,1200,230),150,False,30,18)]}
VAR={k:[S+f'conv/var/{n}_a.png',S+f'conv/var/{n}_b.png'] for k,n in [('sabado:3','b2p4'),('sabado:4','b2p5'),('sabado:5','b2p6'),('sabado:6','b2p7')]}

def exclusion(key,img,people_only=False):
    m=Image.new('L',(W,H),0); d=ImageDraw.Draw(m)
    for q in life.people_polys(A+'index.html',key):
        d.polygon([(float(x)*1600/465.8,float(y)*898/260) for x,y in (t.split(',') for t in q.split())],fill=255)
    for q in ([] if people_only else STILL.get(img,[])): d.polygon([(x*K,y*K) for x,y in q],fill=255)
    return np.asarray(m.filter(ImageFilter.MaxFilter(11)),np.float32)/255
NIGHTK={'manha:8','sabado:7','jantar:7'}
def water_mask(B,polys,ex,key,foam_polys=(),EXP_=None):
    area=F.poly_mask(polys); R,G,Bc=B[...,0],B[...,1],B[...,2]
    R_,G_,B_=[cv2.GaussianBlur(c,(0,0),2) for c in (R,G,Bc)]
    L=F.lum(B); s=F.sat(B)
    lo=12 if key in NIGHTK else 85
    S_=cv2.GaussianBlur(s,(0,0),2); L_=cv2.GaussianBlur(L,(0,0),2)
    lo=12 if key in NIGHTK else 55
    blue=(B_-R_>-6)
    if key in SEA:                                    # whole-sea outline: keep pixels that look like this sea
        lab=cv2.cvtColor(cv2.GaussianBlur(B,(0,0),2).astype(np.uint8),cv2.COLOR_RGB2LAB).astype(np.float32)
        d=np.full(L.shape,1e9,np.float32)
        for sx,sy in SEEDS[key]:
            med=lab[sy-8:sy+8,sx-8:sx+8].reshape(-1,3).mean(0)
            d=np.minimum(d,np.sqrt(((lab[...,1:]-med[1:])**2).sum(-1)*4+((lab[...,0]-med[0])*.35)**2))
        blue=(d<THR.get(key,22)).astype(np.uint8)
        blue=cv2.morphologyEx(blue,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
        n_,lb=cv2.connectedComponents(blue&area.astype(np.uint8))
        keep={lb[sy,sx] for sx,sy in SEEDS[key]}-{0}
        blue=np.isin(lb,list(keep)); ex=EXP_
        if key in SEA_HOLES: area=area&~F.poly_mask([SEA_HOLES[key]])
    m=area&blue&(L_>lo)&~((L_>205)&(S_<22))
    if foam_polys: m|=F.poly_mask(foam_polys)&(L>170)&(s<60)
    m=m.astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((7,7),np.uint8))
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((15,15),np.uint8)).astype(bool)&area
    m=F.soften(m,3)
    return np.clip(m-ex*1.5,0,1)
def build(key):
    img=blocks[key]; b=block(key); B=F.load(img+'.jpg'); ex=exclusion(key,img); parts=[]; n=0
    polys=[eval(p) for p in re.findall(r"R\(p\+'\w', '\w+ph', (\[[^\]]*\]), 'water'",b)]+EXTRA.get(key,{}).get('sea',[])
    if key in SEA: polys=[SEA[key]]
    if key in NPYX:                                           # extra still things cut with SAM
        nx=np.load(S+NPYX[key]).astype(np.uint8); ex=np.maximum(ex,cv2.dilate(nx,np.ones((25,25),np.uint8)).astype(np.float32))
    if key in VAR:                                            # beach: painted wave cycle
        foam=[SURF[img]] if img in SURF else []
        m=water_mask(B,polys+foam,ex,key,foam)
        exd=cv2.GaussianBlur(cv2.dilate((ex>0.05).astype(np.uint8),np.ones((61,61),np.uint8)).astype(np.float32),(0,0),6)[...,None]
        vs=[F.rgb(p)*(1-exd)+B*exd for p in VAR[key]]      # variants never redraw people/animals
        fr=F.water_cycle(B,vs,amp=.3 if key=='sabado:5' else .4,steps=10 if key=='sabado:5' else 7)
        pa,box=F.save(fr,m,img,'lw'); parts.append(F.loop(pa,box,12))
    elif polys:                                               # sea / harbour: own texture drifts toward the viewer
        m=water_mask(B,polys,ex,key,EXP_=exclusion(key,img,True) if key in SEA else None)
        if key in SEA_EXCL: m=np.clip(m-F.soften(F.poly_mask(SEA_EXCL[key])>0,5),0,1)
        if key not in NIGHTK:                                 # rocks and dark shore stay still
            dk=cv2.dilate((F.lum(B)<60).astype(np.uint8),np.ones((7,7),np.uint8)).astype(np.float32)
            m=np.clip(m-cv2.GaussianBlur(dk,(0,0),2)*1.5,0,1)
        fr=F.ripple(B,m,n=16,near=RAMP.get(key,2.6 if key in FAR else 3.4))
        pa,box=F.save(fr,m,img,'ls'); parts.append(F.loop(pa,box,6))
    if key in LEVADA:
        poly=eval(re.search(r"life\.flow\(p\+'s', '\w+', (\[[^\]]*\])",b).group(1))
        d,P=LEVADA[key]; m=np.clip(F.soften(F.poly_mask([poly]),3)-ex*1.5,0,1)
        fr=F.fall_scroll(B,n=24,P=P,direction=d); pa,box=F.save(fr,m,img,'lv'); parts.append(F.loop(pa,box,9))
    for poly in re.findall(r"R\(p\+'\w', '\w+ph', (\[[^\]]*\]), 'fall'",b):
        poly=eval(poly); area=F.poly_mask([poly]); m=area&(F.lum(B)>150)&(F.sat(B)<70)
        m=np.clip(F.soften(m,3)-ex*1.5,0,1)
        fr=F.fall_scroll(B,n=24,P=70); pa,box=F.save(fr,m,img,'lf'); parts.append(F.loop(pa,box,9))
    if key=='domingo:3':                                       # forest mist drifts sideways (pale pixels only)
        poly=eval(re.search(r"R\(p\+'m', 'domingo3ph', (\[[^\]]*\]), 'sky'",b).group(1))
        m=F.poly_mask([poly])&(F.lum(B)>175)&(F.sat(B)<40); m=np.clip(F.soften(m,3,3)-ex*1.5,0,1)
        fr=F.fall_scroll(B,n=16,P=70,direction=(1,0)); pa,box=F.save(fr,m,img,'lm'); parts.append(F.loop(pa,box,16))
    glows=[(float(x),float(y),float(r)) for x,y,r in re.findall(r"G\(p\+'\w+', ([\d.]+), ([\d.]+), ([\d.]+)",b)]+EXTRA.get(key,{}).get('glow',[])
    exp=exclusion(key,img,True)
    for gi,(cx,cy,r) in enumerate(glows):
        g=np.exp(-(((F.GX-cx*K)**2+(F.GY-cy*K)**2)/(2*(r*K*.6)**2))).astype(np.float32)
        g2=np.clip(g-ex,0,1); g=g2 if (g2>.02).sum()>=200 else np.clip(g-exp,0,1); amp=.07
        if (g>.02).sum()<50: continue
        fr=F.breathe(B,g,n=16,amp=amp); m=np.clip(g*4,0,1)*(g>.02)
        pa,box=F.save(fr,m,img,f'lg{gi}'); parts.append(F.loop(pa,box,12+2*gi))
    for ti,(rect,th,warm,mx,gap) in enumerate(TW.get(key,[])+EXTRA.get(key,{}).get('tw',[])):
        dots=life.bright_spots(F.M+img+'.jpg',rect,thresh=th,warm=warm,max_n=mx,min_gap=gap)
        if not dots: continue
        mm=np.zeros((H,W),np.float32)
        for x,y in dots: cv2.circle(mm,(int(x*K),int(y*K)),10,1.0,-1)
        mm=np.clip(cv2.GaussianBlur(mm,(0,0),3)-exp,0,1)
        if (mm>.01).sum()<50: continue
        fr=F.twinkle(B,dots,n=24); pa,box=F.save(fr,mm,img,f'lt{ti}'); parts.append(F.loop(pa,box,18))
    return parts
def strip_pfx(key):
    lines=open(A+'index.html').read().split('\n')
    i=[n for n,l in enumerate(lines) if re.match(r"^(?:const PHOTOS=\{)?'"+re.escape(key)+"':",l)][0]
    lines[i]=re.sub(r'<g class="pfxw">.*?</g><!--/pfx-->','',lines[i]); open(A+'index.html','w').write('\n'.join(lines))
if __name__=='__main__':
  keys=sys.argv[1:] or [k for k in blocks if k not in DONE]
  for key in keys:
    parts=build(key); strip_pfx(key)
    F.insert(A+'index.html',key,''.join(parts)); print(key,len(parts),flush=True)
