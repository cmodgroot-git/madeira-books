"""Generic optical-flow morph loop builder.
usage: morph_page.py <base img name, e.g. b3p6> <prefix> <amp> <steps> <variants json list of full-frame jpg paths> <water polys json (preview px)> <out json>"""
import sys, json, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'
A=S+'artifact-files/87e1712e-5e90-4175-b828-2581544915d4/img/'
img,pre,amp,steps=sys.argv[1],sys.argv[2],float(sys.argv[3]),int(sys.argv[4])
var=json.loads(sys.argv[5]); polys=json.loads(sys.argv[6]); outj=sys.argv[7]
W,H=1600,898; k=W/1200
B=np.asarray(Image.open(A+img+'.jpg').convert('RGB'),np.float32)
dis=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
g=lambda a:cv2.cvtColor(np.clip(a,0,255).astype(np.uint8),cv2.COLOR_RGB2GRAY)
flow=lambda a,b:dis.calc(g(a),g(b),None)
gx,gy=np.meshgrid(np.arange(W,dtype=np.float32),np.arange(H,dtype=np.float32))
warp=lambda im,f,s:cv2.remap(im,gx-s*f[...,0],gy-s*f[...,1],cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT)
def morph(a,b,s,fab=None,fba=None):
    fab=flow(a,b) if fab is None else fab; fba=flow(b,a) if fba is None else fba
    return (1-s)*warp(a,fab,s)+s*warp(b,fba,1-s)
V=[np.asarray(Image.open(p).convert('RGB').resize((W,H),Image.LANCZOS),np.float32) for p in var]
keys=[B]+[morph(B,v,amp) for v in V]
frames=[]
for i in range(len(keys)):
    a,b=keys[i],keys[(i+1)%len(keys)]; fab,fba=flow(a,b),flow(b,a)
    frames+= [morph(a,b,j/steps,fab,fba) for j in range(steps)]
m=Image.new('L',(W,H),0); d=ImageDraw.Draw(m)
for q in polys: d.polygon([(x*k,y*k) for x,y in q],fill=255)
still=json.load(open(S+'gen/still.json')).get(img,[])
ex=Image.new('L',(W,H),0); d=ImageDraw.Draw(ex)
for q in still: d.polygon([(x*k,y*k) for x,y in q],fill=255)
ex=np.asarray(ex.filter(ImageFilter.MaxFilter(9)),np.float32)/255
mask=np.clip(np.asarray(m.filter(ImageFilter.GaussianBlur(3)),np.float32)/255-ex*1.5,0,1)
ys,xs=np.nonzero(mask>0.01); x0,y0,x1,y1=xs.min(),ys.min(),xs.max()+1,ys.max()+1
al=(mask[y0:y1,x0:x1]*255).astype(np.uint8); paths=[]
for i,f in enumerate(frames):
    p=f'{img}_{pre}{i:02d}.webp'
    Image.fromarray(np.dstack([np.clip(f[y0:y1,x0:x1],0,255).astype(np.uint8),al]),'RGBA').save(A+p,quality=80,method=6); paths.append(p)
json.dump([paths,[int(x0),int(y0),int(x1-x0),int(y1-y0)]],open(outj,'w'))
pv=Image.new('RGB',(1200,337))
for i,j in enumerate([0,len(frames)//3,2*len(frames)//3]):
    c=Image.fromarray(np.clip(frames[j],0,255).astype(np.uint8)).resize((1200,674)).crop((150,0,750,674)).resize((300,337)); pv.paste(c,(i*400,0))
pv.save(outj.replace('.json','_prev.jpg'),quality=88)
print(len(paths), sum(__import__('os').path.getsize(A+p) for p in paths)//1024,'KB')
