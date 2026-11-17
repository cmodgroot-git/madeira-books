"""Tap regions for book 20b (diario20, «O Diário da Ana»): book 20's pictures (masters b20p*), Ana's words."""
import os,sys
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','b20'))
from hl_book20 import TREES1,TRAIL3,RITA3,SEA6,COAST6
GLOVES1=[('ell',x,y,16,20) for x,y in [(925,535),(1025,540),(1137,545),(1168,540),(1285,548),(1412,548)]]+[('ell',637,420,26,24)]
HAIR5=[('poly',[(598,140),(628,128),(642,252),(604,258),(594,200)]),('poly',[(688,138),(706,150),(702,232),(688,236)])]
TIAGO7=('sam',(470,240,900,810),[(650,300),(600,450),(560,750)],[(755,665),(450,250)],'big')
SPEC={
0:[('nevoeiro',[('rect',820,170,1200,330)]),('arvores',TREES1),('luvas',GLOVES1)],
1:[('dedos',[('ell',1212,470,82,55)])],
2:[('floresta',[('rect',0,0,1600,620),('sub',RITA3),('sub',TRAIL3),('sub',('sam',(500,70,800,650),[(640,120),(630,250),(620,420)],[],'big')),('sub',('sam',(1000,170,1260,640),[(1100,230),(1110,330),(1120,450)],[],'big'))]),('trilho',[TRAIL3])],
3:[],
4:[('cabelo',HAIR5)],
5:[('vista',[('rect',880,0,1600,898)]),('ceu',[('rect',900,0,1600,290)]),('mar',[SEA6,('sub',COAST6)]),('falesias',[COAST6]),('horizonte',[('line',[(1170,298),(1600,298)],12)])],
6:[('mecanico',[TIAGO7]),('ombro',[('ell',545,395,45,30)])],
7:[('pordosol',[('ell',545,255,70,55)])],
}
NOT_SHOWN={}
