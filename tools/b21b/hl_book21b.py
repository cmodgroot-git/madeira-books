"""Tap regions for book 21b (mae21, «Mensagens para a Mãe»): book 21's pictures (masters b21p*), João's words."""
import os,sys
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','b21'))
from hl_book21 import SPEC as S21
def g(p,k): return dict(S21[p])[k]
SPEC={
0:[('cafe',[('ell',700,585,50,32),('ell',858,583,50,32)]),('mao',[('ell',762,505,78,48)]),('cao',g(0,'cao'))],
1:[('varanda',g(1,'varanda')),('papel',g(1,'renda'))],
2:[('janela',[('rect',1062,30,1475,700)])],
3:[],
4:[('linha',g(4,'linha'))],
5:[('olhos',[('ell',768,107,30,13)]),('pes',[('ell',965,838,95,42)])],
6:[('chaves',g(6,'chaves'))],
7:[('pizza',g(7,'pizza'))],
}
NOT_SHOWN={}
