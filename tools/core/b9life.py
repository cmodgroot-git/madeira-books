"""Book 9 animation: sea ripples (p1, p2, p8), underwater shimmer and bubbles (p4-p6), sun glow (p8)."""
import sys, glob, os, pickle, numpy as np, cv2
S = '/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'; sys.path.insert(0, S)
import frames as F, windfx
W, H = 1600, 898
PREVIEW = len(sys.argv) > 2
def poly(*p):
    m = np.zeros((H, W), np.uint8); cv2.fillPoly(m, [np.array(p, np.int32)], 1); return m
def regions(idx):
    f = sorted(glob.glob(S + f'gen/hlcache/garajau_{idx}_*.pkl'), key=os.path.getmtime)[-1]
    return {k: (m > 0).astype(np.uint8) for k, m in pickle.load(open(f, 'rb'))[1]}
def blue(B, mn=60):
    b = B; return ((b[..., 2] > b[..., 0] + 15) & (F.lum(B) > mn)).astype(np.uint8)
def out(key, stem, fr, mask, dur):
    if PREVIEW:
        B = fr[0]; cv2.imwrite(S + f'gen/{stem}_mask.jpg', cv2.cvtColor(np.clip(B * (1 - .6 * mask[..., None]) + np.array([255, 0, 0]) * .6 * mask[..., None], 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR)); return
    pa, box = F.save(fr, mask, stem.split('_')[0], stem.split('_')[1])
    windfx.add_layer(key, F.loop(pa, box, dur), stem); print(stem, box)
def soft(m, s=1.2): return cv2.GaussianBlur(m.astype(np.float32), (0, 0), s)
which = sys.argv[1] if len(sys.argv) > 1 else 'all'

if which in ('all', '0'):   # page 1: the open sea ripples
    B = F.load('b9p1.jpg'); R = regions(0)
    sea = poly((850, 330), (1600, 330), (1600, 898), (1430, 898), (1350, 700), (1270, 560), (1150, 470), (1000, 520), (850, 600))
    sea &= blue(B, 70) & (1 - cv2.dilate(R['estatua'] | R['cabine'] | R['teleferico'], np.ones((9, 9), np.uint8)))
    fr = F.ripple(B, sea, n=16, near=1.6, far=.4, lam_near=40., lam_far=12., shine=.05, edge=5)
    out('garajau:0', 'b9p1_ls', fr, soft(sea), 6.0)

if which in ('all', '1'):   # page 2: small waves along the shore
    B = F.load('b9p2.jpg'); R = regions(1)
    ppl = cv2.dilate(R['joao'] | R['marta'] | R['vermelha'], np.ones((11, 11), np.uint8))
    sea = poly((0, 300), (1600, 250), (1600, 690), (1100, 620), (700, 520), (300, 470), (0, 420))
    from hlmask import Page, sam
    pg = Page('garajau', 1); ana = (pg.region([sam([555, 105, 760, 820], [(650, 200), (650, 450), (640, 700)], [(480, 400)], 'big')]) > 0).astype(np.uint8)
    rita = (pg.region([sam([230, 90, 445, 820], [(330, 200), (330, 500)], [(500, 400)], 'big')]) > 0).astype(np.uint8)
    sea &= blue(B, 70) & (1 - ppl) & (1 - cv2.dilate(ana | rita, np.ones((11, 11), np.uint8)))
    fr = F.ripple(B, sea, n=16, near=2.0, far=.5, lam_near=46., lam_far=14., shine=.06, edge=5)
    out('garajau:1', 'b9p2_ls', fr, soft(sea), 6.0)

for idx, img in (('3', 'b9p4.jpg'), ('4', 'b9p5.jpg'), ('5', 'b9p6.jpg')):   # underwater: light shimmer near the surface
    if which not in ('all', idx): continue
    B = F.load('b9p6v2.jpg' if img == 'b9p6.jpg' else img); R = regions(int(idx))
    m = poly((0, 0), (1600, 0), (1600, 150), (0, 150)).astype(np.float32)
    keep = np.zeros((H, W), np.uint8)
    for k, v in R.items(): keep |= v
    ppl = poly((0, 0), (1, 0), (1, 1), (0, 1))
    if idx == '3': ppl = poly((560, 150), (920, 150), (920, 330), (560, 330))
    if idx == '4': ppl = poly((260, 140), (1250, 140), (1250, 560), (260, 560))
    if idx == '5': ppl = poly((300, 120), (900, 120), (900, 600), (300, 600))
    from hlmask import Page, sam
    pg = Page('garajau', int(idx)); boxes = {'3': [[560, 120, 930, 340]], '4': [[260, 120, 470, 330], [530, 120, 880, 470], [930, 140, 1250, 560]], '5': [[300, 100, 650, 520], [600, 220, 780, 480]]}[idx]
    who = np.zeros((H, W), np.uint8)
    for bx in boxes: who |= (pg.region([sam(bx, [((bx[0]+bx[2])//2, (bx[1]+bx[3])//2)], [], 'big')]) > 0).astype(np.uint8)
    who = cv2.GaussianBlur(cv2.dilate(who, np.ones((9, 9), np.uint8)).astype(np.float32), (0, 0), 4)
    m = np.clip(cv2.GaussianBlur(m, (0, 0), 30) * 1.4, 0, 1) * (1 - np.clip(who * 1.5, 0, 1))
    fr = F.ripple(B, (m > .05).astype(np.uint8), n=16, near=1.2, far=1.2, lam_near=60., lam_far=60., shine=.06, edge=8)
    out(f'garajau:{idx}', f'b9p{int(idx)+1}_lw', fr, m, 6.0)

if which in ('all', '7'):   # page 8: sea ripples, setting sun glows
    B = F.load('b9p8.jpg'); R = regions(7)
    sea = poly((930, 375), (1600, 375), (1600, 898), (1470, 898), (1400, 780), (1330, 640), (1230, 560), (1100, 520), (930, 560))
    b = B; green = (b[..., 1] > b[..., 2] + 8) & (b[..., 1] > b[..., 0] * .8)
    land = cv2.dilate(cv2.morphologyEx(green.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8)), np.ones((9, 9), np.uint8))
    sea &= (F.lum(B) > 60).astype(np.uint8) & (1 - land) & (1 - cv2.dilate(poly((1200, 330), (1330, 330), (1330, 520), (1200, 520)), np.ones((5, 5), np.uint8)))
    n_, lab, st, _ = cv2.connectedComponentsWithStats(sea); k_ = np.zeros_like(sea)
    for i_ in range(1, n_):
        if st[i_, 4] > 3000: k_[lab == i_] = 1
    sea = k_
    fr = F.ripple(B, sea, n=16, near=1.4, far=.4, lam_near=36., lam_far=12., shine=.06, edge=5)
    g = np.zeros((H, W), np.float32); cv2.circle(g, (1463, 350), 46, 1., -1); g = cv2.GaussianBlur(g, (0, 0), 18)
    fr = [np.clip(f * (1 + .12 * 0.5 * (1 - np.cos(2 * np.pi * i / 16)) * g[..., None]), 0, 255) for i, f in enumerate(fr)]
    out('garajau:7', 'b9p8_ls', fr, np.clip(np.maximum(soft(sea), g * 1.5), 0, 1), 6.0)
print('done')
