import sys, re, numpy as np
S = '/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'
sys.path.insert(0, S + 'sam/repo')
from PIL import Image
src = open(S + 'windfx.py').read()
FOL = eval(re.search(r'FOLIAGE = (\{.*?\n\})', src, re.S).group(1))
from segment_anything import sam_model_registry, SamPredictor
key = sys.argv[1]; img, polys, boxes, amp = FOL[key]
P = SamPredictor(sam_model_registry['vit_h'](checkpoint=S + 'sam/vit_h.pth'))
arr = np.asarray(Image.open(S + f'gen/masters/{img}.jpg').convert('RGB').resize((1600, 898)))
P.set_image(arr); m = np.zeros((898, 1600), np.uint8)
for b in boxes:
    ms, sc, _ = P.predict(box=np.array(b, float), multimask_output=True)
    m |= ms[int(np.argmax([x.sum() for x in ms]))].astype(np.uint8)
np.save(S + f'gen/ppl_{img}.npy', m); print(key, m.mean())
