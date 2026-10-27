"""Book 6 page 7 (b6p7v2): steam rises from Ana's cup of tea."""
import sys, numpy as np, cv2
S='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'; sys.path.insert(0,S)
import frames as F, windfx
B=F.load('b6p7v2.jpg'); H,W=898,1600
fr=F.steam(B,755,366,height=150,width=42,alpha=.5,lean=12)
m=np.zeros((H,W),np.float32); cv2.ellipse(m,(765,290),(70,110),0,0,360,1.,-1); m=cv2.GaussianBlur(m,(0,0),10)
windfx.add_layer('pico:6','','b6p7_lt')
pa,box=F.save(fr,np.clip(m*1.3,0,1),'b6p7','lt'); windfx.add_layer('pico:6',F.loop(pa,box,4.0),'b6p7_lt'); print(box)
