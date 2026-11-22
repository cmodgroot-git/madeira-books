import cv2,numpy as np,pickle,glob,sys
F=sorted(glob.glob('fr/*.png')); R=pickle.load(open('roto.pkl','rb')); rows=[]
for k in sys.argv[1].split(','):
    cells=[]
    for t in [0,20,40,60,78,95]:
        f=cv2.imread(F[t]); a=R[k][t]; ys,xs=np.nonzero(a>127); cx,cy=int(xs.mean()),int(ys.mean()); h=120 if k!='rita' else 170
        x0,y0=max(0,min(1280-2*h,cx-h)),max(0,min(720-2*h,cy-h)); c=f[y0:y0+2*h,x0:x0+2*h].copy()
        cs,_=cv2.findContours((a[y0:y0+2*h,x0:x0+2*h]>127).astype(np.uint8),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        c=cv2.resize(c,(400,400),interpolation=cv2.INTER_CUBIC); cs=[(x*400/(2*h)).astype(np.int32) for x in cs]
        cv2.drawContours(c,cs,-1,(0,255,255),1,cv2.LINE_AA); cv2.putText(c,f'{k} {t}',(8,24),0,0.7,(255,255,255),2); cells.append(c)
    rows.append(np.hstack(cells))
cv2.imwrite('roto_sheet.jpg',np.vstack(rows),[cv2.IMWRITE_JPEG_QUALITY,82])
