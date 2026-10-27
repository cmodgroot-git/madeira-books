"""Book 3 page 6: the waterfall falls with the same streak method and speed as book 7 (24 frames, 1.5 s)."""
import sys, glob, os, pickle, re, numpy as np, cv2
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'; sys.path.insert(0,S)
import frames as F, windfx
W,H=F.W,F.H
src=open(S+'b7anim.py').read(); i=src.find('def waterfall'); j=src.find('\ni=int(sys.argv[1])')
exec(src[i:j])
B=F.load('b3p6.jpg')
f=sorted(glob.glob(S+'gen/hlcache/domingo_5_*.pkl'),key=os.path.getmtime)[-1]; R={k:m for k,m in pickle.load(open(f,'rb'))[1]}
m=R['cascata agua cai'].astype(np.uint8)
hsv=cv2.cvtColor(np.clip(B,0,255).astype(np.uint8),cv2.COLOR_RGB2HSV)
m=(m&(hsv[...,2]>140)&(hsv[...,1]<80)).astype(np.uint8)          # the white water only, not the wet rock behind it
m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((9,5),np.uint8)); n,lb,st,_=cv2.connectedComponentsWithStats(m)
m=np.isin(lb,[k for k in range(1,n) if st[k,4]>300]).astype(np.uint8)
print('fall px',m.sum(),'box',cv2.boundingRect(m))
fr,mw=waterfall(B,m)
if len(sys.argv)>1:
    import imageio.v2 as iio
    from PIL import Image
    iio.mimsave(S+'city2/b3p6_fall.mp4',[np.asarray(Image.fromarray(np.clip(f*mw[...,None]+B*(1-mw[...,None]),0,255).astype(np.uint8)).resize((1200,674))) for f in fr]*4,fps=16,quality=8,macro_block_size=2); sys.exit()
windfx.add_layer('domingo:5','','b3p6_mw')
pa,box=F.save(fr,mw,'b3p6','lw'); windfx.add_layer('domingo:5',F.loop(pa,box,1.5),'b3p6_lw'); print('ok',box)
pool=(R['lago pequeno'].astype(np.uint8)&(1-cv2.dilate(R['rochas'].astype(np.uint8),np.ones((5,5),np.uint8)))).astype(np.float32)
pool=pool*(1-np.clip(cv2.GaussianBlur(cv2.dilate(m,np.ones((15,15),np.uint8)).astype(np.float32),(0,0),4),0,1))
fp=F.ripple(B,pool,n=16,near=2.4,far=1.0,lam_near=60.,lam_far=30.,shine=.04)
pa,box=F.save(fp,np.clip(cv2.GaussianBlur(pool,(0,0),1.2),0,1),'b3p6','lp'); windfx.add_layer('domingo:5',F.loop(pa,box,6.0),'b3p6_lp'); print('pool',box)
