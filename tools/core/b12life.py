"""Book 12 animation: coffee steam (p1), pennants flutter (p2), flowers sway (p6), the vine over the roof sways (p8)."""
import sys, glob, os, pickle, numpy as np, cv2
S = '/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'; sys.path.insert(0, S)
import frames as F, windfx
W, H = 1600, 898; GX, GY = F.GX, F.GY
PREVIEW = len(sys.argv) > 2
def poly(*p):
    m = np.zeros((H, W), np.uint8); cv2.fillPoly(m, [np.array(p, np.int32)], 1); return m
def regions(idx):
    f = sorted(glob.glob(S + f'gen/hlcache/carro_{idx}_*.pkl'), key=os.path.getmtime)[-1]
    out = {}
    for k, m in pickle.load(open(f, 'rb'))[1]:
        for w in k.split(): out[w] = (m > 0).astype(np.uint8)
    return out
def out(key, stem, fr, mask, dur):
    if PREVIEW:
        B = fr[0]; cv2.imwrite(S + f'gen/{stem}_mask.jpg', cv2.cvtColor(np.clip(B * (1 - .6 * mask[..., None]) + np.array([255, 0, 0]) * .6 * mask[..., None], 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR)); return
    pa, box = F.save(fr, mask, stem.split('_')[0], stem.split('_')[1])
    windfx.add_layer(key, F.loop(pa, box, dur), stem); print(stem, box, flush=True)
which = sys.argv[1] if len(sys.argv) > 1 else 'all'

if which in ('all', '0'):   # page 1: steam curls up from both coffees
    B = F.load('b12p1v2.jpg')
    a = F.steam(B, 602, 568, height=55, width=24, n=24, strands=2, alpha=.45, seed=3)
    b = F.steam(B, 900, 572, height=45, width=24, n=24, strands=2, alpha=.45, seed=8, lean=-4)
    fr = [np.clip(x + (y - B), 0, 255) for x, y in zip(a, b)]
    m = poly((570, 505), (640, 505), (640, 572), (570, 572)) | poly((865, 520), (935, 520), (935, 576), (865, 576))
    out('carro:0', 'b12p1_st', fr, np.clip(cv2.GaussianBlur(m.astype(np.float32), (0, 0), 6), 0, 1), 3.0)

if which in ('all', '1'):   # page 2: the pennant strings flutter
    B = F.load('b12p2.jpg')
    band = poly((0, 198), (765, 205), (765, 232), (0, 228)) & (F.sat(B) > 55).astype(np.uint8)
    band = cv2.dilate(band, np.ones((7, 7), np.uint8))
    w = cv2.GaussianBlur(band.astype(np.float32), (0, 0), 2)
    fr = F.sway(B, w, n=16, amp=2.2, lam=60., gust=.5, vertical=.9)
    out('carro:1', 'b12p2_fl', fr, np.clip(cv2.GaussianBlur(band.astype(np.float32), (0, 0), 1.5), 0, 1), 1.6)

if which in ('all', '5'):   # page 6: the geraniums and hydrangeas nod in the breeze
    B = F.load('b12p6.jpg'); R = regions(5)
    fl = R['flores']
    top = np.clip((900 - GY) / 500, 0, 1).astype(np.float32)
    w = cv2.GaussianBlur(fl.astype(np.float32), (0, 0), 3) * top
    fr = F.sway(B, w, n=16, amp=2.4, lam=220., gust=.4, vertical=.3)
    out('carro:5', 'b12p6_fw', fr, np.clip(cv2.GaussianBlur(cv2.dilate(fl, np.ones((9, 9), np.uint8)).astype(np.float32), (0, 0), 2), 0, 1), 3.2)

if which in ('all', '7'):   # page 8: the vine over the roof sways
    B = F.load('b12p8.jpg')
    hsv = cv2.cvtColor(np.clip(B, 0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV)
    v = poly((330, 0), (700, 0), (700, 215), (330, 215)) & ((hsv[..., 0] > 25) & (hsv[..., 0] < 50) & (hsv[..., 1] > 50)).astype(np.uint8)
    v = cv2.morphologyEx(v, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    hang = np.clip((GY - 0) / 210, 0, 1).astype(np.float32)
    w = cv2.GaussianBlur(v.astype(np.float32), (0, 0), 3) * (.4 + .6 * hang)
    fr = F.sway(B, w, n=16, amp=2.6, lam=200., gust=.4, vertical=.3)
    out('carro:7', 'b12p8_vn', fr, np.clip(cv2.GaussianBlur(cv2.dilate(v, np.ones((9, 9), np.uint8)).astype(np.float32), (0, 0), 2), 0, 1), 3.2)
print('done')
