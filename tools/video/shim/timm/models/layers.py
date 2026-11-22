import torch,torch.nn as nn,collections.abc,itertools
def to_2tuple(x): return tuple(x) if isinstance(x,collections.abc.Iterable) else (x,x)
def trunc_normal_(t,mean=0.,std=1.,a=-2.,b=2.): return nn.init.trunc_normal_(t,mean,std,a,b)
class DropPath(nn.Module):
    def __init__(self,drop_prob=0.,scale_by_keep=True): super().__init__(); self.drop_prob=drop_prob
    def forward(self,x): return x
