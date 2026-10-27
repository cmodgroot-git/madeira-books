"""Re-trace book 1 tap regions with Segment Anything (box/point prompts) + hand shapes. usage: hl_book1.py [preview|apply]"""
import sys, re, math, json, numpy as np, cv2
sys.path.insert(0, '/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/sam/repo')
from PIL import Image, ImageDraw
S = '/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'
A = S + 'artifact-files/87e1712e-5e90-4175-b828-2581544915d4/'
W, H = 1600, 898; SX, SY = 465.8 / W, 260 / H

def sam(box, pos=(), neg=(), pick='best'): return ('sam', box, pos, neg, pick)
def poly(*pts): return ('poly', pts)
def ell(cx, cy, rx, ry): return ('ell', cx, cy, rx, ry)
def sub(sh): return ('sub', sh)
def post(sh): return ('post', sh)

# master-pixel prompts (1600x898)
SPEC = {
 0: [('rita', [sam([200, 300, 490, 720], [(360, 410), (300, 600)])]),
     ('cama', [sam([20, 300, 1110, 898], [(600, 650), (100, 750)], [(360, 420)], 'big')]),
     ('funchal mora', [poly((855, 215), (960, 230), (1100, 330), (1200, 352), (1310, 335), (1310, 500), (1000, 500), (855, 520))]),
     ('sol', [ell(1210, 180, 48, 48)]),
     ('ceu manha', [poly((858, 62), (1310, 62), (1310, 330), (1200, 345), (1100, 318), (960, 222), (858, 205))])],
 1: [('rita acorda', [sam([260, 250, 520, 840], [(400, 450), (380, 300)])]),
     ('janela abre', [poly((30, 0), (400, 40), (400, 898), (30, 898)), sub(sam([260, 250, 520, 840], [(400, 450), (380, 300)]))]),
     ('cidade', [poly((440, 330), (560, 250), (800, 230), (1000, 280), (1200, 385), (1000, 420), (880, 480), (870, 560), (700, 600), (560, 520), (470, 470))]),
     ('mar', [sam([860, 230, 1600, 640], [(1000, 470), (1150, 520), (1450, 330), (1550, 420)], [(1290, 490), (800, 400), (1480, 560)], 'big'), sub(poly((860, 220), (1140, 220), (1140, 385), (860, 385)))]),
     ('navio', [sam([1180, 420, 1395, 565])])],
 2: [('cozinha', [poly((960, 0), (1600, 0), (1600, 898), (940, 898))]),
     ('rita', [sam([240, 85, 800, 898], [(520, 300), (450, 700)])]),
     ('cafe bebe', [sam([565, 390, 765, 545], [(650, 470)])]),
     ('cafe', [sam([1115, 320, 1400, 675], [(1250, 500)])]),
     ('quente', [ell(650, 380, 55, 60)])],
 3: [('rita', [sam([690, 80, 1170, 760], [(900, 400), (850, 200)])]),
     ('come pao', [sam([700, 295, 845, 425], [(780, 340)])]),
     ('pao bom', [sam([360, 610, 805, 845], [(500, 700), (700, 780)])]),
     ('manteiga', [sam([262, 745, 388, 858], [(325, 790)])]),
     ('gosta', [ell(845, 235, 80, 95)])],
 4: [('rita sai', [sam([305, 315, 495, 805], [(400, 600), (400, 380)]), sam([310, 395, 425, 600], [(370, 545), (340, 520)], [(285, 520)])]),
     ('casa', [poly((120, 140), (330, 30), (640, 150), (640, 720), (500, 780), (250, 860), (120, 860))]),
     ('rua', [sam([200, 600, 800, 898], [(560, 860), (700, 700), (300, 870)], [(400, 650)], 'big'), sub(sam([305, 315, 495, 805], [(400, 600), (400, 380)]))]),
     ('gato dorme', [sam([875, 290, 1445, 535], [(1150, 420), (950, 380)])]),
     ('muro', [sam([790, 330, 1600, 898], [(1000, 700), (1400, 650)], [(1150, 420)], 'big'), sub(sam([875, 290, 1445, 535], [(1150, 420), (950, 380)]))]),
     ('sol', [poly((640, 0), (1150, 0), (1100, 60), (900, 180), (800, 300), (640, 300))])],
 5: [('mercado', [poly((0, 0), (1600, 0), (1600, 898), (0, 898)), sub(sam([0, 520, 1450, 898], [(220, 780), (530, 700), (760, 660), (1150, 590), (1200, 760)], [], 'big'))]),
     ('fruta', [sam([50, 640, 435, 898], [(220, 780)]), sam([335, 600, 745, 805], [(530, 700)]),
                sam([575, 550, 950, 785], [(760, 660)]), sam([940, 505, 1430, 705], [(1150, 590)])]),
     ('banana', [sam([50, 640, 435, 898], [(220, 780)])]),
     ('maracuja', [sam([335, 600, 745, 805], [(530, 700)])]),
     ('laranja', [sam([575, 550, 950, 785], [(760, 660)])])],
 6: [('rita', [sam([185, 130, 720, 898], [(480, 600), (430, 300)])]),
     ('tres banana', [sam([705, 370, 880, 505], [(790, 440)])]),
     ('banana', [sam([585, 580, 805, 710], [(690, 650)])]),
     ('compra', [sam([640, 480, 760, 560], [(700, 520)]), sam([760, 520, 985, 590], [(860, 555)])]),
     ('euros', [ell(715, 518, 34, 26), poly((680, 568), (755, 568), (755, 625), (680, 625))]),
     ('senhor', [sam([860, 100, 1365, 898], [(1100, 500), (1080, 250)])]),
     ('obrigada', [ell(510, 265, 55, 80)])],
 7: [('autocarro apanha', [poly((0, 0), (1600, 0), (1600, 898), (0, 898)), sub(poly((1150, 0), (1600, 0), (1600, 760), (1165, 445))), sub(poly((447, 153), (833, 153), (833, 327), (447, 327))), sub(sam([930, 75, 1110, 445], [(1020, 250)], [], 'big'))]),
     ('rita', [sam([870, 250, 1210, 865], [(950, 400), (1000, 700), (1010, 320)]), sam([820, 380, 980, 690], [(890, 600)])]),
     ('janela', [poly((1150, 0), (1600, 0), (1600, 760), (1165, 445))]),
     ('mar', [sam([1140, 210, 1600, 520], [(1450, 320), (1300, 280), (1550, 420)], [(1350, 520), (1250, 400)])]),
     ('rua sobe', [poly((447, 153), (833, 153), (833, 327), (447, 327)), sub(sam([400, 200, 590, 500], [(470, 260), (500, 400)]))])],
 8: [('casa', [poly((0, 0), (1600, 0), (1600, 898), (0, 898)), sub(poly((850, 45), (1310, 45), (1310, 770), (985, 770), (870, 480))), post(sam([650, 190, 1055, 898], [(800, 600), (860, 300)]))]),
     ('noite', [poly((850, 45), (1310, 45), (1310, 770), (985, 770), (870, 480)), sub(sam([650, 190, 1055, 898], [(800, 600), (860, 300)]))]),
     ('lua', [ell(1215, 160, 34, 34)]),
     ('rita', [sam([650, 190, 1055, 898], [(800, 600), (860, 300)])]),
     ('come banana', [sam([840, 340, 935, 455], [(890, 400)])])],
}
GAZE = {  # key: (eye master px, [(target master px, radius master px)], day)
 1: ('ve', (418, 292), [((760, 440), 120)], True),
 7: ('ve', (592, 262), [((1200, 440), 110)], True),
}

def masks_for(page):
    img = Image.open(S + f'gen/masters/b1p{page+1}.jpg').convert('RGB').resize((W, H))
    arr = np.asarray(img); need = any(sh[0] == 'sam' for _, shs in SPEC[page] for sh in shs)
    if need:
        P.set_image(arr)
    out = []
    for keys, shapes in SPEC[page]:
        m = np.zeros((H, W), np.uint8)
        subs = [x[1] for x in shapes if x[0] == 'sub']; posts = [x[1] for x in shapes if x[0] == 'post']
        shapes = [x for x in shapes if x[0] not in ('sub', 'post')]
        for sh in shapes + [('SUB',)] + subs + [('POST',)] + posts:
            if sh[0] == 'SUB':
                base = m; m = np.zeros((H, W), np.uint8); continue
            if sh[0] == 'POST':
                base = base & (1 - cv2.dilate(m, np.ones((7, 7), np.uint8))); m = np.zeros((H, W), np.uint8); continue
            if sh[0] == 'poly':
                cv2.fillPoly(m, [np.array(sh[1], np.int32)], 1)
            elif sh[0] == 'ell':
                cv2.ellipse(m, (sh[1], sh[2]), (sh[3], sh[4]), 0, 0, 360, 1, -1)
            else:
                _, box, pos, neg, pick = sh
                pts = list(pos) + list(neg); lab = [1] * len(pos) + [0] * len(neg)
                ms, sc, _ = P.predict(point_coords=np.array(pts, float) if pts else None,
                                      point_labels=np.array(lab) if pts else None,
                                      box=np.array(box, float), multimask_output=True)
                k = int(np.argmax([x.sum() for x in ms])) if pick == 'big' else int(np.argmax(sc))
                mm = ms[k].astype(np.uint8)
                n, lb, st, _ = cv2.connectedComponentsWithStats(mm)
                if n > 2:  # keep the big pieces only
                    keep = [i for i in range(1, n) if st[i, 4] > 0.04 * st[1:, 4].max()]
                    mm = np.isin(lb, keep).astype(np.uint8)
                m |= mm
        m = base | m
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
        out.append((keys, m))
    return arr, out

def polys_of(m):
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cs = [c for c in cs if cv2.contourArea(c) > 400]
    res = []
    for c in cs:
        per = cv2.arcLength(c, True); eps = 0.004 * per
        a = cv2.approxPolyDP(c, eps, True)
        while len(a) > 48: eps *= 1.3; a = cv2.approxPolyDP(c, eps, True)
        res.append([(float(x), float(y)) for x, y in a[:, 0]])
    return res

def svgpts(p): return ' '.join(f'{x*SX:.1f},{y*SY:.1f}' for x, y in p)

def gaze(gid, key, eye, targets, day):
    ex, ey = eye[0] * SX, eye[1] * SY; parts = []
    for j, ((tx, ty), tr) in enumerate(targets):
        tx, ty, tr = tx * SX, ty * SY, tr * SX
        a = math.atan2(ty - ey, tx - ex); px, py = -math.sin(a), math.cos(a); w = tr * 1.6
        cone = f'{ex:.1f},{ey:.1f} {tx+px*w:.1f},{ty+py*w:.1f} {tx-px*w:.1f},{ty-py*w:.1f}'
        parts.append(f'<linearGradient id="{gid}g{j}" gradientUnits="userSpaceOnUse" x1="{ex:.1f}" y1="{ey:.1f}" x2="{tx:.1f}" y2="{ty:.1f}">'
                     f'<stop offset="0" stop-color="#FFE2B8" stop-opacity=".05"/><stop offset="1" stop-color="#FFE2B8" stop-opacity=".55"/></linearGradient>'
                     f'<polygon class="gz-cone" points="{cone}" fill="url(#{gid}g{j})"/>'
                     f'<line class="gz-line" x1="{ex:.1f}" y1="{ey:.1f}" x2="{tx:.1f}" y2="{ty:.1f}"/>'
                     f'<circle class="gz-ring" cx="{tx:.1f}" cy="{ty:.1f}" r="{tr:.1f}"/>')
    parts.append(f'<circle class="gz-eye" cx="{ex:.1f}" cy="{ey:.1f}" r="2.2"/>')
    cls = 'gaze gz-day' if day else 'gaze'
    return "${o('" + key + "',`<g class=\"" + cls + "\">" + ''.join(parts) + "</g>`)}"

if __name__ == '__main__':
    mode = sys.argv[1]; pages = [int(x) for x in sys.argv[2:]] or list(range(9))
    from segment_anything import sam_model_registry, SamPredictor
    P = SamPredictor(sam_model_registry['vit_b'](checkpoint=S + 'sam/vit_b.pth'))
    h = open(A + 'index.html').read(); tiles = []
    cols = [(255, 40, 40), (40, 220, 40), (60, 120, 255), (255, 200, 0), (255, 0, 255), (0, 230, 230), (255, 128, 0), (255, 255, 255)]
    for pg in pages:
        arr, ms = masks_for(pg); pol = [(k, polys_of(m)) for k, m in ms]
        if mode == 'preview':
            im = Image.fromarray(arr).resize((1000, 561)); d = ImageDraw.Draw(im); f = 1000 / W
            for n, (k, ps) in enumerate(pol):
                for p in ps:
                    q = [(x * f, y * f) for x, y in p]; d.line(q + [q[0]], fill=cols[n % 8], width=3)
                if ps: d.text((ps[0][0][0] * f + 4, ps[0][0][1] * f + 4), k, fill=cols[n % 8])
            if pg in GAZE:
                k, e, ts, _ = GAZE[pg]
                for (t, r) in ts: d.line([(e[0]*f, e[1]*f), (t[0]*f, t[1]*f)], fill='yellow', width=2); d.ellipse([(t[0]-r)*f, (t[1]-r)*f, (t[0]+r)*f, (t[1]+r)*f], outline='yellow', width=2)
            d.text((8, 8), f'b1p{pg+1}', fill='yellow'); tiles.append(im)
        else:
            key = f'manha:{pg}'; i = h.find(f"'{key}':"); j = h.find('\n', i); line = h[i:j]
            p = f'manha{pg}'
            defs = ''.join(f'<clipPath id="{p}c{n}">' + ''.join(f'<polygon points="{svgpts(q)}"/>' for q in ps) + '</clipPath>' for n, (k, ps) in enumerate(pol))
            groups = ''.join("${o('" + k + "',`<use href=\"#" + p + "ph\" clip-path=\"url(#" + p + f"c{n})\"/>" + ''.join(f'<polygon class="rg" points="{svgpts(q)}"/>' for q in ps) + "`)}" for n, (k, ps) in enumerate(pol))
            old_gaze = re.findall(r"\$\{o\('[^']+',`<g class=\"gaze.*?</g>`\)\}", line)
            if pg in GAZE:
                k, e, ts, day = GAZE[pg]; groups += gaze(f'gzm{pg}', k, e, ts, day)
                old_gaze = [g for g in old_gaze if not g.startswith("${o('" + k + "',")]
            groups += ''.join(old_gaze)
            line2 = re.sub(r'<defs>.*?</defs>', '<defs>' + defs + '</defs>', line, count=1)
            dm = line2.find('<rect class="dimmer"'); de = line2.find('/>', dm) + 2
            end = line2[line2.rfind('`)}')+3:]
            line2 = line2[:de] + groups + end
            assert line2.count('`') % 2 == 0
            h = h[:i] + line2 + h[j:]; print(key, [k for k, _ in pol], 'gaze' if pg in GAZE else '', len(old_gaze))
    if mode == 'preview':
        Sh = Image.new('RGB', (2000, 561 * ((len(tiles) + 1) // 2)))
        for n, t in enumerate(tiles): Sh.paste(t, ((n % 2) * 1000, (n // 2) * 561))
        Sh.save(S + 'conv/hl_preview.jpg', quality=82)
    else:
        open(A + 'index.html', 'w').write(h)
