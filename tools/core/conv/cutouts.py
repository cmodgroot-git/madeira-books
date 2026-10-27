import sys, numpy as np
sys.argv=[sys.argv[0]]+sys.argv[1:]
sys.path.insert(0,'/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/conv')
import hl_book1 as HB
from segment_anything import sam_model_registry, SamPredictor
from PIL import Image, ImageDraw
HB.P=SamPredictor(sam_model_registry['vit_b'](checkpoint=HB.S+'sam/vit_b.pth'))
pages=[int(x) for x in sys.argv[1:]] or list(range(9))
tiles=[]
for pg in pages:
    arr,ms=HB.masks_for(pg)
    for k,m in ms:
        a=arr.astype(np.float32); mm=m[...,None].astype(np.float32)
        out=a*mm+a*(1-mm)*0.25
        im=Image.fromarray(out.astype(np.uint8)).resize((480,269)); ImageDraw.Draw(im).text((4,4),f'p{pg+1} {k}',fill=(255,255,0)); tiles.append(im)
cols=4; rows=(len(tiles)+cols-1)//cols
S_=Image.new('RGB',(480*cols,269*rows))
for i,t in enumerate(tiles): S_.paste(t,((i%cols)*480,(i//cols)*269))
S_.save(HB.S+'conv/cutouts_'+'_'.join(map(str,pages))+'.jpg',quality=80)
