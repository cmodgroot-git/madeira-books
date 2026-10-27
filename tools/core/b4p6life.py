"""Book 4 page 6 (b4p6v2): sea ripples between the two women, the setting sun glows softly."""
import sys, glob, os, pickle, numpy as np, cv2
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'; sys.path.insert(0,S)
import frames as F, windfx
W,H=1600,898
B=F.load('b4p6v2.jpg')
def poly(*p):
    m=np.zeros((H,W),np.uint8); cv2.fillPoly(m,[np.array(p,np.int32)],1); return m
f=sorted(glob.glob(S+'gen/hlcache/jantar_5_*.pkl'),key=os.path.getmtime)[-1]; R={k:m for k,m in pickle.load(open(f,'rb'))[1]}
ppl=(R['comem']>0).astype(np.uint8)
sea=poly((0,266),(1335,284),(1330,350),(1380,385),(1450,402),(1600,408),(1600,488),(0,488))
sea&=1-cv2.dilate(ppl,np.ones((9,9),np.uint8))
sea&=1-poly((615,425),(705,425),(705,520),(615,520))   # bottle neck
for p in [((0,318),(60,318),(120,360),(180,390),(200,488),(0,488)),((495,455),(565,445),(580,488),(495,488)),((1415,430),(1480,412),(1600,412),(1600,488),(1415,488))]: sea&=1-poly(*p)
sea=cv2.morphologyEx(sea,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
n,lab,st,_=cv2.connectedComponentsWithStats(sea); keep=np.zeros_like(sea)
for i in range(1,n):
    if st[i,4]>4000: keep[lab==i]=1
sea=keep
fr=F.ripple(B,sea,n=16,near=1.6,far=.4,lam_near=40.,lam_far=12.,shine=.05,edge=6)
g=np.zeros((H,W),np.float32); cv2.ellipse(g,(791,262),(70,66),0,180,360,1.,-1); g=cv2.GaussianBlur(g,(0,0),16)
g*=(1-cv2.GaussianBlur(ppl.astype(np.float32),(0,0),3))
fr=[np.clip(f*(1+.10*0.5*(1-np.cos(2*np.pi*i/16))*g[...,None]),0,255) for i,f in enumerate(fr)]
mask=np.clip(np.maximum(cv2.GaussianBlur(sea.astype(np.float32),(0,0),1.2),np.clip(g*1.5,0,1)),0,1)
if len(sys.argv)>1:
    cv2.imwrite(S+'gen/b4p6_seamask.jpg',cv2.cvtColor(np.clip(B*(1-.6*mask[...,None])+np.array([255,0,0])*.6*mask[...,None],0,255).astype(np.uint8),cv2.COLOR_RGB2BGR)); sys.exit()
windfx.add_layer('jantar:5','','b4p6_ls'); windfx.add_layer('jantar:5','','b4p6_lg0')
pa,box=F.save(fr,mask,'b4p6','sea')
windfx.add_layer('jantar:5',F.loop(pa,box,6.0),'b4p6_sea')
print('ok',box)
