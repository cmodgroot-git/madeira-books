"""Gentle wind layers (painted-frame sway). usage: windfx.py <key>   (adds/replaces the page's 'lb' layer)"""
import sys, re, numpy as np, cv2
S = '/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'
sys.path.insert(0, S)
import frames as F
W, H = 1600, 898
YY, XX = np.mgrid[0:H, 0:W]

FOLIAGE = {  # key: (image, foliage polys, people/object boxes to keep still (SAM), amp)
 'domingo:1': ('b3p2v2', [[(0, 60), (330, 60), (330, 600), (0, 640)], [(1270, 100), (1600, 100), (1600, 898), (1150, 898), (1150, 600), (1270, 600)]],
               [[700, 265, 985, 898], [60, 360, 1020, 898], [630, 400, 760, 560]], 2.4),
 'domingo:2': ('b3p3', [[(0, 0), (420, 0), (420, 480), (0, 500)], [(0, 640), (260, 640), (260, 898), (0, 898)], [(1150, 470), (1600, 470), (1600, 898), (1150, 898)]],
               [[420, 190, 620, 770], [590, 190, 800, 780], [750, 600, 1010, 900]], 2.4),
 'domingo:3': ('b3p4', [[(0, 690), (240, 690), (260, 898), (0, 898)], [(0, 540), (120, 540), (120, 690), (0, 690)], [(1340, 500), (1600, 500), (1600, 820), (1340, 820)], [(560, 0), (1080, 0), (1080, 110), (560, 110)]],
               [[900, 500, 1140, 898], [730, 690, 880, 820]], 2.2),
 'domingo:4': ('b3p5', [[(1150, 0), (1600, 0), (1600, 898), (1240, 898), (1240, 450), (1150, 450)], [(450, 0), (1150, 0), (1150, 70), (450, 70)], [(0, 640), (250, 640), (250, 898), (0, 898)]],
               [[370, 160, 560, 800], [540, 160, 820, 800], [930, 520, 1150, 760]], 2.4),
 'domingo:6': ('b3p7', [[(0, 230), (450, 230), (450, 680), (0, 700)], [(1240, 380), (1600, 380), (1600, 898), (1380, 898), (1380, 700), (1240, 700)]],
               [[440, 140, 800, 898], [750, 150, 1210, 898], [1040, 520, 1430, 898], [0, 640, 400, 898]], 2.4),
}
HAIR = {  # key: (image, [(hair box x0,y0,x1,y1, face cx,cy)], amp)
 'sabado:3': ('b2p4', [(520, 240, 710, 400, 630, 320), (900, 190, 1100, 360, 1010, 290)], 1.8),
 'sabado:4': ('b2p5', [(840, 100, 1060, 330, 950, 215), (1060, 110, 1240, 290, 1140, 200)], 1.8),
 'sabado:5': ('b2p6', [(510, 80, 720, 360, 630, 220), (880, 130, 1060, 420, 960, 250)], 1.8),
 'sabado:6': ('b2p7', [(330, 200, 560, 450, 470, 320), (570, 320, 730, 480, 650, 410)], 1.8),
}
UMBRELLA = {'sabado:6': [(1340, 0), (1600, 0), (1600, 45), (1340, 30)]}

def people_mask(img, boxes):
    import os
    f = S + f'gen/ppl_{img}.npy'
    if os.path.exists(f): return np.load(f)
    raise SystemExit('run: python3 windmask.py ' + img)

def _sam_people(img, boxes):
    from segment_anything import sam_model_registry, SamPredictor
    P = SamPredictor(sam_model_registry['vit_h'](checkpoint=S + 'sam/vit_h.pth'))
    arr = np.asarray(__import__('PIL.Image', fromlist=['x']).open(S + f'gen/masters/{img}.jpg').convert('RGB').resize((W, H)))
    P.set_image(arr); m = np.zeros((H, W), np.uint8)
    for b in boxes:
        ms, sc, _ = P.predict(box=np.array(b, float), multimask_output=True)
        m |= ms[int(np.argmax([x.sum() for x in ms]))].astype(np.uint8)
    return m

def add_layer(key, html_layer, stem):
    h = open(F.A + 'index.html').read(); i = h.find(f"'{key}':"); j = h.find('\n', i); line = h[i:j]
    line = re.sub(r'<svg x="[\d.]+" y="[\d.]+" width="[\d.]+" height="[\d.]+" viewBox="[^"]+"[^>]*><image href="img/' + stem + r'_sheet\.webp".*?</svg>', '', line)
    line = re.sub(r'<image href="img/' + stem + r'00\.webp".*?(?=<image href="img/(?!' + stem + r')|<svg|</g><!--/life-->)', '', line, flags=re.S)
    if '<!--/life-->' in line:
        line = line.replace('</g><!--/life-->', html_layer + '</g><!--/life-->', 1)
        open(F.A + 'index.html', 'w').write(h[:i] + line + h[j:])
    else:
        F.insert(F.A + 'index.html', key, html_layer)

def build(key):
    if key in FOLIAGE:
        img, polys, boxes, amp = FOLIAGE[key]
        B = F.load(img + '.jpg')
        area = F.poly_mask(polys, scale=1) > 0
        R, G, Bc = B[..., 0], B[..., 1], B[..., 2]
        green = (G > R * 0.95) & (G > Bc * 1.05) & (F.sat(B) > 18) & (F.lum(B) > 40)
        ppl = people_mask(img, boxes)
        keep = cv2.dilate(ppl, np.ones((15, 15), np.uint8)) > 0
        w = (area & green & ~keep).astype(np.float32)
        w = cv2.morphologyEx(w, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
        w = cv2.GaussianBlur(w, (0, 0), 6)
        w[keep] = 0; w = cv2.GaussianBlur(w, (0, 0), 1.5)
        fr = F.sway(B, w, n=16, amp=amp, lam=320.)
        mask = np.clip(cv2.GaussianBlur((w > 0.03).astype(np.float32), (0, 0), 2) * 1.2, 0, 1); mask[keep] = 0
    else:
        img, heads, amp = HAIR[key]
        B = F.load(img + '.jpg'); L = F.lum(B)
        w = np.zeros((H, W), np.float32)
        for x0, y0, x1, y1, fx, fy in heads:
            box = (XX >= x0) & (XX < x1) & (YY >= y0) & (YY < y1)
            hair = box & (L < 125) & (B[..., 0] > B[..., 2] * 1.1) & (F.sat(B) < 90)
            face = ((XX - fx) / 58.) ** 2 + ((YY - fy) / 74.) ** 2 < 1
            hair &= ~face
            hair = cv2.morphologyEx(hair.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0
            grad = np.clip((YY - y0) / max(1, (y1 - y0)), 0, 1) ** 1.2
            w += hair * (0.25 + 0.75 * grad)
        if key in UMBRELLA:
            um = F.poly_mask([UMBRELLA[key]], scale=1) > 0
            w += (um & (L < 140)).astype(np.float32) * 0.8
        w = cv2.GaussianBlur(w, (0, 0), 3)
        for x0, y0, x1, y1, fx, fy in heads:
            w[((XX - fx) / 52.) ** 2 + ((YY - fy) / 68.) ** 2 < 1] = 0
        w = cv2.GaussianBlur(w, (0, 0), 1.5)
        fr = F.sway(B, w, n=16, amp=amp, lam=400., vertical=.15)
        mask = np.clip(cv2.GaussianBlur((w > 0.02).astype(np.float32), (0, 0), 3) * 1.3, 0, 1)
        for x0, y0, x1, y1, fx, fy in heads:
            mask[((XX - fx) / 50.) ** 2 + ((YY - fy) / 64.) ** 2 < 1] = 0
    pa, box = F.save(fr, mask, img, 'lb')
    add_layer(key, F.loop(pa, box, 6), f'{img}_lb')
    print(key, len(pa), box, flush=True)

if __name__ == '__main__':
    for k in sys.argv[1:]: build(k)
