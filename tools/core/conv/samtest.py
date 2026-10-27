import sys,numpy as np,resource
sys.path.insert(0,'sam/repo')
import torch; torch.set_num_threads(4)
from segment_anything import sam_model_registry, SamPredictor
from PIL import Image
m=sam_model_registry['vit_h'](checkpoint='sam/vit_h.pth'); print('loaded',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024,'MB',flush=True)
P=SamPredictor(m); a=np.asarray(Image.open('gen/masters/b5p1.jpg').convert('RGB'))
with torch.inference_mode(): P.set_image(a)
print('set',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024,'MB')
