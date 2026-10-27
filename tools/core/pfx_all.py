"""Water particle systems for every page with water. Run AFTER life_all.py (which rebuilds the life layers)."""
import sys, re, json
sys.path.insert(0, '/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad')
import life
S = '/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'
A = S + 'artifact-files/87e1712e-5e90-4175-b828-2581544915d4/'
F = A + 'index.html'
src = open(S + 'life_all.py').read()
IMG = dict(re.findall(r"'(\w+:\d+)': \('(b\dp\d)'", src)); IMG.update({'manha:8': 'b1p9', 'manha:2': 'b1p3'})
STILL = json.load(open(S + 'gen/still.json')); SURF = json.load(open(S + 'gen/surf.json')); WASH = json.load(open(S + 'gen/wash.json'))
SEA = {}
for pid, poly in re.findall(r"R\(p\+'s', '(\w+?)ph', (\[[^\]]*\]), 'water'\)", src):
    m = re.match(r'([a-z]+)(\d+)', pid); SEA[f'{m.group(1)}:{m.group(2)}'] = eval(poly)
SEA['manha:8'] = [(770,288),(830,262),(972,258),(972,372),(868,370),(805,348),(772,322)]
FRAMES = {'jantar:1', 'domingo:5'}             # pages animated with painted water frames instead of particles
NIGHT = {'manha:8', 'sabado:7', 'jantar:7'}
FAR = {'manha:0', 'manha:1', 'manha:3', 'manha:4', 'manha:7', 'manha:8', 'sabado:0', 'sabado:1', 'sabado:2', 'sabado:7', 'domingo:7', 'jantar:0', 'jantar:2', 'jantar:5'}
DAY, MOON = '#FFFDF2', '#E6ECF7'

def area(p):
    return abs(sum(p[i][0]*p[i-1][1] - p[i-1][0]*p[i][1] for i in range(len(p)))) / 2 * life.KX * life.KY

C3 = [(0,345),(30,350),(150,440),(250,520),(360,600),(455,674),(275,674),(235,630),(150,505),(0,385)]
C4 = [(830,462),(848,462),(945,518),(1040,578),(1130,628),(1200,655),(1200,674),(1140,674),(1030,604),(930,530),(828,470)]
C5 = [(688,430),(708,428),(712,468),(700,510),(660,590),(615,674),(505,674),(600,560),(685,450)]
FALL = [(300,0),(400,0),(410,150),(440,300),(470,442),(310,446),(305,300),(295,150)]
STREAMS = {
 'domingo:2': [dict(t='stream', a=(15,352), b=(370,674), wa=25, wb=110, n=26, travel=9, len=6, w=.8, op=.4, dop=.55), C3],
 'domingo:3': [dict(t='stream', a=(838,466), b=(1190,668), wa=12, wb=40, n=12, travel=10, len=3, w=.6, op=.4, dop=.5), C4],
 'domingo:4': [dict(t='stream', a=(699,432), b=(558,690), wa=22, wb=112, n=22, travel=8, len=6, w=.8, op=.4, dop=.55), C5],
}

def systems(key):
    out = []
    if key in FRAMES: return out
    if key in SEA:
        p = SEA[key]; night = key in NIGHT; shore_page = IMG.get(key) in WASH
        n = max(12, min(60, round(area(p) / 60)))
        d = (0, .5) if key == 'domingo:5' else (.5, .2) if shore_page else (.9, 0)
        far = key in FAR
        out.append(([dict(t='sea', poly=p, n=n, d=d, life=(4, 8), len=2.6 if far else 5.5, w=.5 if far else .8,
                          op=(.2 if far else .28) if night else (.28 if far else .4), dop=(.25 if far else .35) if night else (.35 if far else .55),
                          col=MOON if night else DAY)], p))
    img = IMG.get(key)
    if img in WASH:
        out.append(([dict(t='shore', sea=WASH[img]['sea'], shore=WASH[img]['shore'], n=34, T=14, roll=1.6, amp=.3, len=9, w=1.0, op=.55, dop=.5)], SURF[img]))
    if key in STREAMS:
        c, clip = STREAMS[key]; out.append(([c], clip))
    if key == 'jantar:0':
        out.append(([dict(t='fall', a=(318,0), b=(332,330), wa=20, wb=34, n=12, travel=3.2, along=True, len=8, w=.5, op=.3, dop=.25, bend=0)], [(295,0),(330,0),(355,200),(345,330),(315,330),(305,200)]))
    if key == 'jantar:1':
        out.append(([dict(t='spray', o=(700,300), wpx=200, n=22, v=7, life=(2.5, 4.5), len=1.4, w=1.4, op=.4)], [(540,120),(880,120),(880,330),(540,330)]))
        out.append(([dict(t='sea', poly=[(0,420),(150,420),(430,415),(520,390),(700,385),(760,420),(760,560),(600,520),(450,560),(300,600),(150,560),(0,560)], n=16, d=(.2,.05), life=(5, 9), len=4.5, w=.7, op=.3, dop=.35)], [(0,420),(150,420),(430,415),(520,390),(700,385),(760,420),(760,560),(600,520),(450,560),(300,600),(150,560),(0,560)]))
    if key == 'domingo:5':
        out.append(([dict(t='fall', a=(360,0), b=(395,440), wa=80, wb=110, n=30, travel=3.2, along=True, len=10, w=.8, op=.3, dop=.3, bend=0)], FALL))
        out.append(([dict(t='spray', o=(390,442), wpx=160, n=16, v=3, life=(2.5, 4), len=1.4, w=1.4, op=.35)], [(250,380),(530,380),(530,505),(250,505)]))
    return out

def inject(key):
    lines = open(F).read().split('\n')
    i = [n for n, l in enumerate(lines) if re.match(r"^(?:const PHOTOS=\{)?'" + re.escape(key) + "':", l)][0]; l = lines[i]
    l = re.sub(r'<g class="pfxw">.*?</g><!--/pfx-->', '', l)
    sy = systems(key)
    if sy:
        ex = life.people_polys(F, key) + [life.pts(q) for q in STILL.get(IMG.get(key), [])]
        pfx = 'P' + key.replace(':', '').replace('manha', 'm').replace('sabado', 's').replace('domingo', 'd')
        body = "".join(life.particles(f'{pfx}{j}', dict(c[0], img=A + 'img/' + IMG[key] + '.jpg'), clip, exclude=ex) for j, (c, clip) in enumerate(sy))
        wrap = f'<g class="pfxw">{body}</g><!--/pfx-->'
        k = l.index('<rect class="beat"') if '<rect class="beat"' in l else l.index('</g><!--/life-->')
        l = l[:k] + wrap + l[k:]
    lines[i] = l; open(F, 'w').write('\n'.join(lines))
    return len(sy)

def install_engine():
    h = open(F).read(); js = open(S + 'pfx_engine.js').read()
    h = re.sub(r'<script id="pfx-engine">.*?</script>\n?', '', h, flags=re.S)
    i = h.rindex('</body>'); h = h[:i] + f'<script id="pfx-engine">\n{js}</script>\n' + h[i:]
    open(F, 'w').write(h)

if __name__ == '__main__':
    install_engine()
    keys = sys.argv[1:] or sorted(set(list(SEA) + list(STREAMS) + [k for k, v in IMG.items() if v in WASH]))
    for k in keys: print(k, inject(k))
    h = open(F).read()
    open(S + 'gen/check.js', 'w').write('\n'.join(re.findall(r'<script[^>]*>(.*?)</script>', h, re.S)))
