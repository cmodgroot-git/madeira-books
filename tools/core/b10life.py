"""Book 10 animation: geraniums stir (p3), curtains dance in the breeze (p6), the wall lamp glows (p7), harbour ripples and city lights twinkle (p8)."""
import sys, glob, os, pickle, numpy as np, cv2
S = '/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'; sys.path.insert(0, S)
import frames as F, windfx
W, H = 1600, 898
PREVIEW = len(sys.argv) > 2
def poly(*p):
    m = np.zeros((H, W), np.uint8); cv2.fillPoly(m, [np.array(p, np.int32)], 1); return m
def regions(idx):
    f = sorted(glob.glob(S + f'gen/hlcache/novacasa_{idx}_*.pkl'), key=os.path.getmtime)[-1]
    return {k: (m > 0).astype(np.uint8) for k, m in pickle.load(open(f, 'rb'))[1]}
def keep_big(m, a=3000):
    n, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8)); o = np.zeros_like(m, np.uint8)
    for i in range(1, n):
        if st[i, 4] > a: o[lab == i] = 1
    return o
def out(key, stem, fr, mask, dur):
    if PREVIEW:
        B = fr[0]; cv2.imwrite(S + f'gen/{stem}_mask.jpg', cv2.cvtColor(np.clip(B * (1 - .6 * mask[..., None]) + np.array([255, 0, 0]) * .6 * mask[..., None], 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR)); return
    pa, box = F.save(fr, mask, stem.split('_')[0], stem.split('_')[1])
    windfx.add_layer(key, F.loop(pa, box, dur), stem); print(stem, box)
which = sys.argv[1] if len(sys.argv) > 1 else 'all'

if which in ('all', '2'):   # page 3: geraniums on the balcony stir
    B = F.load('b10p3.jpg'); b = B
    area = poly((900, 95), (1270, 80), (1295, 330), (1180, 300), (960, 300), (905, 230))
    leafy = ((b[..., 1] > b[..., 2] + 8) | (b[..., 0] > b[..., 1] + 40)) & (F.sat(B) > 35)
    area &= 1 - poly((1060, 0), (1200, 0), (1200, 175), (1060, 175))
    w = keep_big((area & leafy.astype(np.uint8)), 600).astype(np.float32)
    w = cv2.GaussianBlur(cv2.morphologyEx(w, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)), (0, 0), 5)
    fr = F.sway(B, w, n=16, amp=1.4, lam=200.)
    out('novacasa:2', 'b10p3_lf', fr, np.clip(cv2.GaussianBlur((w > .03).astype(np.float32), (0, 0), 2) * 1.2, 0, 1), 4.0)

if which in ('all', '5'):   # page 6: the white curtains dance in the breeze (doors stay still)
    B = F.load('b10p6.jpg'); R = regions(5)
    c = R['cortinas'].astype(np.uint8)
    ce = cv2.erode(c, np.ones((5, 5), np.uint8)).astype(np.float32)
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    w = cv2.GaussianBlur(ce, (0, 0), 6) * ce * np.clip(yy * 1.6, 0, 1)
    fr = F.sway(B, w, n=16, amp=5.0, lam=320., gust=.5, vertical=.15)
    m = cv2.GaussianBlur(ce, (0, 0), 1.2)
    fr = [f * m[..., None] + B * (1 - m[..., None]) for f in fr]
    out('novacasa:5', 'b10p6_lf', fr, np.clip(m, 0, 1), 4.0)

if which in ('all', '6'):   # page 7: the wall lamp glows softly
    B = F.load('b10p7.jpg')
    g = np.zeros((H, W), np.float32); cv2.ellipse(g, (1268, 60), (130, 120), 0, 0, 360, 1., -1); g = cv2.GaussianBlur(g, (0, 0), 35)
    fr = F.breathe(B, g, n=16, amp=.10)
    out('novacasa:6', 'b10p7_lg', fr, np.clip(g * 1.4, 0, 1), 5.0)

if which in ('all', '7'):   # page 8: moonlit harbour ripples, the town lights twinkle
    B = F.load('b10p8.jpg'); R = regions(7)
    sea = poly((1330, 400), (1600, 395), (1600, 540), (1440, 540), (1340, 505))
    cab = (poly((1460, 460), (1530, 460), (1530, 540), (1460, 540)) | poly((1340, 400), (1400, 400), (1400, 465), (1340, 465))) & (((B[..., 0] > B[..., 2] + 5) | (F.lum(B) < 70)).astype(np.uint8))
    cab = cv2.dilate(cv2.morphologyEx(cab, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)), np.ones((5, 5), np.uint8))
    sea &= (F.lum(B) > 45).astype(np.uint8) & (1 - cab)
    fr = F.ripple(B, sea, n=24, near=1.0, far=.5, lam_near=20., lam_far=10., shine=.08, edge=4)
    L = F.lum(B); town = R['luzes'] | poly((1050, 600), (1380, 560), (1380, 898), (1050, 898))
    warm = (L > 165) & (B[..., 0] > B[..., 2] + 40) & (town > 0)
    n, lab, st, cen = cv2.connectedComponentsWithStats(warm.astype(np.uint8))
    dots = [(cx / F.K, cy / F.K) for i, (cx, cy) in enumerate(cen) if i and 2 <= st[i, 4] <= 120 and not (cx < 1150 and cy < 470)]
    rng = np.random.default_rng(3); rng.shuffle(dots); dots = dots[:60]
    tw = F.twinkle(B, dots, n=24, amp=.35, r=4)
    fr = [np.where(sea[..., None] > 0, f, t) for f, t in zip(fr, tw)]
    m = np.clip(cv2.GaussianBlur(sea.astype(np.float32), (0, 0), 1.2) + cv2.GaussianBlur(cv2.dilate(town * 0 + 0, np.ones((3, 3), np.uint8)).astype(np.float32), (0, 0), 1), 0, 1)
    dm = np.zeros((H, W), np.float32)
    for x, y in dots: cv2.circle(dm, (int(x * F.K), int(y * F.K)), 9, 1., -1)
    m = np.clip(np.maximum(m, cv2.GaussianBlur(dm, (0, 0), 2)), 0, 1)
    out('novacasa:7', 'b10p8_ls', fr, m, 6.0)
print('done')
