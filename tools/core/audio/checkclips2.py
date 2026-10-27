import sys,json,unicodedata,difflib; sys.path.insert(0,'.')
from decode import dec
D='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/artifact-files/87e1712e-5e90-4175-b828-2581544915d4/audio/w/'
ix=json.load(open('wordindex.json')); B=json.load(open('wordbatches.json'))
n=lambda s:''.join(c for c in unicodedata.normalize('NFD',s.lower()) if not unicodedata.combining(c) and c.isalpha())
skel=lambda s:''.join(c for c in n(s) if c not in 'aeiou')   # consonant skeleton survives vowel reduction
bad=[]
for f in json.load(open('badwords.json')):
    if 1:
        g=dec(D+ix[f.lower()]+'.mp3',0,None)
        r=difflib.SequenceMatcher(None,skel(f),skel(g)).ratio()
        if r<.6 or len(n(g))>len(n(f))*1.8+2: bad.append((f,g,round(r,2)))
print(len(bad)); [print(b) for b in bad]
json.dump([b[0] for b in bad],open('badwords2.json','w'),ensure_ascii=False)
