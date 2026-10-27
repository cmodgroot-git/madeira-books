"""Moving-vehicle interiors (skill madeira-vehicle-interior): scenery rushing past side windows.
side(B, panes, people, n, P, K) -> frames, mask   panes = [(mask, dirn)], dirn -1 = slides left, +1 = slides right"""
import numpy as np, cv2
def side(B,panes,people=None,n=24,P=110,K=34,sx=11,sy=3,drops=True):
    H,W=B.shape[:2]; L=B@np.float32([.299,.587,.114])
    out=[B.copy() for _ in range(n)]; masks=[]
    ppl=cv2.dilate(people.astype(np.uint8),np.ones((9,9),np.uint8)) if people is not None else np.zeros((H,W),np.uint8)
    for m,dirn in panes:
        m=(m>0).astype(np.uint8)&(1-ppl)
        loc=cv2.GaussianBlur(L,(0,0),4); d=((L-loc>22)&(m>0)).astype(np.uint8)
        nn,lb,st,_=cv2.connectedComponentsWithStats(d)
        dm=cv2.dilate(np.isin(lb,[k for k in range(1,nn) if 3<=st[k,4]<=40]).astype(np.uint8),np.ones((3,3),np.uint8))*(1 if drops else 0)
        clean=cv2.inpaint(np.clip(B,0,255).astype(np.uint8),dm.astype(np.uint8),5,cv2.INPAINT_TELEA).astype(np.float32) if dm.any() else B.copy()
        dl=np.where(dm[...,None]>0,B-clean,0)
        me=cv2.erode(m,np.ones((5,5),np.uint8)); rows=[]
        for y in range(H):
            xs_=np.nonzero(me[y])[0]
            if len(xs_)<10: continue
            for rr in np.split(xs_,np.nonzero(np.diff(xs_)>1)[0]+1):
                if len(rr)<10: continue
                xa,xb=rr[0],rr[-1]+1
                seg=cv2.resize(clean[y:y+1,xa:xb],(P+K,1),interpolation=cv2.INTER_LINEAR)[0]
                w=np.linspace(0,1,K)[:,None]; tile=seg[:P].copy(); tile[:K]=seg[P:P+K]*(1-w)+seg[:K]*w
                rows.append((y,xa,xb,tile))
        ys,xs=np.nonzero(me); y0,y1,x0,x1=max(0,ys.min()-8),min(H,ys.max()+9),max(0,xs.min()-8),min(W,xs.max()+9)
        mm=me[y0:y1,x0:x1].astype(np.float32)
        for k in range(n):
            layer=np.zeros((y1-y0,x1-x0,3),np.float32)
            for y,xa,xb,tile in rows:
                xs=np.arange(xa,xb); acc=0
                for sft in np.linspace(-.5,.5,5):
                    acc=acc+tile[np.mod(np.round((xs-xa)*P/(xb-xa)-(k+sft)*P/n*dirn).astype(int),P)]
                layer[y-y0,xa-x0:xb-x0]=acc/5
            num=cv2.GaussianBlur(layer*mm[...,None],(0,0),sigmaX=sx,sigmaY=sy); den=cv2.GaussianBlur(mm,(0,0),sigmaX=sx,sigmaY=sy)[...,None]
            sub=out[k][y0:y1,x0:x1]; sub[:]=np.where(mm[...,None]>0,num/np.maximum(den,1e-3),sub); out[k][me>0]+=dl[me>0]
        masks.append(np.clip(cv2.GaussianBlur(me.astype(np.float32),(0,0),1.),0,1))
    return out,masks
