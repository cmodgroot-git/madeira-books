"""Book 6 page 2 (tunnel): tunnel walls rush past the four side panes (skill madeira-vehicle-interior). usage: b6p2life.py [preview]"""
import sys, glob, os, pickle, numpy as np, cv2
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'; sys.path.insert(0,S)
import frames as F, windfx, vehlife
W,H=1600,898; B=F.load('b6p2.jpg')
def poly(*p):
    m=np.zeros((H,W),np.uint8); cv2.fillPoly(m,[np.array(p,np.int32)],1); return m
def line(p,q,w):
    m=np.zeros((H,W),np.uint8); cv2.line(m,p,q,1,w); return m
if os.path.exists(S+'gen/b6p2_ppl.npz'):
    d=np.load(S+'gen/b6p2_ppl.npz'); ANA,RITA=d['A'],d['R']
else:
    import hlmask; pg=hlmask.Page('pico',1)
    ANA,_=pg.sam_mask([150,100,750,640],[(440,230),(400,450),(690,440),(330,300)],[(800,300)],'big')
    RITA,_=pg.sam_mask([980,110,1445,660],[(1080,270),(1160,350),(1050,520),(1220,480)],[(1270,650),(900,300)],'big')
    np.savez_compressed(S+'gen/b6p2_ppl.npz',A=ANA,R=RITA)
PPL=(ANA|RITA).astype(np.uint8)
mir_l=poly((177,323),(300,323),(300,409),(177,409)); mir_r=poly((1320,326),(1451,326),(1451,421),(1320,421))
LR=poly((0,0),(100,0),(95,60),(62,300),(40,470),(0,480))                                   # rear-left quarter glass
LF=poly((236,94),(362,122),(362,438),(176,438),(191,286))&(1-mir_l)&(1-line((171,223),(326,383),40))&(1-poly((160,200),(206,200),(206,280),(160,280)))
RF=poly((1282,116),(1415,94),(1440,110),(1448,440),(1349,446),(1303,377),(1288,229))&(1-mir_r)&(1-line((1497,246),(1354,417),40))
RR=poly((1538,14),(1600,14),(1600,470),(1565,466),(1540,200))
panes=[(LR,-1),(LF,-1),(RF,1)]   # the far-right rear pane is mostly door frame: left still
if __name__=='__main__':
    o=B*.3
    for m,_ in panes:
        mm=(m&(1-cv2.dilate(PPL,np.ones((9,9),np.uint8))))>0; o[mm]=B[mm]
    cv2.imwrite(S+'conv/p2panes.jpg',cv2.cvtColor(np.clip(o,0,255).astype(np.uint8),cv2.COLOR_RGB2BGR))
    if len(sys.argv)>1 and sys.argv[1]=='masks': sys.exit()
    fr,ms=vehlife.side(B,panes,people=PPL)
    if len(sys.argv)>1:
        from PIL import Image
        mm=np.clip(sum(ms),0,1)
        rows=[np.clip(fr[k]*mm[...,None]+B*(1-mm[...,None]),0,255).astype(np.uint8)[0:500] for k in (0,8,16)]
        Image.fromarray(np.concatenate([np.concatenate([r[:,0:400],r[:,1260:1600]],1) for r in rows],0)).save(S+'conv/p2prev.jpg',quality=85); sys.exit()
    left=np.clip(ms[0]+ms[1],0,1); right=ms[2]
    for name,m in (('lsl',left),('lsr',right)):
        pa,box=F.save(fr,m,'b6p2',name); windfx.add_layer('pico:1',F.loop(pa,box,1.2),f'b6p2_{name}'); print(name,len(pa),box,flush=True)
