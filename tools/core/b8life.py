"""Book 8 animation: palms sway on the avenue, marina water ripples, balcony flowers stir, distant sea ripples, the lamp glows."""
import sys, glob, os, pickle, numpy as np, cv2
S = '/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'; sys.path.insert(0, S)
import frames as F, windfx
W, H = 1600, 898
PREVIEW = len(sys.argv) > 2
def poly(*p):
    m = np.zeros((H, W), np.uint8); cv2.fillPoly(m, [np.array(p, np.int32)], 1); return m
def regions(idx):
    f = sorted(glob.glob(S + f'gen/hlcache/casa_{idx}_*.pkl'), key=os.path.getmtime)[-1]
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

if which in ('all', '1'):   # page 2: palm fronds sway on the seafront avenue
    B = F.load('b8p2.jpg'); b = B
    area = poly((0, 0), (420, 0), (420, 300), (330, 300), (300, 330), (0, 330))
    green = (b[..., 1] > b[..., 2] + 10) & (b[..., 1] > b[..., 0] * .92) & (F.sat(B) > 28) & (F.lum(B) > 50)
    w = (area & green).astype(np.float32)
    trunk = poly((95, 160), (150, 160), (150, 520), (95, 520)) | poly((290, 200), (335, 200), (335, 420), (290, 420))
    w = cv2.morphologyEx(w, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8)); w[trunk > 0] = 0; w[cv2.dilate(poly((360, 190), (540, 190), (600, 898), (250, 898)), np.ones((25, 25), np.uint8)) > 0] = 0
    w = keep_big(w > 0, 4000).astype(np.float32); w = cv2.GaussianBlur(w, (0, 0), 6)
    fr = F.sway(B, w, n=16, amp=2.2, lam=300.)
    mask = np.clip(cv2.GaussianBlur((w > .03).astype(np.float32), (0, 0), 2) * 1.2, 0, 1)
    out('casa:1', 'b8p2_lf', fr, mask, 4.0)

if which in ('all', '4'):   # page 5: the marina water ripples between the boats
    B = F.load('b8p5.jpg'); R = regions(4); b = B
    water = poly((0, 345), (1600, 330), (1600, 470), (1380, 470), (1380, 500), (0, 445))
    from hlmask import Page, sam
    marta = (Page('casa', 4).region([sam([940, 60, 1450, 898], [(1080, 200), (1180, 500), (1100, 850), (1000, 600)], [(800, 400), (1500, 300)], 'big')]) > 0).astype(np.uint8)
    people = cv2.dilate(R['desiludida'] | marta | R['telemovel'], np.ones((9, 9), np.uint8))
    blue = (F.lum(B) > 70) & ~((F.lum(B) > 225) & (F.sat(B) < 18))
    m = water & R['marina'] & blue.astype(np.uint8) & (1 - people) & (1 - cv2.dilate(R['barcos'], np.ones((9, 9), np.uint8)))
    m = keep_big(cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)), 1500)
    fr = F.ripple(B, m, n=16, near=1.4, far=.5, lam_near=34., lam_far=14., shine=.05, edge=5)
    out('casa:4', 'b8p5_ls', fr, cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.2), 6.0)

if which in ('all', '5'):   # page 6: geraniums on the balcony stir
    B = F.load('b8p6.jpg'); R = regions(5)
    w = R['flores'].astype(np.float32); w = cv2.GaussianBlur(w, (0, 0), 5)
    fr = F.sway(B, w, n=16, amp=1.4, lam=200.)
    mask = np.clip(cv2.GaussianBlur((w > .03).astype(np.float32), (0, 0), 2) * 1.2, 0, 1)
    out('casa:5', 'b8p6_lf', fr, mask, 4.0)

if which in ('all', '6'):   # page 7: the distant sea ripples
    B = F.load('b8p7.jpg'); R = regions(6)
    m = R['mar'] & (F.lum(B) > 90).astype(np.uint8)
    fr = F.ripple(B, m, n=16, near=.8, far=.3, lam_near=22., lam_far=10., shine=.05, edge=4)
    out('casa:6', 'b8p7_ls', fr, cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.2), 6.0)

if which in ('all', '7'):   # page 8: the lamp glows softly
    B = F.load('b8p8.jpg')
    g = np.zeros((H, W), np.float32); cv2.ellipse(g, (705, 120), (150, 130), 0, 0, 360, 1., -1); g = cv2.GaussianBlur(g, (0, 0), 40)
    fr = F.breathe(B, g, n=16, amp=.10)
    out('casa:7', 'b8p8_lg', fr, np.clip(g * 1.4, 0, 1), 5.0)
print('done')
