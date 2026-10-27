"""Book 7 page 8 (b7p8v3, car seen from the road ahead): the sea ripples, the setting sun glows softly."""
import sys, numpy as np, cv2
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'; sys.path.insert(0,S)
import frames as F, windfx
W,H=1600,898
B=F.load('b7p8v4.jpg')
def poly(*p):
    m=np.zeros((H,W),np.uint8); cv2.fillPoly(m,[np.array(p,np.int32)],1); return m
sea=poly((1048,320),(1600,320),(1600,492),(1450,470),(1250,440),(1110,424),(1048,418))
sea&=1-poly((1050,392),(1113,392),(1113,458),(1050,458))           # the wing mirror
sea&=1-poly((1000,300),(1049,300),(1049,460),(1000,460))           # the car's side pillar
lum=F.lum(B); sea&=(lum>70).astype(np.uint8)
sea=cv2.morphologyEx(sea,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
fr=F.ripple(B,sea,n=16,near=2.2,far=.4,lam_near=60.,lam_far=12.,shine=.05,edge=6)
g=np.zeros((H,W),np.float32); cv2.circle(g,(1228,302),46,1.,-1); g=cv2.GaussianBlur(g,(0,0),14)
fr=[np.clip(f*(1+.10*0.5*(1-np.cos(2*np.pi*i/16))*g)[...,None] if False else f*(1+.10*0.5*(1-np.cos(2*np.pi*i/16))*g[...,None]),0,255) for i,f in enumerate(fr)]
mask=np.clip(np.maximum(cv2.GaussianBlur(sea.astype(np.float32),(0,0),1.2),np.clip(g*1.5,0,1)),0,1)
if len(sys.argv)>1:
    cv2.imwrite(S+'car2/seamask.jpg',cv2.cvtColor(np.clip(B*(1-.6*mask[...,None])+np.array([255,0,0])*.6*mask[...,None],0,255).astype(np.uint8),cv2.COLOR_RGB2BGR)); sys.exit()
pa,box=F.save(fr,mask,'b7p8','sea')
windfx.add_layer('seixal:7',F.loop(pa,box,6.0),'b7p8_sea')
print('ok',box)
