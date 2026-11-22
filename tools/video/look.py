"""The approved highlight look (user-tuned on book 22 page 4, Nov 2026), for a still or a video frame.
usage: python3 look.py picture.jpg matte.png out.jpg [--strength 1.0]
matte: grey PNG, white = the word's thing (soft edges fine). Same numbers as tools/video/b22p4/render.py."""
import cv2,numpy as np,sys
DIM=0.62      # rest of picture: 38% darker (user: "increase the dimming only")
GREY=0.275    # rest of picture: 27.5% toward grey
CONTRAST=1.06; LIFT=0.03   # the thing itself: slightly punchier, a touch brighter
GLOW=0.30; GLOW_SIGMA=7    # soft warm-white halo just outside the edge
def look(f,a,s=1.0):
    """f: BGR float 0..1, a: matte float 0..1, s: fade 0..1"""
    g=f.mean(2,keepdims=True); out_=(f*(1-GREY)+g*GREY)*DIM
    in_=np.clip((f-0.5)*CONTRAST+0.5+LIFT,0,1)
    A=cv2.GaussianBlur(a,(0,0),1.2)[...,None]; o=in_*A+out_*(1-A)
    rim=np.clip(cv2.GaussianBlur(a,(0,0),GLOW_SIGMA)-a,0,1)[...,None]*1.6
    o=o+rim*np.float32([0.78,0.93,1.0])*GLOW
    return np.clip(f*(1-s)+o*s,0,1)
if __name__=='__main__':
    f=cv2.imread(sys.argv[1]).astype(np.float32)/255
    a=cv2.resize(cv2.imread(sys.argv[2],0),(f.shape[1],f.shape[0])).astype(np.float32)/255
    s=float(sys.argv[sys.argv.index('--strength')+1]) if '--strength' in sys.argv else 1.0
    cv2.imwrite(sys.argv[3],(look(f,a,s)*255).astype(np.uint8))
