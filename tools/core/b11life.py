"""Book 11 animation: sea ripples in the V (p1), flags wave (p3), exhaust smoke drifts (p4), rain falls (p5), chequered flag waves (p6), sea sparkles past the van (p8)."""
import sys, glob, os, re, pickle, numpy as np, cv2
S = '/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'; sys.path.insert(0, S)
import frames as F, windfx
from PIL import Image
W, H = 1600, 898; GX, GY = F.GX, F.GY
PREVIEW = len(sys.argv) > 2
def poly(*p):
    m = np.zeros((H, W), np.uint8); cv2.fillPoly(m, [np.array(p, np.int32)], 1); return m
def regions(idx):
    f = sorted(glob.glob(S + f'gen/hlcache/corridas_{idx}_*.pkl'), key=os.path.getmtime)[-1]
    out = {}
    for k, m in pickle.load(open(f, 'rb'))[1]:
        for w in k.split(): out[w] = (m > 0).astype(np.uint8)
    return out
def out(key, stem, fr, mask, dur):
    if PREVIEW:
        B = fr[0]; cv2.imwrite(S + f'gen/{stem}_mask.jpg', cv2.cvtColor(np.clip(B * (1 - .6 * mask[..., None]) + np.array([255, 0, 0]) * .6 * mask[..., None], 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR)); return
    pa, box = F.save(fr, mask, stem.split('_')[0], stem.split('_')[1])
    windfx.add_layer(key, F.loop(pa, box, dur), stem); print(stem, box, flush=True)
def flag(B, area, amp=4., lam=90.):
    yy = np.clip((GX - area[0]) / (area[2] - area[0]), 0, 1).astype(np.float32)   # pole side still, free end flutters
    m = poly((area[0], area[1]), (area[2], area[1]), (area[2], area[3]), (area[0], area[3])).astype(np.float32)
    return m, yy
which = sys.argv[1] if len(sys.argv) > 1 else 'all'

if which in ('all', '0'):   # page 1: the sea in the V ripples
    B = F.load('b11p1v2.jpg'); R = regions(0)
    sea = R['mar'] & (F.lum(B) > 60).astype(np.uint8)
    sea = cv2.erode(sea, np.ones((3, 3), np.uint8))
    fr = F.ripple(B, sea, n=24, near=.9, far=.5, lam_near=18., lam_far=10., shine=.07, edge=3)
    out('corridas:0', 'b11p1_sea', fr, np.clip(cv2.GaussianBlur(sea.astype(np.float32), (0, 0), 1.2), 0, 1), 6.0)

def flags(B, boxes):
    w = np.zeros((H, W), np.float32)
    for x0, y0, x1, y1, pole_right in boxes:
        m = poly((x0, y0), (x1, y0), (x1, y1), (x0, y1)).astype(np.float32)
        t = np.clip(((x1 - GX) if pole_right else (GX - x0)) / (x1 - x0), 0, 1)
        w = np.maximum(w, m * t)
    return cv2.GaussianBlur(w, (0, 0), 3)

if which in ('all', '2'):   # page 3: the marshal's two flags flutter
    B = F.load('b11p3.jpg'); R = regions(2)
    fl = cv2.dilate(R['bandeira'], np.ones((5, 5), np.uint8))
    w = flags(B, [(640, 295, 745, 405, True), (840, 285, 932, 395, False)]) * cv2.GaussianBlur(fl.astype(np.float32), (0, 0), 2)
    fr = F.sway(B, w, n=16, amp=3.5, lam=70., gust=.5, vertical=.6)
    out('corridas:2', 'b11p3_fl', fr, np.clip(cv2.GaussianBlur(fl.astype(np.float32), (0, 0), 1.5), 0, 1), 1.6)

if which in ('all', '3'):   # page 4: the blue exhaust smoke drifts and swells
    B = F.load('b11p4.jpg')
    g = np.zeros((H, W), np.float32)
    for cx, cy, rx, ry in [(925, 565, 70, 60), (1265, 585, 65, 55), (795, 425, 60, 32), (890, 445, 45, 26)]:
        cv2.ellipse(g, (cx, cy), (rx, ry), 0, 0, 360, 1., -1)
    g = cv2.GaussianBlur(g, (0, 0), 14)
    smoky = np.clip((F.lum(B) - 150) / 60, 0, 1) * np.clip((B[..., 2] - B[..., 0]) / 25, 0, 1)
    w = g * cv2.GaussianBlur(smoky.astype(np.float32), (0, 0), 4)
    w = w / max(w.max(), 1e-3)
    fr = F.sway(B, w, n=16, amp=6., lam=140., gust=.6, vertical=.7)
    out('corridas:3', 'b11p4_sm', fr, np.clip(g * 1.3, 0, 1) * np.clip(w * 3, 0, 1), 2.4)

def streak_tile(T, count, length, width, slope, seed):
    rng = np.random.default_rng(seed); t = np.zeros((T * 3, T * 3), np.float32)
    for _ in range(count):
        x, y = rng.uniform(0, T, 2); L = length * rng.uniform(.6, 1.2); a = rng.uniform(.5, 1)
        for ox in (0, T, 2 * T):
            for oy in (0, T, 2 * T):
                cv2.line(t, (int(x + ox), int(y + oy)), (int(x + ox + slope * L), int(y + oy + L)), a, width, cv2.LINE_AA)
    return cv2.GaussianBlur(t[T:2 * T, T:2 * T], (0, 0), .6)
def rain_layer(n, layers, keep):
    res = []
    for k in range(n):
        A = np.zeros((H, W), np.float32)
        for T, count, length, width, slope, tiles_down, alpha, seed in layers:
            tile = streak_tile(T, count, length, width, slope, seed)
            dy = tiles_down * T * k / n; dx = slope * dy
            big = np.tile(tile, (H // T + 2, W // T + 2)); ox = int(round(-dx)) % T; oy = int(round(-dy)) % T
            A = np.maximum(A, big[oy:oy + H, ox:ox + W] * alpha)
        res.append(A * keep)
    return res
def save_rgba(frames_a, col, base, name, key, dur):
    U = np.max(frames_a, 0); ys, xs = np.nonzero(U > .01); x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    for f in os.listdir(F.I):
        if re.match(rf'{base}_{name}\d\d\.webp$', f): os.remove(F.I + f)
    w, h = int((x1 - x0) * .75), int((y1 - y0) * .75); pa = []
    for k, a in enumerate(frames_a):
        rgb = np.zeros((y1 - y0, x1 - x0, 3), np.uint8); rgb[:] = col; p = f'{base}_{name}{k:02d}.webp'
        Image.fromarray(np.dstack([rgb, (np.clip(a[y0:y1, x0:x1], 0, 1) * 255).astype(np.uint8)]), 'RGBA').resize((w, h), Image.LANCZOS).save(F.I + p, quality=80, method=6); pa.append('img/' + p)
    windfx.add_layer(key, F.loop(pa, (int(x0), int(y0), int(x1 - x0), int(y1 - y0)), dur), f'{base}_{name}'); print(base, name, len(pa), flush=True)

if which in ('all', '4'):   # page 5: drizzle falls in front of the valley, not over Rita and her kart
    B = F.load('b11p5.jpg'); R = regions(4)
    keep = 1 - cv2.GaussianBlur(cv2.dilate(R['piao'], np.ones((15, 15), np.uint8)).astype(np.float32), (0, 0), 3)
    LAY = [(180, 22, 31, 1, -.22, 3, .26, 21), (288, 12, 62, 2, -.26, 5, .32, 22)]
    fa = rain_layer(16, LAY, keep)
    if PREVIEW: cv2.imwrite(S + 'gen/b11p5_rain.jpg', cv2.cvtColor(np.clip(B * (1 - fa[3][..., None]) + 240 * fa[3][..., None], 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
    else: save_rgba(fa, (232, 238, 245), 'b11p5', 'rn', 'corridas:4', 1.2)

if which in ('all', '5'):   # page 6: the chequered flag waves
    B = F.load('b11p6v2.jpg')
    fl = poly((852, 345), (968, 275), (1012, 410), (905, 458)) & ((F.lum(B) < 90) | (F.lum(B) > 200)).astype(np.uint8)
    fl = cv2.morphologyEx(fl, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8)); fl = cv2.dilate(fl, np.ones((5, 5), np.uint8))
    w = flags(B, [(850, 270, 1015, 460, True)]) * cv2.GaussianBlur(fl.astype(np.float32), (0, 0), 2)
    fr = F.sway(B, w, n=16, amp=4.5, lam=80., gust=.5, vertical=.6)
    out('corridas:5', 'b11p6_fl', fr, np.clip(cv2.GaussianBlur(fl.astype(np.float32), (0, 0), 1.5), 0, 1), 1.4)

if which in ('all', '7'):   # page 8: the sea glitters past the left window
    B = F.load('b11p8.jpg')
    sea = poly((0, 346), (212, 346), (194, 440), (0, 446)) & (F.lum(B) > 60).astype(np.uint8)
    sea = cv2.morphologyEx(sea, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    fr = F.ripple(B, sea, n=24, near=1.2, far=.5, lam_near=22., lam_far=10., shine=.09, edge=4)
    out('corridas:7', 'b11p8_sea', fr, np.clip(cv2.GaussianBlur(sea.astype(np.float32), (0, 0), 1.2), 0, 1), 5.0)
print('done')
