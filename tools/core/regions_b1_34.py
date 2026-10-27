import re
from PIL import Image, ImageDraw
S = '/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'
A = S + 'artifact-files/87e1712e-5e90-4175-b828-2581544915d4/'
k = 1600 / 1200
PAGES = {
 3: ('b1n3j', {
  'cozinha': [[(730,0),(1200,0),(1200,674),(700,674),(700,460),(735,390)]],
  'rita': [[(230,90),(330,70),(470,65),(520,130),(525,250),(510,310),(560,380),(580,560),(480,600),(260,640),(190,600),(190,440),(230,330),(240,250)]],
  'cafe bebe': [[(420,295),(520,295),(560,330),(565,410),(510,410),(440,380),(410,340)]],
  'cafe': [[(835,245),(1040,245),(1045,500),(840,500),(830,380)]],
  'quente': [[(440,262),(505,252),(512,322),(470,332),(440,310)]],
 }),
 4: ('b1n4j', {
  'rita': [[(565,70),(650,60),(740,90),(800,200),(810,300),(860,330),(880,480),(860,560),(600,560),(470,480),(480,400),(560,330),(555,250),(560,150)]],
  'come pao': [[(530,230),(630,215),(640,260),(590,290),(540,280)]],
  'pao bom': [[(270,450),(420,460),(520,510),(610,540),(600,600),(520,630),(430,600),(290,590),(270,520)]],
  'manteiga': [[(195,550),(290,550),(290,620),(200,620)]],
  'gosta': [[(575,95),(650,85),(700,120),(700,200),(640,230),(585,210),(570,150)]],
 }),
}
sx, sy = 465.8 / 1600, 260 / 898
f = A + 'index.html'
lines = open(f).read().split('\n')
sheet = Image.new('RGB', (1200, 1348), 'white')
for row, (n, (src, R)) in enumerate(PAGES.items()):
    im = Image.open(S + f'gen/{src}_1600.jpg').convert('RGB')
    im.save(A + f'img/b1p{n}.jpg', quality=88)
    prev = im.resize((1200, 674)); d = ImageDraw.Draw(prev)
    p = f'manha{n-1}'; defs, body = [], []
    for i, (key, polys) in enumerate(R.items()):
        for poly in polys: d.polygon(poly, outline=(255, 0, 0), width=3)
        pts = [" ".join(f"{x*k*sx:.1f},{y*k*sy:.1f}" for x, y in poly) for poly in polys]
        defs.append(f'<clipPath id="{p}c{i}">' + "".join(f'<polygon points="{s}"/>' for s in pts) + '</clipPath>')
        outl = "".join(f'<polygon points="{s}" fill="none" stroke="#FFE2B8" stroke-width="1.2" stroke-linejoin="round"/>' for s in pts)
        body.append("${o('" + key + "',`<use href=\"#" + p + "ph\" clip-path=\"url(#" + p + f"c{i})\"/>" + outl + "`)}")
    sheet.paste(prev, (0, 674 * row))
    svg = "<defs>" + "".join(defs) + "</defs>" + f'<image id="{p}ph" href="img/b1p{n}.jpg" x="0" y="0" width="465.8" height="260" preserveAspectRatio="none"/><rect class="dimmer" x="0" y="0" width="465.8" height="260" fill="#1B1512"/>' + "".join(body)
    key = f"'manha:{n-1}':"
    idx = [i for i, l in enumerate(lines) if l.startswith(key)]
    assert len(idx) == 1, key
    end = lines[idx[0]][lines[idx[0]].rfind('`}') + 2:]   # keep the original terminator ("," or "};")
    lines[idx[0]] = key + "{w:465.8,svg:()=>`" + svg + "`}" + end
sheet.resize((600, 674)).save(S + 'gen/regions_b1_34.jpg', quality=85)
h = '\n'.join(lines); open(f, 'w').write(h)
open(S + 'gen/check.js', 'w').write('\n'.join(re.findall(r'<script>(.*?)</script>', h, re.S)))
print('ok')
