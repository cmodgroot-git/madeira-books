"""Ambient 'life' layers for Histórias da Madeira pictures.

All coordinates given to the helpers are PREVIEW pixels on the 1200x674 preview of the
1600x898 page image; they are converted to the page svg's 465.8x260 user units here.
A page's layer is one <g class="life"> inserted right after the <image>, before the dimmer,
so it drifts with the picture, sits under the tap highlights and is covered when a word is tapped.
"""
import random, re, math
import numpy as np, cv2
from PIL import Image

KX, KY = 465.8 / 1200, 260 / 674          # preview px -> svg units
def P(x, y): return x * KX, y * KY
def pts(poly): return " ".join(f"{x*KX:.1f},{y*KY:.1f}" for x, y in poly)

def bbox(poly, pad=4):
    xs = [x for x, _ in poly]; ys = [y for _, y in poly]
    x0, y0 = min(xs) * KX - pad, min(ys) * KY - pad
    return x0, y0, (max(xs) - min(xs)) * KX + 2 * pad, (max(ys) - min(ys)) * KY + 2 * pad

# ---- effects -------------------------------------------------------------------------
def ripple(uid, img_id, poly, kind='water', strength=1.0, seed=3, exclude=(), soft=None):
    """Displace a clipped copy of the picture with slowly changing turbulence.
    kind: water (horizontal ripples), leaves (soft sway), sky (very slow drift), heat (rising shimmer)."""
    cfg = {
        'water':  ('0.018 0.09', '0.018 0.09;0.019 0.096;0.018 0.09', 0.7, 36),
        'leaves': ('0.03 0.03',  '0.03 0.03;0.031 0.032;0.03 0.03',   0.6, 36),
        'sky':    ('0.012 0.03', '0.012 0.03;0.013 0.032;0.012 0.03', 0.9, 60),
        'heat':   ('0.01 0.05',  '0.01 0.05;0.01 0.055;0.01 0.05',    0.45, 24),
        'fall':   ('0.09 0.012', '0.09 0.012;0.096 0.013;0.09 0.012', 1.1, 24),   # falling water: vertical streaks
        'surf':   ('0.006 0.045', '0.006 0.045;0.0065 0.049;0.006 0.045', 0.7, 28),
    }[kind]
    base, vals, scale, dur = cfg
    if soft is None and kind == 'surf': soft = 2.5      # feathered edge (svg units)
    x, y, w, h = bbox(poly, pad=4 + (3 * soft if soft else 0))
    edge = (f'<mask id="{uid}c" maskUnits="userSpaceOnUse" x="0" y="0" width="465.8" height="260">'
            f'<filter id="{uid}b" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="{soft}"/></filter>'
            f'<polygon points="{pts(poly)}" fill="#fff" filter="url(#{uid}b)"/></mask>') if soft else \
           f'<clipPath id="{uid}c"><polygon points="{pts(poly)}"/></clipPath>'
    return (edge +
            f'<filter id="{uid}f" filterUnits="userSpaceOnUse" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" color-interpolation-filters="sRGB">'
            f'<feTurbulence type="turbulence" baseFrequency="{base}" numOctaves="1" seed="{seed}">'
            f'<animate attributeName="baseFrequency" values="{vals}" dur="{dur}s" repeatCount="indefinite"/></feTurbulence>'
            f'<feDisplacementMap in="SourceGraphic" scale="{scale*strength:.2f}" xChannelSelector="R" yChannelSelector="G"/></filter>'
            + (f'<g mask="url(#{uid}c)">' if soft else f'<g clip-path="url(#{uid}c)">') + f'<use href="#{img_id}" filter="url(#{uid}f)"/>'
            + (f'<clipPath id="{uid}x">' + "".join(f'<polygon points="{g}"/>' for q in exclude for g in grow(q)) + '</clipPath>'
               f'<use href="#{img_id}" clip-path="url(#{uid}x)"/>' if exclude else '')
            + '</g>')

def grow(q, d=1.6, k=8):
    """Pad an svg-unit polygon by d units (rasterise at k px/unit, dilate, re-trace)."""
    p = np.array([tuple(map(float, t.split(','))) for t in q.split()])
    m = np.zeros((int(260*k)+1, int(465.8*k)+1), np.uint8)
    cv2.fillPoly(m, [np.round(p*k).astype(np.int32)], 255)
    r = int(d*k); m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*r+1, 2*r+1)))
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    out = []
    for c in cs:
        c = cv2.approxPolyDP(c, 0.15*k, True).reshape(-1, 2) / k
        out.append(" ".join(f"{x:.1f},{y:.1f}" for x, y in c))
    return out

def glow(uid, cx, cy, r, color='#FFD98A', lo=.10, hi=.22, dur=5, flicker=False):
    """Soft breathing light (lamp, moon, sun, window). flicker=True for a candle/lamp-like uneven pulse."""
    X, Y = P(cx, cy); R = r * KX
    hi = lo + (hi - lo) * .6; dur = dur * 2
    vals = f"{lo};{hi};{lo}"          # no flicker: every light breathes slowly (no high-frequency motion)
    return (f'<radialGradient id="{uid}g"><stop offset="0" stop-color="{color}" stop-opacity="1"/>'
            f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>'
            f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{R:.1f}" fill="url(#{uid}g)" opacity="{lo}" style="mix-blend-mode:screen">'
            f'<animate attributeName="opacity" values="{vals}" dur="{dur}s" repeatCount="indefinite"/></circle>')

def twinkle(uid, points, color='#FFE6A8', size=.55, hi=.6, rng=None):
    """Tiny lights fading in and out at different rhythms (town lights at night, stars, sparkles on water)."""
    rng = rng or random.Random(7); out = []
    for i, (px, py) in enumerate(points):
        X, Y = P(px, py); d = rng.uniform(14, 22); b = rng.uniform(0, d)
        r = size * rng.uniform(.8, 1.3); peak = hi * .6 * rng.uniform(.6, 1)
        out.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{r:.2f}" fill="{color}" opacity="0" style="mix-blend-mode:screen">'
                   f'<animate attributeName="opacity" values="0;{peak:.2f};0" dur="{d:.1f}s" begin="-{b:.1f}s" repeatCount="indefinite"/></circle>')
    return f'<g>{"".join(out)}</g>'

def steam(uid, x, y, height=40, wisps=3, color='#FFFFFF'):
    """Rising, fading wisps above a hot drink or food."""
    rng = random.Random(11); out = []
    X, Y = P(x, y); H = height * KY
    for i in range(wisps):
        dx = (i - (wisps - 1) / 2) * 1.6; d = rng.uniform(11, 14); b = i * d / wisps
        path = f"M{X+dx:.1f},{Y:.1f} c-1.5,{-H*.25:.1f} 1.5,{-H*.45:.1f} 0,{-H*.7:.1f} s1.2,{-H*.2:.1f} 0,{-H*.3:.1f}"
        out.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width=".7" stroke-linecap="round" opacity="0">'
                   f'<animate attributeName="opacity" values="0;.22;0" dur="{d:.1f}s" begin="-{b:.1f}s" repeatCount="indefinite"/>'
                   f'<animateTransform attributeName="transform" type="translate" values="0,2;0,-3" dur="{d:.1f}s" begin="-{b:.1f}s" repeatCount="indefinite"/></path>')
    return f'<g>{"".join(out)}</g>'

# ---- finding things in the picture ----------------------------------------------------
def bright_spots(img_path, rect, thresh=200, warm=True, max_n=30, min_gap=10):
    """Find small bright (optionally warm) points inside rect=(x0,y0,x1,y1) in preview px."""
    im = np.array(Image.open(img_path).convert('RGB').resize((1200, 674))).astype(np.int16)
    x0, y0, x1, y1 = rect; sub = im[y0:y1, x0:x1]
    lum = sub.mean(axis=2)
    mask = lum > thresh
    if warm: mask &= (sub[..., 0] >= sub[..., 2] + 15)
    mask = mask.astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats(mask)
    cand = [(st[i, cv2.CC_STAT_AREA], cen[i]) for i in range(1, n) if st[i, cv2.CC_STAT_AREA] <= 40]
    cand.sort(key=lambda t: -t[0]); out = []
    for _, (cx, cy) in cand:
        p = (cx + x0, cy + y0)
        if all((p[0]-q[0])**2 + (p[1]-q[1])**2 >= min_gap**2 for q in out): out.append(p)
        if len(out) >= max_n: break
    return out

# ---- inserting into the page ------------------------------------------------------------
def insert(index_html, key, layer):
    """Replace/insert the <g class="life"> layer of PHOTOS[key] (e.g. 'manha:8')."""
    h = open(index_html).read(); lines = h.split('\n')
    i = [n for n, l in enumerate(lines) if re.match(r"^(?:const PHOTOS=\{)?'" + re.escape(key) + "':", l)]
    assert len(i) == 1, key; l = lines[i[0]]
    l = re.sub(r'<g class="life">.*?</g><!--/life-->', '', l)
    m = re.search(r'(<image id="[^"]+ph"[^>]*/>)', l); assert m
    beat = ('<rect class="beat" x="0" y="0" width="465.8" height="260" fill="#000" opacity=".002">'
            '<animate attributeName="opacity" values=".002;.003;.002" dur="10s" repeatCount="indefinite"/></rect>')
    layer = re.sub(r'<rect class="beat".*?</rect>', '', layer) + beat   # keeps Chromium repainting animated filters
    l = l[:m.end()] + f'<g class="life">{layer}</g><!--/life-->' + l[m.end():]
    lines[i[0]] = l; open(index_html, 'w').write('\n'.join(lines))

PEOPLE = re.compile(r'\b(rita|ana|senhor|cansadas|estendem|gato|cao|feliz|gosta|obrigada|ve|come|bebe|compra|dia|vizinha|sai|acorda|tem|caminhar|comem|ouvem|acende|calca|da|empregado|pede|dividem|bonita)\b')
def people_polys(index_html, key):
    """svg-unit polygons of every tap region on the page that shows a person or animal (to keep them still)."""
    lines = open(index_html).read().split('\n')
    l = [x for x in lines if re.match(r"^(?:const PHOTOS=\{)?'" + re.escape(key) + "':", x)][0]
    clips = dict(re.findall(r'<clipPath id="([^"]+)">(.*?)</clipPath>', l))
    out = []
    for k, inner in re.findall(r"\$\{o\('([^']*)',`(.*?)`\)\}", l):
        if not PEOPLE.search(k): continue
        m = re.search(r'url\(#([^)]+)\)', inner)
        if m and m.group(1) in clips: out += re.findall(r'points="([^"]+)"', clips[m.group(1)])
    return out

def flow(uid, img_id, poly, direction, dist=30, dur=12, scale=2.0, base='0.08 0.02', exclude=(), seed=5):
    """Water that visibly flows: the ripple pattern drifts along `direction` (preview px vector, e.g. down a
    channel). Two copies, half a cycle apart, cross-fade so the loop restart is never seen."""
    dx, dy = direction; n = (dx*dx + dy*dy) ** .5; ux, uy = dx/n*dist, dy/n*dist      # svg units per cycle
    x, y, w, h = bbox(poly)
    fx, fy = x - (ux if ux > 0 else 0), y - (uy if uy > 0 else 0)                       # room upstream for the drift
    fw, fh = w + abs(ux), h + abs(uy)
    out = f'<clipPath id="{uid}c"><polygon points="{pts(poly)}"/></clipPath><g clip-path="url(#{uid}c)">'
    for j in (0, 1):
        b = j * dur / 2
        out += (f'<filter id="{uid}f{j}" filterUnits="userSpaceOnUse" x="{fx:.1f}" y="{fy:.1f}" width="{fw:.1f}" height="{fh:.1f}" color-interpolation-filters="sRGB">'
                f'<feTurbulence type="turbulence" baseFrequency="{base}" numOctaves="1" seed="{seed+j}" result="t"/>'
                f'<feOffset in="t" dx="0" dy="0" result="o">'
                f'<animate attributeName="dx" values="0;{ux:.1f}" dur="{dur}s" begin="-{b}s" repeatCount="indefinite"/>'
                f'<animate attributeName="dy" values="0;{uy:.1f}" dur="{dur}s" begin="-{b}s" repeatCount="indefinite"/></feOffset>'
                f'<feDisplacementMap in="SourceGraphic" in2="o" scale="{scale:.2f}" xChannelSelector="R" yChannelSelector="G"/></filter>'
                f'<use href="#{img_id}" filter="url(#{uid}f{j})" opacity="0">'
                f'<animate attributeName="opacity" values="0;1;0" dur="{dur}s" begin="-{b}s" repeatCount="indefinite"/></use>')
    if exclude:
        out += (f'<clipPath id="{uid}x">' + "".join(f'<polygon points="{g}"/>' for q in exclude for g in grow(q)) + '</clipPath>'
                f'<use href="#{img_id}" clip-path="url(#{uid}x)"/>')
    return out + '</g>'

def glints(uid, poly, direction, dist=50, dur=10, base='0.12 0.03', cut=.62, opacity=.55, seed=9):
    """Soft light glints on a water surface that travel along `direction` (preview px vector):
    turbulence thresholded to small bright streaks, drifting downstream, screen-blended. Two copies half a
    cycle apart cross-fade so the loop restart is never seen."""
    dx, dy = direction; n = (dx*dx + dy*dy) ** .5; ux, uy = dx/n*dist, dy/n*dist
    x, y, w, h = bbox(poly)
    fx, fy = x - (ux if ux > 0 else 0) - 2, y - (uy if uy > 0 else 0) - 2
    fw, fh = w + abs(ux) + 4, h + abs(uy) + 4
    a = 1 / (1 - cut)                                   # alpha = a*(R - cut)
    out = f'<clipPath id="{uid}c"><polygon points="{pts(poly)}"/></clipPath><g clip-path="url(#{uid}c)" style="mix-blend-mode:screen" opacity="{opacity}">'
    for j in (0, 1):
        b = j * dur / 2
        out += (f'<filter id="{uid}f{j}" filterUnits="userSpaceOnUse" x="{fx:.1f}" y="{fy:.1f}" width="{fw:.1f}" height="{fh:.1f}" color-interpolation-filters="sRGB">'
                f'<feTurbulence type="fractalNoise" baseFrequency="{base}" numOctaves="2" seed="{seed+j}" result="t"/>'
                f'<feColorMatrix in="t" type="matrix" values="0 0 0 0 1  0 0 0 0 0.97  0 0 0 0 0.88  {a:.2f} 0 0 0 {-a*cut:.2f}" result="g"/>'
                f'<feOffset in="g" dx="0" dy="0">'
                f'<animate attributeName="dx" values="0;{ux:.1f}" dur="{dur}s" begin="-{b}s" repeatCount="indefinite"/>'
                f'<animate attributeName="dy" values="0;{uy:.1f}" dur="{dur}s" begin="-{b}s" repeatCount="indefinite"/></feOffset></filter>'
                f'<rect x="{fx:.1f}" y="{fy:.1f}" width="{fw:.1f}" height="{fh:.1f}" fill="#fff" filter="url(#{uid}f{j})" opacity="0">'
                f'<animate attributeName="opacity" values="0;1;0" dur="{dur}s" begin="-{b}s" repeatCount="indefinite"/></rect>')
    return out + '</g>'

def _protect(uid, img_id, exclude):
    """Mask that hides overlay marks over protected areas (people, animals, ships). Overlays that only ADD light
    must be masked: redrawing the picture on top does not reliably cover animated, blended marks."""
    if not exclude: return '', ''
    m = (f'<mask id="{uid}m" maskUnits="userSpaceOnUse" x="0" y="0" width="465.8" height="260"><rect width="465.8" height="260" fill="#fff"/>'
         + "".join(f'<polygon points="{g}" fill="#000"/>' for q in exclude for g in grow(q)) + '</mask>')
    return m, f' mask="url(#{uid}m)"'

def _mark(X0, Y0, X1, Y1, ang, s0, s1, d, b, peak, ln, bend, color, width, keys="0;.25;.7;1", fade=.8):
    mark = f'M{-ln/2:.2f},0 q{ln/2:.2f},{-bend:.2f} {ln:.2f},0'
    return (f'<g opacity="0"><animate attributeName="opacity" values="0;{peak:.2f};{peak*fade:.2f};0" keyTimes="{keys}" dur="{d:.1f}s" begin="-{b:.1f}s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" values="{X0:.1f},{Y0:.1f};{X1:.1f},{Y1:.1f}" dur="{d:.1f}s" begin="-{b:.1f}s" repeatCount="indefinite"/>'
            f'<g transform="rotate({ang:.1f})"><path d="{mark}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round">'
            f'<animateTransform attributeName="transform" type="scale" values="{s0:.2f};{s1:.2f}" dur="{d:.1f}s" begin="-{b:.1f}s" repeatCount="indefinite"/></path></g></g>')

def streamlets(uid, poly, top, bottom, wtop, wbot, n=22, dur=(10, 14), peak=.4, color='#FFFBEA', seed=4,
               along=False, img_id=None, exclude=()):
    """Flow marks for narrow running water (levadas, streams, channels, waterfalls), preview px.
    Small pale ripple marks ride from `top` to `bottom` along the centreline, spread across the local width
    (wtop..wbot), growing toward the viewer and fading in and out. along=True turns the marks to lie along the
    flow (streaks on a waterfall) instead of across it."""
    rng = random.Random(seed)
    (tx, ty), (bx, by) = top, bottom
    ang = math.degrees(math.atan2(by - ty, bx - tx)) + (0 if along else 90)
    nx, ny = -(by - ty), (bx - tx); L_ = (nx*nx + ny*ny) ** .5; nx, ny = nx / L_, ny / L_
    mdef, matt = _protect(uid, img_id, exclude)
    out = mdef + f'<clipPath id="{uid}c"><polygon points="{pts(poly)}"/></clipPath><g clip-path="url(#{uid}c)"><g{matt} style="mix-blend-mode:screen">'
    for i in range(n):
        d = rng.uniform(*dur); b = (i + rng.random()) * d / n; f = rng.uniform(-.38, .38)
        X0, Y0 = P(tx + nx * f * wtop, ty + ny * f * wtop); X1, Y1 = P(bx + nx * f * wbot, by + ny * f * wbot)
        ln = rng.uniform(3.2, 5.5) * (2.2 if along else 1)
        out += _mark(X0, Y0, X1, Y1, ang, wtop / wbot, 1.0, d, b, peak * rng.uniform(.6, 1) / .8 * .8, ln,
                     rng.uniform(.6, 1.1) * (.3 if along else 1), color, .8)
    return out + '</g></g>'

def wash(uid, poly, sea, shore, n=26, dur=(10, 14), peak=.4, color='#FFFBEA', seed=6, img_id=None, exclude=()):
    """Shoreline marks (preview px): pale ripple marks lying along the shore drift in from the `sea` line to the
    `shore` line (both polylines left->right) and fade out as they reach the sand, like small waves arriving."""
    rng = random.Random(seed)
    def at(line, x):
        for (x0, y0), (x1, y1) in zip(line, line[1:]):
            if x0 <= x <= x1 or x1 <= x <= x0:
                t = 0 if x1 == x0 else (x - x0) / (x1 - x0); return y0 + t * (y1 - y0), (y1 - y0) / ((x1 - x0) or 1)
        (x0, y0), (x1, y1) = (line[0], line[1]) if x < line[0][0] else (line[-2], line[-1])
        return (y0 if x < line[0][0] else y1), (y1 - y0) / ((x1 - x0) or 1)
    xa = max(sea[0][0], shore[0][0]); xb = min(sea[-1][0], shore[-1][0])
    mdef, matt = _protect(uid, img_id, exclude)
    out = mdef + f'<clipPath id="{uid}c"><polygon points="{pts(poly)}"/></clipPath><g clip-path="url(#{uid}c)"><g{matt} style="mix-blend-mode:screen">'
    for i in range(n):
        d = rng.uniform(*dur); b = (i + rng.random()) * d / n; x = rng.uniform(xa, xb)
        ys, _ = at(sea, x); yl, sl = at(shore, x)
        y0 = ys + .15 * (yl - ys); y1 = yl - .08 * (yl - ys)
        X0, Y0 = P(x, y0); X1, Y1 = P(x, y1)
        ang = math.degrees(math.atan2(sl * KY, KX))
        s = .55 + .9 * y1 / 674
        out += _mark(X0, Y0, X1, Y1, ang, s * .85, s, d, b, peak * rng.uniform(.6, 1), rng.uniform(4, 7),
                     rng.uniform(.5, .9), color, .7, keys="0;.45;.8;1", fade=.75)
    return out + '</g></g>'

def particles(uid, cfg, clip, exclude=()):
    """A water particle system (drawn by the page's particle engine). cfg in PREVIEW px:
      stream / fall: a=(x,y) upstream, b=(x,y) downstream, wa/wb widths, n, travel (s), len, w, op, along
      shore: sea=[...], shore=[...] polylines left->right, n, T (wave period s), roll, len, w, op
      sea: poly=[...], n, d=(vx,vy) drift in svg units/s, life=(a,b), len, w, op, ang
      spray: o=(x,y) base centre, wpx width, n, v, life, len, w, op
    `clip` is the water polygon(s) in preview px; people/ships in `exclude` are masked out."""
    import json
    c = dict(cfg)
    for k in ('a', 'b', 'o'):
        if k in c: c[k] = [round(c[k][0]*KX, 2), round(c[k][1]*KY, 2)]
    for k in ('sea', 'shore', 'poly'):
        if k in c: c[k] = [[round(x*KX, 2), round(y*KY, 2)] for x, y in c[k]]
    for k in ('wa', 'wb'):
        if k in c: c[k] = round(c[k]*KX, 2)
    if 'wpx' in c: c['sw'] = round(c.pop('wpx')*KX, 2)          # spray spawn width
    if 'travel' in c: c['v'] = round(1 / c.pop('travel'), 4)
    c.setdefault('col', '#FFFDF2')
    if c.get('img') and 'dark' not in c:                      # crest colour = the water's own colour, darkened
        im = np.array(Image.open(c.pop('img')).convert('RGB').resize((1200, 674)))
        m = np.zeros((674, 1200), np.uint8)
        for q in (clip if clip and isinstance(clip[0][0], (list, tuple)) else [clip]):
            cv2.fillPoly(m, [np.array(q, np.int32)], 1)
        mean = im[m == 1].mean(axis=0) if m.any() else np.array([90, 130, 140])
        c['dark'] = '#%02x%02x%02x' % tuple(int(v * .55) for v in mean)
    c.pop('img', None)
    clips = clip if clip and isinstance(clip[0][0], (list, tuple)) else [clip]
    mdef, matt = _protect(uid, None, exclude)
    js = json.dumps(c, separators=(',', ':'))
    return (mdef + f'<clipPath id="{uid}c">' + "".join(f'<polygon points="{pts(q)}"/>' for q in clips) + '</clipPath>'
            f'<g clip-path="url(#{uid}c)"><g class="pfx"{matt} data-pfx=\'{js}\'></g></g>')


def frames(uid, srcs, dur=24, fade=.6):
    """Painted water frames. srcs: full-size RGBA images holding ONLY water pixels (AI-painted variants of the page,
    cut with a water mask), in the order of the motion (e.g. calm -> rising -> burst -> falling -> receding).
    Each state fades in ON TOP of the previous one (no dip back to the original picture); at the end of the cycle
    the last state fades out to reveal the first, which stays underneath. fade = share of each slot spent fading."""
    n = len(srcs); slot = 1 / n; e = .0005; spl = "0.45 0 0.55 1"
    def anim(points):
        pts_ = sorted(points); kt = ";".join(f"{t:.4f}" for t, _ in pts_); vs = ";".join(f"{v:.2f}" for _, v in pts_)
        return (f'<animate attributeName="opacity" values="{vs}" keyTimes="{kt}" calcMode="spline" '
                f'keySplines="{";".join([spl] * (len(pts_) - 1))}" dur="{dur}s" repeatCount="indefinite"/>')
    out = ''
    for i, s in enumerate(srcs):
        if i == 0:
            out += f'<image href="{s}" x="0" y="0" width="465.8" height="260" preserveAspectRatio="none"/>'
            continue
        t0 = i * slot; t1 = t0 + fade * slot
        if i < n - 1:     # fade in, stay until the last state is fully in, then switch off (hidden under it)
            off = (n - 1) * slot + fade * slot + e
            p = [(0, 0), (t0, 0), (t1, 1), (off, 1), (min(off + e, 1 - e), 0), (1, 0)]
        else:             # last state: fade in, hold, fade out at the end to reveal the first
            p = [(0, 0), (t0, 0), (t1, 1), (1 - fade * slot, 1), (1, 0)]
        out += (f'<image href="{s}" x="0" y="0" width="465.8" height="260" preserveAspectRatio="none" opacity="0">'
                + anim(p) + '</image>')
    return out


def sway(uid, src, dur=14, fade=.18):
    """Two-pose sway for clothing/hair (shapes must never be half-blended for long, or they ghost):
    rest pose (the picture) -> short smooth cross-fade -> breeze pose (src, RGBA, only the clothes) -> hold -> back."""
    f = fade / 2; spl = "0.45 0 0.55 1"
    kt = f"0;{.25-f:.3f};{.25+f:.3f};{.75-f:.3f};{.75+f:.3f};1"
    return (f'<image href="{src}" x="0" y="0" width="465.8" height="260" preserveAspectRatio="none" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{kt}" calcMode="spline" '
            f'keySplines="{";".join([spl]*5)}" dur="{dur}s" repeatCount="indefinite"/></image>')


def loop(uid, srcs, box, dur):
    """Seamless loop of morph frames (a closed cycle: the frame after the last is the first).
    srcs: RGBA images of the same region; box=(x,y,w,h) in 1600x898 image px. Adjacent frames are nearly
    identical, so each one cross-fades over the previous; just before the wrap all but the last switch off
    (hidden under it) and the last fades out to reveal the first, which stays underneath."""
    n = len(srcs); sx, sy = 465.8 / 1600, 260 / 898
    x, y, w, h = box[0] * sx, box[1] * sy, box[2] * sx, box[3] * sy
    img = lambda s, extra='': f'<image href="{s}" x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" preserveAspectRatio="none"{extra}'
    e = .0005; cut = (n - 1) / n
    out = img(srcs[0]) + '/>'
    for i in range(1, n):
        a, b = (i - 1) / n, i / n
        if i < n - 1:
            pts_ = [(0, 0), (a, 0), (b, 1), (cut + e, 1), (cut + 2 * e, 0), (1, 0)]
        else:
            pts_ = [(0, 0), (a, 0), (b, 1), (1 - e, 0), (1, 0)]
            pts_ = [(0, 0), (a, 0), (b, 1), (1, 0)]
        kt = ";".join(f"{t:.4f}" for t, _ in pts_); vs = ";".join(f"{v:g}" for _, v in pts_)
        out += img(srcs[i], ' opacity="0"') + f'><animate attributeName="opacity" values="{vs}" keyTimes="{kt}" dur="{dur}s" repeatCount="indefinite"/></image>'
    return out
