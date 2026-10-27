"""Exact cut-out highlights for Histórias da Madeira.

Each tappable region becomes a pixel mask (a small grey PNG inlined as a data URI inside an SVG <mask>),
cut with Segment Anything from box/point prompts, or drawn as a shape for big areas.

usage:
  hlmask.py sheet <story> [idx...]      per-word cut-out review sheet  -> conv/cut_<story>.jpg
  hlmask.py apply <story> [idx...]      write masks into index.html
Specs: SPECS[story][idx] = [(keys, [shapes...]), ...]; pages with no spec are seeded from their current polygons.
"""
import sys, re, io, json, base64, math, numpy as np, cv2
from PIL import Image, ImageDraw
S = '/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'
A = S + 'artifact-files/87e1712e-5e90-4175-b828-2581544915d4/'
sys.path.insert(0, S + 'sam/repo')
W, H = 1600, 898; SX, SY = 465.8 / W, 260 / H
BOOK = {'manha': 1, 'sabado': 2, 'domingo': 3, 'jantar': 4, 'passeio': 5, 'pico': 6, 'seixal': 7, 'casa': 8, 'garajau': 9, 'novacasa': 10, 'corridas': 11, 'carro': 12, 'veleiro': 13, 'voo': 14, 'festa': 15}

# ---- shapes (master px, 1600x898) ----
def sam(box, pos=(), neg=(), pick='best'): return ('sam', box, pos, neg, pick)
def poly(*pts): return ('poly', pts)
def ell(cx, cy, rx, ry): return ('ell', cx, cy, rx, ry)
def sub(sh): return ('sub', sh)      # cut this out of what came before
def post(sh): return ('post', sh)    # add back after the cuts
ALL = poly((0, 0), (W, 0), (W, H), (0, H))

_P = {}
def predictor(model='vit_h'):
    if model not in _P:
        import torch; torch.set_num_threads(4); torch.set_grad_enabled(False)
        from segment_anything import sam_model_registry, SamPredictor
        ck = {'vit_h': 'sam/vit_h.pth', 'vit_b': 'sam/vit_b.pth'}[model]
        net = sam_model_registry[model](checkpoint=S + ck)
        enc = net.image_encoder.to(torch.bfloat16); fwd = enc.forward
        enc.forward = lambda x: fwd(x.to(torch.bfloat16)).float()   # half the memory of the big encoder
        import gc; gc.collect()
        _P[model] = SamPredictor(net)
    return _P[model]

class Page:
    def __init__(self, story, idx, model='vit_h'):
        self.story, self.idx, self.model = story, idx, model
        h = open(A + 'index.html').read(); i = h.find(f"'{story}:{idx}':"); self.line = h[i:h.find('\n', i)]
        self.img = re.search(r'<image id="\w+ph" href="(img/[^"]+)"', self.line).group(1)
        name = self.img.split('/')[-1].rsplit('.', 1)[0]
        try: im = Image.open(S + f'gen/masters/{name}.jpg')
        except FileNotFoundError: im = Image.open(A + self.img)
        self.arr = np.asarray(im.convert('RGB').resize((W, H), Image.LANCZOS)); self._set = False
    def P(self):
        p = predictor(self.model)
        if not self._set: p.set_image(self.arr); self._set = True
        return p
    def sam_mask(self, box, pos=(), neg=(), pick='best', ref=None):
        pts = list(pos) + list(neg); lab = [1] * len(pos) + [0] * len(neg)
        ms, sc, _ = self.P().predict(point_coords=np.array(pts, float) if pts else None,
                                     point_labels=np.array(lab) if pts else None,
                                     box=np.array(box, float) if box is not None else None, multimask_output=True)
        if ref is not None:
            iou = [((m & ref).sum() / max(1, (m | ref).sum())) for m in ms]; k = int(np.argmax(iou))
        elif pick == 'big': k = int(np.argmax([m.sum() for m in ms]))
        else: k = int(np.argmax(sc))
        m = ms[k].astype(np.uint8)
        n, lb, st, _ = cv2.connectedComponentsWithStats(m)
        if n > 2:
            keep = [i for i in range(1, n) if st[i, 4] > 0.04 * st[1:, 4].max()]
            m = np.isin(lb, keep).astype(np.uint8)
        return m, (float(iou[k]) if ref is not None else None)
    def shape(self, sh):
        m = np.zeros((H, W), np.uint8)
        if sh[0] == 'poly': cv2.fillPoly(m, [np.array(sh[1], np.int32)], 1)
        elif sh[0] == 'ell': cv2.ellipse(m, (int(sh[1]), int(sh[2])), (int(sh[3]), int(sh[4])), 0, 0, 360, 1, -1)
        elif sh[0] == 'sam': m = self.sam_mask(*sh[1:])[0]
        elif sh[0] == 'mask': m = sh[1]
        return m
    def region(self, shapes):
        plus = [s for s in shapes if s[0] not in ('sub', 'post')]
        subs = [s[1] for s in shapes if s[0] == 'sub']; posts = [s[1] for s in shapes if s[0] == 'post']
        m = np.zeros((H, W), np.uint8)
        for s in plus: m |= self.shape(s)
        for s in subs: m &= 1 - cv2.dilate(self.shape(s), np.ones((5, 5), np.uint8))
        for s in posts: m |= self.shape(s)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        return m

# ---- existing markup ----
GRP = re.compile(r"\$\{o\('([^']+)',`(.*?)`\)\}", re.S)
def existing(line):
    """[(keys, kind, raw, [polygons in master px])]; kind is 'gaze' or 'region'."""
    defs = re.search(r'<defs>(.*?)</defs>', line, re.S); defs = defs.group(1) if defs else ''
    clips = {cid: [[(float(a) / SX, float(b) / SY) for a, b in (t.split(',') for t in pts.split())]
                   for pts in re.findall(r'points="([^"]+)"', body)]
             for cid, body in re.findall(r'<clipPath id="(\w+)">(.*?)</clipPath>', defs, re.S)}
    out = []
    for m in GRP.finditer(line):
        keys, inner = m.group(1), m.group(2)
        if 'class="gaze' in inner: out.append((keys, 'gaze', m.group(0), [])); continue
        cid = re.search(r'clip-path="url\(#(\w+)\)"', inner)
        polys = clips.get(cid.group(1), []) if cid else []
        if not polys: polys = [[(float(a) / SX, float(b) / SY) for a, b in (t.split(',') for t in pts.split())] for pts in re.findall(r'points="([^"]+)"', inner)]
        mk = re.search(r'mask="url\(#(\w+)\)"', inner)
        out.append((keys, 'region', m.group(0), polys, mk.group(1) if mk else None))
    return out

def auto_shapes(pg, polys):
    """Seed SAM from an old outline: per polygon, box + interior points, keep the mask closest to the outline."""
    parts = []; flags = []
    for p in polys:
        ref = np.zeros((H, W), np.uint8); cv2.fillPoly(ref, [np.array(p, np.int32)], 1)
        area = ref.sum()
        if area < 30: continue
        if area > 0.22 * W * H: parts.append(('mask', ref)); flags.append('area'); continue
        x, y, w, h = cv2.boundingRect(np.array(p, np.int32)); pad = int(0.04 * max(w, h))
        box = [max(0, x - pad), max(0, y - pad), min(W, x + w + pad), min(H, y + h + pad)]
        dt = cv2.distanceTransform(ref, cv2.DIST_L2, 5); pts = []
        for _ in range(3):
            yy, xx = np.unravel_index(np.argmax(dt), dt.shape)
            if dt[yy, xx] < 3: break
            pts.append((int(xx), int(yy))); cv2.circle(dt, (int(xx), int(yy)), int(max(dt[yy, xx] * 1.5, 8)), 0, -1)
        m, iou = pg.sam_mask(box, pts, (), 'best', ref.astype(bool))
        if iou < 0.5: parts.append(('mask', ref)); flags.append(f'iou{iou:.2f}')
        else: parts.append(('mask', m)); flags.append(f'{iou:.2f}')
    return parts, flags

# ---- output ----
def mask_png(m):
    ys, xs = np.nonzero(m)
    x0, y0, x1, y1 = max(0, xs.min() - 3), max(0, ys.min() - 3), min(W, xs.max() + 4), min(H, ys.max() + 4)
    f = cv2.GaussianBlur(m[y0:y1, x0:x1].astype(np.float32), (0, 0), 0.9)
    im = Image.fromarray((np.clip(f, 0, 1) * 255).astype(np.uint8)).resize((max(1, (x1 - x0) // 2), max(1, (y1 - y0) // 2)), Image.LANCZOS)
    im = im.quantize(16).convert('L')  # few grey levels: tiny file, soft edge
    b = io.BytesIO(); im.save(b, 'PNG', optimize=True)
    return base64.b64encode(b.getvalue()).decode(), (x0, y0, x1, y1)

def markup(prefix, regions, flagged=()):
    defs, groups = [], []
    regions = [(' '.join(k for k in keys.split() if k not in flagged), m) for keys, m in regions]
    regions = [(k, m) for k, m in regions if k]
    for n, (keys, m) in enumerate(regions):
        if m.sum() < 20: continue
        b64, (x0, y0, x1, y1) = mask_png(m)
        x, y, w, h = x0 * SX, y0 * SY, (x1 - x0) * SX, (y1 - y0) * SY
        mid = f'{prefix}m{n}'
        defs.append(f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}">'
                    f'<image href="data:image/png;base64,{b64}" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" preserveAspectRatio="none"/></mask>')
        ys, xs = np.nonzero(m)
        bx, by, bw, bh = xs.min() * SX, ys.min() * SY, (xs.max() - xs.min()) * SX, (ys.max() - ys.min()) * SY
        groups.append("${o('" + keys + "',`<use href=\"#" + prefix + "ph\" mask=\"url(#" + mid + ")\"/>"
                      f'<rect class="bb" x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="none"/>' + "`)}")
    return ''.join(defs), ''.join(groups)

def write(story, idx, regions, gazes):
    h = open(A + 'index.html').read(); i = h.find(f"'{story}:{idx}':"); j = h.find('\n', i); line = h[i:j]
    prefix = re.search(r'<image id="(\w+)ph"', line).group(1)
    fl = json.load(open(S + 'gen/flagged_actions.json')).get(f'{story}:{idx}', {})
    d, g = markup(prefix, regions, fl)
    olddefs = re.search(r'<defs>(.*?)</defs>', line, re.S)
    keep = re.sub(r'<clipPath id="\w+">.*?</clipPath>|<mask id="\w+".*?</mask>', '', olddefs.group(1), flags=re.S) if olddefs else ''
    if olddefs: line2 = line[:olddefs.start()] + '<defs>' + keep + d + '</defs>' + line[olddefs.end():]
    else: line2 = line.replace('svg:()=>`', 'svg:()=>`<defs>' + d + '</defs>', 1)
    dm = line2.find('<rect class="dimmer"'); de = line2.find('/>', dm) + 2
    tail = line2[line2.rfind('`)}') + 3:] if '`)}' in line2[de:] else line2[de:]
    line2 = line2[:de] + g + ''.join(gazes) + tail
    assert line2.count('`') % 2 == 0, 'backticks'
    open(A + 'index.html', 'w').write(h[:i] + line2 + h[j:])

def regions_for(story, idx, model='vit_h', specs=None):
    pg = Page(story, idx, model); ex = existing(pg.line)
    spec = (specs or {}).get(idx)
    regions, flags = [], []
    gazes = [e[2] for e in ex if e[1] == 'gaze']
    if spec is not None:
        for keys, shapes in spec: regions.append((keys, pg.region(shapes))); flags.append('spec')
    else:
        saved = json.load(open(S + 'gen/hl_polys.json'))[f'{story}:{idx}']
        import hlspecs; ovr = hlspecs.OVR; likes = []
        for keys, polys in saved:
            o = ovr.get((story, idx, keys))
            if o == 'ref':
                ref = np.zeros((H, W), np.uint8); [cv2.fillPoly(ref, [np.array(p, np.int32)], 1) for p in polys]
                regions.append((keys, ref)); flags.append('ref'); continue
            if isinstance(o, tuple) and o[0] == 'like': likes.append((len(regions), o[1])); regions.append((keys, None)); flags.append('like'); continue
            if isinstance(o, tuple) and o[0] == 'area': regions.append((keys, pg.region(o[1]))); flags.append('area,fix' + (',keep=' + '/'.join(o[2]) if len(o) > 2 else '')); continue
            if o is not None: regions.append((keys, pg.region(o))); flags.append('fix'); continue
            shapes, fl = auto_shapes(pg, polys)
            regions.append((keys, pg.region(shapes) if shapes else np.zeros((H, W), np.uint8))); flags.append(','.join(fl))
        for n, other in likes:
            src = np.zeros((H, W), np.uint8)
            for ok in other.split('|'): src |= [m for k, m in regions if k == ok][0]
            regions[n] = (regions[n][0], src); flags[n] = 'like ' + other
    # big areas give way to objects that cross their edge (a person standing in a window), keep those wholly inside (the sun in the sky)
    for n, ((keys, m), fl) in enumerate(zip(regions, flags)):
        if 'area' not in fl: continue
        keep = fl.split('keep=')[1].split('/') if 'keep=' in fl else []
        for k2, o in [r for q, r in enumerate(regions) if q != n and 'area' not in flags[q] and 'like' not in flags[q] and r[0] not in keep]:
            inter = (o & m).sum()
            if 0 < inter < 0.9 * o.sum() or (inter > 0.9 * o.sum() and o.sum() > 0.012 * W * H): m = m & (1 - cv2.dilate(o, np.ones((5, 5), np.uint8)))
        regions[n] = (keys, m)
    return pg, regions, flags, gazes

def cached(story, idx, model, specs):
    import hashlib, os, pickle
    import hlspecs
    key = hashlib.md5((repr((specs or {}).get(idx)) + repr(sorted((k, repr(v)) for k, v in hlspecs.OVR.items() if k[0] == story and k[1] == idx)) + 'r2' + model + str(os.path.getmtime(S + 'gen/hl_polys.json'))).encode()).hexdigest()[:10]
    f = S + f'gen/hlcache/{story}_{idx}_{key}.pkl'
    if os.path.exists(f): return pickle.load(open(f, 'rb'))
    os.makedirs(S + 'gen/hlcache', exist_ok=True)
    pg, regions, flags, gazes = regions_for(story, idx, model, specs)
    res = (pg.arr, regions, flags, gazes); pickle.dump(res, open(f, 'wb')); return res

def sheet(story, pages, model='vit_h', specs=None, out=None):
    tiles = []; report = []
    for idx in pages:
        arr, regions, flags, _ = cached(story, idx, model, specs)
        for (keys, m), fl in zip(regions, flags):
            a = arr.astype(np.float32); mm = m[..., None].astype(np.float32)
            o = a * mm + a * (1 - mm) * 0.22
            cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            o = o.astype(np.uint8).copy(); cv2.drawContours(o, cs, -1, (255, 60, 60), 3)
            im = Image.fromarray(o).resize((480, 269)); d = ImageDraw.Draw(im)
            d.rectangle([0, 0, 480, 16], fill=(0, 0, 0)); d.text((4, 3), f'p{idx+1} {keys}  [{fl}]', fill=(255, 255, 0))
            tiles.append(im); report.append((idx, keys, fl))
    cols = 4; rows = (len(tiles) + cols - 1) // cols
    Sh = Image.new('RGB', (480 * cols, 269 * rows))
    for n, t in enumerate(tiles): Sh.paste(t, ((n % cols) * 480, (n // cols) * 269))
    out = out or S + f'conv/cut_{story}_{"_".join(map(str, pages))}.jpg'; Sh.save(out, quality=80)
    return out, report

def apply(story, pages, model='vit_h', specs=None):
    for idx in pages:
        arr, regions, flags, gazes = cached(story, idx, model, specs)
        h = open(A + 'index.html').read(); i = h.find(f"'{story}:{idx}':"); line = h[i:h.find('\n', i)]
        gazes = [e[2] for e in existing(line) if e[1] == 'gaze']
        extra = (specs or {}).get(('gaze', idx), [])
        write(story, idx, regions, gazes + extra); print(story, idx, [k for k, _ in regions], flush=True)

if __name__ == '__main__':
    mode, story = sys.argv[1], sys.argv[2]
    pages = [int(x) for x in sys.argv[3:]] or list(range(9 if story == 'manha' else 8))
    import hlspecs
    specs = hlspecs.SPECS.get(story, {})
    model = 'vit_h' if __import__('os').path.exists(S + 'sam/vit_h.pth') and __import__('os').path.getsize(S + 'sam/vit_h.pth') > 2e9 else 'vit_b'
    if mode == 'sheet': print(sheet(story, pages, model, specs))
    else: apply(story, pages, model, specs)
