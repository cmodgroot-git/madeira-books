import sys,json,re,unicodedata,difflib; sys.path.insert(0,'.')
from decode import dec
B=json.load(open('wordbatches.json'))
n=lambda s:''.join(c for c in unicodedata.normalize('NFD',s.lower()) if not unicodedata.combining(c))
for bi,forms in enumerate(B):
    got=n(dec(f'words/batch{bi}.mp3',0,None)).split()
    exp=[w for f in forms for w in n(f).replace('-',' ').replace("'"," ").split()]
    sm=difflib.SequenceMatcher(None,exp,got)
    miss=[]
    for op,a1,a2,b1,b2 in sm.get_opcodes():
        if op in('delete','replace'): miss.append((' '.join(exp[a1:a2]),'->',' '.join(got[b1:b2])))
    print(bi,miss)
