"""Book 14 animation: banana leaves sway (p1), windsock flutters (p2), sea ripples below the flight (p6) and at the beach (p7), string lights twinkle (p8)."""
import sys, glob, os, pickle, numpy as np, cv2
S = '/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'; sys.path.insert(0, S)
import frames as F, windfx
W, H = 1600, 898; GX, GY = F.GX, F.GY
PREVIEW = len(sys.argv) > 2
def poly(*p):
    m = np.zeros((H, W), np.uint8); cv2.fillPoly(m, [np.array(p, np.int32)], 1); return m
def regions(idx):
    f = sorted(glob.glob(S + f'gen/hlcache/voo_{idx}_*.pkl'), key=os.path.getmtime)[-1]
    out = {}
    for k, m in pickle.load(open(f, 'rb'))[1]:
        for w in k.split(): out[w] = (m > 0).astype(np.uint8)
    return out
def out(key, stem, fr, mask, dur):
    if PREVIEW:
        B = fr[0]; cv2.imwrite(S + f'gen/{stem}_mask.jpg', cv2.cvtColor(np.clip(B * (1 - .6 * mask[..., None]) + np.array([255, 0, 0]) * .6 * mask[..., None], 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR)); return
    pa, box = F.save(fr, mask, stem.split('_')[0], stem.split('_')[1])
    windfx.add_layer(key, F.loop(pa, box, dur), stem); print(stem, box, flush=True)
def water(B, area, minus=(), grow=15):
    hsv = cv2.cvtColor(np.clip(B, 0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV)
    m = area & ((hsv[..., 0] > 70) & (hsv[..., 0] < 115) & (hsv[..., 1] > 25) & (hsv[..., 2] > 60)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((21, 21), np.uint8))
    for r in minus: m &= 1 - cv2.dilate(r, np.ones((grow, grow), np.uint8))
    m &= area
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lb, st, _ = cv2.connectedComponentsWithStats(m)
    return np.isin(lb, [i for i in range(1, n) if st[i, 4] > 3000]).astype(np.uint8)
which = sys.argv[1] if len(sys.argv) > 1 else 'all'

if which in ('all', '0'):   # page 1: banana leaves sway
    B = F.load('b14p1.jpg'); R = regions(0)
    hsv = cv2.cvtColor(np.clip(B, 0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV)
    leaves = R['bananeiras'] & poly((1080, 330), (1600, 330), (1600, 700), (1080, 700)) & ((hsv[..., 0] > 22) & (hsv[..., 0] < 55) & (hsv[..., 1] > 70) & (hsv[..., 2] > 90)).astype(np.uint8)
    leaves = cv2.morphologyEx(leaves, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    top = np.clip((720 - GY) / 330, 0, 1).astype(np.float32)
    w = cv2.GaussianBlur(leaves.astype(np.float32), (0, 0), 3) * top
    fr = F.sway(B, w, n=16, amp=2.6, lam=220., gust=.45, vertical=.3)
    out('voo:0', 'b14p1_bn', fr, np.clip(cv2.GaussianBlur(cv2.dilate(leaves, np.ones((9, 9), np.uint8)).astype(np.float32), (0, 0), 2), 0, 1), 3.4)

if which in ('all', '1'):   # page 2: the windsock flutters, stronger toward its open tail
    B = F.load('b14p2.jpg'); R = regions(1)
    ws = R['mangavento']
    tail = np.clip((1480 - GX) / 170, 0, 1).astype(np.float32)
    w = cv2.GaussianBlur(ws.astype(np.float32), (0, 0), 2) * tail
    fr = F.sway(B, w, n=16, amp=3.0, lam=60., gust=.5, vertical=.9)
    out('voo:1', 'b14p2_ws', fr, np.clip(cv2.GaussianBlur(cv2.dilate(ws, np.ones((11, 11), np.uint8)).astype(np.float32), (0, 0), 2), 0, 1), 1.6)

if which in ('all', '5'):   # page 6: the sea far below sparkles
    B = F.load('b14p6.jpg'); R = regions(5)
    sea = water(B, poly((900, 500), (1600, 500), (1600, 898), (1000, 898)), [R['voar']], grow=25)
    fr = F.ripple(B, sea, n=24, near=.9, far=.4, lam_near=16., lam_far=8., shine=.08, edge=3)
    out('voo:5', 'b14p6_sea', fr, np.clip(cv2.GaussianBlur(sea.astype(np.float32), (0, 0), 1.2), 0, 1), 5.0)

if which in ('all', '6'):   # page 7: little waves at the beach
    B = F.load('b14p7.jpg'); R = regions(6)
    sea = water(B, poly((0, 400), (1000, 400), (700, 560), (400, 650), (0, 800)), [R['aterram']], grow=25)
    fr = F.ripple(B, sea, n=24, near=1.4, far=.5, lam_near=24., lam_far=10., shine=.07, edge=4)
    out('voo:6', 'b14p7_sea', fr, np.clip(cv2.GaussianBlur(sea.astype(np.float32), (0, 0), 1.2), 0, 1), 5.0)

if which in ('all', '7'):   # page 8: the string lights twinkle, the dark sea glints
    B = F.load('b14p8.jpg')
    hsv = cv2.cvtColor(np.clip(B, 0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV)
    bulbs = (poly((680, 0), (1600, 0), (1600, 200), (680, 60)) & ((hsv[..., 2] > 225) & (hsv[..., 0] < 40))).astype(np.uint8)
    n, lb, st, cen = cv2.connectedComponentsWithStats(bulbs)
    dots = [(cen[i][0] / F.K, cen[i][1] / F.K) for i in range(1, n) if 15 < st[i, 4] < 900]
    fr = F.twinkle(B, dots, n=24, amp=.35, r=9, seed=4)
    m = np.zeros((H, W), np.uint8)
    for x, y in dots: cv2.circle(m, (int(x * F.K), int(y * F.K)), 20, 1, -1)
    out('voo:7', 'b14p8_lt', fr, np.clip(cv2.GaussianBlur(m.astype(np.float32), (0, 0), 4), 0, 1), 3.0)
print('done')
