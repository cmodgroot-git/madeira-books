import torch.nn.functional as F
from PIL import Image
import numpy as np
def to_pil_image(x): return Image.fromarray(np.asarray(x))
def resize(img,size,**kw):
    if isinstance(img,Image.Image): return img.resize((size[1],size[0]),Image.BILINEAR)
    return F.interpolate(img,size,mode='bilinear',align_corners=False,antialias=True)
