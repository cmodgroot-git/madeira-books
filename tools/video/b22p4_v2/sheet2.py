import cv2,numpy as np,pickle,glob,sys
F=sorted(glob.glob('fr/*.png')); R=pickle.load(open(sys.argv[1],'rb')); keys=sys.argv[2].split(','); ts=[int(x) for x in sys.argv[3].split(',')]
rows=[]
for k in keys:
    cells=[]
    for t in ts:
        f=cv2.imread(F[t]); a=R[k][t]; ys,xs=np.nonzero(a>127)
        if len(xs)==0: cells.append(np.zeros((300,300,3),np.uint8)); continue
        cx,cy=int(xs.mean()),int(ys.mean()); h={'rita':150,'bola':70,'cabeca':110}.get(k,110)
        x0,y0=max(0,min(1280-2*h,cx-h)),max(0,min(720-2*h,cy-h)); c=f[y0:y0+2*h,x0:x0+2*h].copy()
        cs,_=cv2.findContours((a[y0:y0+2*h,x0:x0+2*h]>127).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        c=cv2.resize(c,(300,300),interpolation=cv2.INTER_CUBIC); cs=[(x*300/(2*h)).astype(np.int32) for x in cs]
        cv2.drawContours(c,cs,-1,(0,255,255),1,cv2.LINE_AA); cv2.putText(c,f'{k} {t}',(6,22),0,0.6,(255,255,255),2); cells.append(c)
    rows.append(np.hstack(cells))
cv2.imwrite(sys.argv[4],np.vstack(rows),[cv2.IMWRITE_JPEG_QUALITY,80])
