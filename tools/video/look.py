"""Highlight looks for a still or a video frame.
usage: python3 look.py picture.jpg matte.png out.jpg [--look first|soft] [--strength 1.0]
matte: grey PNG, white = the word's thing (soft edges fine).
DEFAULT = "first" (user, Nov 22 2026: "go back to your original highlight settings"):
  rest of the picture 20% darker, full colour; the thing 40% brighter; 1.5 px light-grey outline just outside it
  (Nov 22: "gray outline slightly thicker. 10% background change. highlight to 40%", then "background to 20%", "thinner outline").
"soft" = the tuned dim-and-glow look from Nov 21-22 (kept in case the user wants it again)."""
import cv2,numpy as np,sys
FIRST=dict(dim=0.80,bright=1.40,line_bgr=(0.75,0.75,0.75),line_px=1.5)
SOFT=dict(dim=0.62,grey=0.275,contrast=1.06,lift=0.03,glow=0.30,glow_sigma=7)
def look_first(f,a,s=1.0,P=FIRST):
    o=f*P['dim']*(1-a[...,None])+np.clip(f*P['bright']+0.02,0,1)*a[...,None]
    r=int(np.ceil(P['line_px'])); k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*r+1,)*2)
    ring=np.clip(cv2.dilate(a,k)-a,0,1); ring=cv2.GaussianBlur(ring,(0,0),0.7)[...,None]
    o=o*(1-ring)+np.float32(P['line_bgr'])*ring
    return np.clip(f*(1-s)+o*s,0,1)
def look_soft(f,a,s=1.0,P=SOFT):
    g=f.mean(2,keepdims=True); out_=(f*(1-P['grey'])+g*P['grey'])*P['dim']
    in_=np.clip((f-0.5)*P['contrast']+0.5+P['lift'],0,1)
    A=cv2.GaussianBlur(a,(0,0),1.2)[...,None]; o=in_*A+out_*(1-A)
    rim=np.clip(cv2.GaussianBlur(a,(0,0),P['glow_sigma'])-a,0,1)[...,None]*1.6
    o=o+rim*np.float32([0.78,0.93,1.0])*P['glow']
    return np.clip(f*(1-s)+o*s,0,1)
look=look_first
if __name__=='__main__':
    f=cv2.imread(sys.argv[1]).astype(np.float32)/255
    a=cv2.resize(cv2.imread(sys.argv[2],0),(f.shape[1],f.shape[0])).astype(np.float32)/255
    s=float(sys.argv[sys.argv.index('--strength')+1]) if '--strength' in sys.argv else 1.0
    fn=look_soft if ('--look' in sys.argv and sys.argv[sys.argv.index('--look')+1]=='soft') else look_first
    cv2.imwrite(sys.argv[3],(fn(f,a,s)*255).astype(np.uint8))
