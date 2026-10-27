"""Book 15 animation: curtains breathe in the breeze (p1), bolo do caco steams and the door lamp glows (p6), balcony string lights twinkle and the moonlit sea glints (p7)."""
import sys, os, numpy as np, cv2
S = '/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'; sys.path.insert(0, S)
import frames as F, windfx
W, H = 1600, 898; GX, GY = F.GX, F.GY
PREVIEW = len(sys.argv) > 2
def poly(*p):
    m = np.zeros((H, W), np.uint8); cv2.fillPoly(m, [np.array(p, np.int32)], 1); return m
def out(key, stem, fr, mask, dur):
    if PREVIEW:
        B = fr[0]; cv2.imwrite(S + f'gen/{stem}_mask.jpg', cv2.cvtColor(np.clip(B * (1 - .6 * mask[..., None]) + np.array([255, 0, 0]) * .6 * mask[..., None], 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR)); return
    pa, box = F.save(fr, mask, stem.split('_')[0], stem.split('_')[1])
    windfx.add_layer(key, F.loop(pa, box, dur), stem); print(stem, box, flush=True)
which = sys.argv[1] if len(sys.argv) > 1 else 'all'

if which in ('all', '0'):   # page 1: sheer curtains move in the breeze from the balcony
    B = F.load('b15p1.jpg')
    hsv = cv2.cvtColor(np.clip(B, 0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV)
    area = poly((0, 0), (275, 0), (275, 640), (0, 640)) | poly((708, 0), (780, 0), (780, 440), (708, 440)) | poly((500, 595), (555, 430), (640, 370), (640, 595))
    cur = area & ((hsv[..., 2] > 170) & (hsv[..., 1] < 60)).astype(np.uint8)
    cur = cv2.morphologyEx(cur, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    cur &= 1 - poly((0, 380), (230, 380), (230, 900), (0, 900))   # keep the lamp and side table still
    low = np.clip((GY - 60) / 450, 0, 1).astype(np.float32)        # hems move most
    w = cv2.GaussianBlur(cur.astype(np.float32), (0, 0), 4) * low
    fr = F.sway(B, w, n=16, amp=3.0, lam=320., gust=.5, vertical=.15)
    out('festa:0', 'b15p1_cur', fr, np.clip(cv2.GaussianBlur(cv2.dilate(cur, np.ones((9, 9), np.uint8)).astype(np.float32), (0, 0), 3), 0, 1), 4.0)

if which in ('all', '5'):   # page 6: warm bolo do caco steams; the door lamp glows gently
    B = F.load('b15p6.jpg')
    st = F.steam(B, 360, 522, height=80, width=30, n=24, strands=2, alpha=.4, seed=5, lean=6)
    gl = np.zeros((H, W), np.float32); cv2.circle(gl, (1040, 200), 60, 1, -1); gl = cv2.GaussianBlur(gl, (0, 0), 22)
    fr = [s * (1 + .10 * 0.5 * (1 - np.cos(2 * np.pi * i / 24)) * gl[..., None]) for i, s in enumerate(st)]
    m = poly((310, 420), (420, 420), (420, 535), (310, 535)).astype(np.float32)
    m = np.maximum(cv2.GaussianBlur(m, (0, 0), 6), np.clip(gl * 1.6, 0, 1))
    out('festa:5', 'b15p6_st', fr, np.clip(m, 0, 1), 3.2)

if which in ('all', '6'):   # page 7: fairy lights on the railing twinkle; moonlight glints on the sea
    B = F.load('b15p7.jpg')
    hsv = cv2.cvtColor(np.clip(B, 0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV)
    bulbs = (poly((380, 860), (1100, 490), (1100, 560), (600, 898), (380, 898)) & ((hsv[..., 2] > 225) & (hsv[..., 0] < 40) & (hsv[..., 1] > 40))).astype(np.uint8)
    n, lb, stt, cen = cv2.connectedComponentsWithStats(bulbs)
    dots = [(cen[i][0] / F.K, cen[i][1] / F.K) for i in range(1, n) if 15 < stt[i, 4] < 900]
    glint = (poly((1380, 390), (1600, 390), (1600, 530), (1380, 530)) & ((hsv[..., 2] > 170) & (hsv[..., 1] < 80)).astype(np.uint8))
    n2, lb2, st2, cen2 = cv2.connectedComponentsWithStats(glint)
    gd = [(cen2[i][0] / F.K, cen2[i][1] / F.K) for i in range(1, n2) if 4 < st2[i, 4] < 600]
    fr = F.twinkle(B, dots, n=24, amp=.35, r=9, seed=4)
    fr2 = F.twinkle(B, gd, n=24, amp=.3, r=4, seed=9)
    gm = np.zeros((H, W), np.float32)
    for x, y in gd: cv2.circle(gm, (int(x * F.K), int(y * F.K)), 8, 1, -1)
    gm = cv2.GaussianBlur(gm, (0, 0), 3)[..., None]
    fr = [a * (1 - gm) + b * gm for a, b in zip(fr, fr2)]
    m = np.zeros((H, W), np.uint8)
    for x, y in dots: cv2.circle(m, (int(x * F.K), int(y * F.K)), 20, 1, -1)
    for x, y in gd: cv2.circle(m, (int(x * F.K), int(y * F.K)), 12, 1, -1)
    print('bulbs', len(dots), 'glints', len(gd))
    out('festa:6', 'b15p7_lt', fr, np.clip(cv2.GaussianBlur(m.astype(np.float32), (0, 0), 4), 0, 1), 3.0)
print('done')
