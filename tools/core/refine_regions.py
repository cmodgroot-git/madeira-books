"""Snap every tap region in Histórias da Madeira to the object's real edges (GrabCut seeded by the
existing polygon), rebuild the PHOTOS entries with a near-invisible outline, and write overlays."""
import re, sys, json
import numpy as np, cv2
from PIL import Image, ImageDraw

S = '/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'
A = S + 'artifact-files/87e1712e-5e90-4175-b828-2581544915d4/'
W0, H0, W, H = 465.8, 260.0, 1600, 898
sx, sy = W / W0, H / H0
only = sys.argv[1:]  # optional list of keys like manha:8

f = A + 'index.html'
lines = open(f).read().split('\n')
ent_re = re.compile(r"^(?:const PHOTOS=\{)?'((?:manha|sabado|domingo|jantar):\d+)':")
grp_re = re.compile(r"\$\{o\('([^']*)',`(.*?)`\)\}", re.S)
clip_re = re.compile(r'<clipPath id="([^"]+)">(.*?)</clipPath>', re.S)
poly_re = re.compile(r'<polygon points="([^"]+)"')

def parse_pts(s):
    return [tuple(map(float, p.split(','))) for p in s.split()]

def refine(img, poly_px):
    """GrabCut seeded by a rough polygon; returns list of refined polygons (px) or None."""
    h, w = img.shape[:2]
    pm = np.zeros((h, w), np.uint8)
    cv2.fillPoly(pm, [np.array(poly_px, np.int32)], 1)
    area = pm.sum()
    if area < 50: return None
    if area > 0.30 * w * h:          # big backgrounds (sky, room, sea): keep, they are areas not objects
        return None
    r = max(4, int(0.035 * np.sqrt(area)))
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*r+1, 2*r+1))
    inner = cv2.erode(pm, k)
    outer = cv2.dilate(pm, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (6*r+1, 6*r+1)))
    gc = np.full((h, w), cv2.GC_BGD, np.uint8)
    gc[outer == 1] = cv2.GC_PR_BGD
    gc[pm == 1] = cv2.GC_PR_FGD
    gc[inner == 1] = cv2.GC_PR_FGD
    x, y, bw, bh = cv2.boundingRect(np.array(poly_px, np.int32))
    pad = 6*r
    x0, y0, x1, y1 = max(0, x-pad), max(0, y-pad), min(w, x+bw+pad), min(h, y+bh+pad)
    sub = img[y0:y1, x0:x1].copy(); gsub = gc[y0:y1, x0:x1].copy()
    bgd = np.zeros((1, 65), np.float64); fgd = np.zeros((1, 65), np.float64)
    try:
        cv2.grabCut(sub, gsub, None, bgd, fgd, 5, cv2.GC_INIT_WITH_MASK)
    except cv2.error:
        return None
    m = np.zeros((h, w), np.uint8)
    m[y0:y1, x0:x1] = ((gsub == cv2.GC_FGD) | (gsub == cv2.GC_PR_FGD)).astype(np.uint8)
    m &= cv2.dilate(pm, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*r+1, 2*r+1)))  # stay near the seed
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    ratio = m.sum() / area
    if ratio < 0.35 or ratio > 1.15:
        return None
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cs = [c for c in cs if cv2.contourArea(c) > max(40, 0.04 * area)]
    if not cs: return None
    out = []
    for c in cs:
        a = cv2.approxPolyDP(c, 1.2, True).reshape(-1, 2)
        if len(a) >= 3: out.append([(float(px), float(py)) for px, py in a])
    return out or None

report = {}
overlays = []
for li, line in enumerate(lines):
    m = ent_re.match(line)
    if not m: continue
    key = m.group(1)
    if only and key not in only: continue
    prefix = line[:line.index("svg:()=>`") + len("svg:()=>`")]
    end = line[line.rfind('`}') :]
    body = line[len(prefix): line.rfind('`}')]
    img_path = re.search(r'href="(img/[^"]+)"', body).group(1)
    p = re.search(r'<image id="([^"]+)ph"', body).group(1)
    clips = {cid: [parse_pts(s) for s in poly_re.findall(inner)] for cid, inner in clip_re.findall(body)}
    img = cv2.cvtColor(np.array(Image.open(S + 'gen/masters/' + img_path.split('/')[-1]).convert('RGB')), cv2.COLOR_RGB2BGR)
    groups = []
    for gkey, inner in grp_re.findall(body):
        if 'class="gaze' in inner or 'class=\\"gaze' in inner:
            groups.append(('raw', "${o('" + gkey + "',`" + inner + "`)}")); continue
        cid = re.search(r'url\(#([^)]+)\)', inner).group(1)
        groups.append(('reg', gkey, clips[cid]))
    defs, outb, ov = [], [], []
    ci = 0; stats = []
    for g in groups:
        if g[0] == 'raw':
            outb.append(g[1]); continue
        _, gkey, polys = g
        newp = []
        for poly in polys:
            px = [(x*sx, y*sy) for x, y in poly]
            r = refine(img, px)
            stats.append((gkey, 'snap' if r else 'keep'))
            newp += r if r else [px]
        svgp = [" ".join(f"{x/sx:.1f},{y/sy:.1f}" for x, y in pp) for pp in newp]
        cid = f"{p}c{ci}"; ci += 1
        defs.append(f'<clipPath id="{cid}">' + "".join(f'<polygon points="{s}"/>' for s in svgp) + '</clipPath>')
        outl = "".join(f'<polygon class="rg" points="{s}"/>' for s in svgp)
        outb.append("${o('" + gkey + "',`<use href=\"#" + p + "ph\" clip-path=\"url(#" + cid + ")\"/>" + outl + "`)}")
        ov.append((gkey, newp))
    new_body = "<defs>" + "".join(defs) + "</defs>" + \
        f'<image id="{p}ph" href="{img_path}" x="0" y="0" width="465.8" height="260" preserveAspectRatio="none"/>' + \
        '<rect class="dimmer" x="0" y="0" width="465.8" height="260" fill="#1B1512"/>' + "".join(outb)
    lines[li] = prefix + new_body + end
    report[key] = stats
    overlays.append((key, img_path, ov))

h = '\n'.join(lines); open(f, 'w').write(h)
open(S + 'gen/check.js', 'w').write('\n'.join(re.findall(r'<script>(.*?)</script>', h, re.S)))

# overlay sheets: each region tinted in its own colour on the page
cols = [(255,80,80),(80,200,255),(120,255,120),(255,200,60),(220,120,255),(255,140,200),(80,255,220),(255,255,120)]
for key, img_path, ov in overlays:
    im = Image.open(S + 'gen/masters/' + img_path.split('/')[-1]).convert('RGB').resize((1200, 674))
    lay = Image.new('RGBA', im.size, (0,0,0,0)); d = ImageDraw.Draw(lay)
    for i, (gk, polys) in enumerate(ov):
        c = cols[i % len(cols)]
        for pp in polys:
            q = [(x*0.75, y*0.75) for x, y in pp]
            if len(q) >= 3: d.polygon(q, fill=c+(90,), outline=c+(255,))
    Image.alpha_composite(im.convert('RGBA'), lay).convert('RGB').save(S + f"gen/ov_{key.replace(':','_')}.jpg", quality=82)
print(json.dumps({k: [s for s in v] for k, v in report.items()}))
