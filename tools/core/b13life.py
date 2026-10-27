"""Book 13 animation: the sea ripples on the marina (p2), the harbour exit (p3), the dolphin sea (p5) and the anchorage (p6)."""
import sys, glob, os, pickle, numpy as np, cv2
S = '/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'; sys.path.insert(0, S)
import frames as F, windfx
W, H = 1600, 898; GX, GY = F.GX, F.GY
PREVIEW = len(sys.argv) > 2
def poly(*p):
    m = np.zeros((H, W), np.uint8); cv2.fillPoly(m, [np.array(p, np.int32)], 1); return m
def regions(idx):
    f = sorted(glob.glob(S + f'gen/hlcache/veleiro_{idx}_*.pkl'), key=os.path.getmtime)[-1]
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
    m = area & ((hsv[..., 0] > 70) & (hsv[..., 0] < 108) & (hsv[..., 1] > 10) & (hsv[..., 2] > 110)).astype(np.uint8)
    for r in minus: m &= 1 - cv2.dilate(r, np.ones((grow, grow), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((21, 21), np.uint8))
    for r in minus: m &= 1 - cv2.dilate(r, np.ones((grow, grow), np.uint8))
    m &= area
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lb, st, _ = cv2.connectedComponentsWithStats(m)
    return np.isin(lb, [i for i in range(1, n) if st[i, 4] > 3000]).astype(np.uint8)
which = sys.argv[1] if len(sys.argv) > 1 else 'all'

if which in ('all', '1'):   # page 2: marina water around the boat
    B = F.load('b13p2.jpg'); R = regions(1)
    sea = water(B, poly((0, 330), (1600, 330), (1600, 898), (0, 898)), [R['veleiro'], R['joao'], R['cais'], R['sofia']])
    fr = F.ripple(B, sea, n=24, near=1.3, far=.5, lam_near=24., lam_far=10., shine=.07, edge=4)
    out('veleiro:1', 'b13p2_sea', fr, np.clip(cv2.GaussianBlur(sea.astype(np.float32), (0, 0), 1.2), 0, 1), 5.0)

if which in ('all', '2'):   # page 3: open water past the harbour wall
    B = F.load('b13p3.jpg'); R = regions(2)
    sea = water(B, poly((0, 420), (1600, 440), (1600, 898), (0, 898)), [R['inclina'], R['leme']])
    sea &= 1 - poly((580, 290), (1430, 290), (1430, 700), (580, 700))
    fr = F.ripple(B, sea, n=24, near=1.6, far=.5, lam_near=30., lam_far=10., shine=.07, edge=4)
    out('veleiro:2', 'b13p3_sea', fr, np.clip(cv2.GaussianBlur(sea.astype(np.float32), (0, 0), 1.2), 0, 1), 4.0)

if which in ('all', '4'):   # page 5: the sea around the dolphins
    B = F.load('b13p5.jpg'); R = regions(4)
    sea = water(B, poly((0, 320), (1600, 320), (1600, 898), (0, 898)), [R['golfinhos'], R['aponta']], grow=25)
    sea &= 1 - poly((560, 290), (1600, 290), (1600, 898), (690, 898))   # leave the boat and its wake alone
    fr = F.ripple(B, sea, n=24, near=1.4, far=.4, lam_near=26., lam_far=10., shine=.07, edge=5)
    out('veleiro:4', 'b13p5_sea', fr, np.clip(cv2.GaussianBlur(sea.astype(np.float32), (0, 0), 1.2), 0, 1), 4.5)

if which in ('all', '5'):   # page 6: the anchorage
    B = F.load('b13p6.jpg'); R = regions(5)
    sea = water(B, poly((0, 380), (1600, 400), (1600, 898), (0, 898)), [R['mergulha']], grow=31)
    sea &= 1 - poly((740, 330), (1120, 330), (1120, 570), (740, 570))
    fr = F.ripple(B, sea, n=24, near=1.3, far=.4, lam_near=24., lam_far=10., shine=.07, edge=4)
    out('veleiro:5', 'b13p6_sea', fr, np.clip(cv2.GaussianBlur(sea.astype(np.float32), (0, 0), 1.2), 0, 1), 5.0)
print('done')
