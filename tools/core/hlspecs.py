"""Hand-checked region specs for hlmask.py (master px 1600x898). Pages not listed are seeded from their saved outlines."""
import sys
sys.path.insert(0, '/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/conv')
from hlmask import sam, poly, ell, sub, post, ALL
import hl_book1
import hl_book5
import hl_book6
import hl_book7
import hl_book4
import hl_book8
import hl_book9
import hl_book10
import hl_book11
import hl_book12
import hl_book13
import hl_book14
import hl_book15
SPECS = {'manha': dict(hl_book1.SPEC), 'sabado': {}, 'domingo': {}, 'jantar': dict(hl_book4.SPEC), 'passeio': dict(hl_book5.SPEC), 'pico': dict(hl_book6.SPEC), 'seixal': dict(hl_book7.SPEC), 'casa': dict(hl_book8.SPEC), 'garajau': dict(hl_book9.SPEC), 'novacasa': dict(hl_book10.SPEC), 'corridas': dict(hl_book11.SPEC), 'carro': dict(hl_book12.SPEC), 'veleiro': dict(hl_book13.SPEC), 'voo': dict(hl_book14.SPEC), 'festa': dict(hl_book15.SPEC)}

# Per-word fixes on seeded pages: shapes, 'ref' (keep the old outline), ('area', shapes), or ('like', other_keys)
OVR = {
 ('sabado', 3, 'escada'): 'ref',
 ('sabado', 6, 'toalha'): [sam([0, 580, 1070, 870], [(64, 752), (960, 656), (640, 832)], [(240, 768), (672, 672), (500, 600)], 'best')],
 ('domingo', 1, 'ana'): [sam([700, 265, 985, 585], [(830, 350), (830, 500)]), sam([765, 785, 910, 898], [(820, 850), (870, 850)])],
 ('domingo', 3, 'floresta'): ('area', [ALL, sub(sam([870, 310, 1140, 810], [(950, 500), (1060, 500), (1000, 750)])), sub(sam([730, 660, 860, 810], [(790, 740)]))], ['nevoeiro', 'musgo', 'arvores altas']),
 ('sabado', 3, 'praia'): ('like', 'areia pretas|mar azul'),
 ('domingo', 6, 'pedra'): [poly((152, 898), (176, 605), (288, 533), (460, 520), (470, 640), (800, 690), (1000, 700), (1120, 740), (1184, 898)),
    sub(sam([440, 380, 820, 898], [(600, 700), (700, 850)])), sub(sam([0, 600, 390, 898], [(150, 720), (300, 840)])), sub(sam([330, 690, 570, 845], [(430, 760)])), sub(sam([600, 380, 1000, 898], [(800, 750), (900, 850)]))],
 ('jantar', 5, 'desce'): ('like', 'sol'),
 ('jantar', 5, 'corlaranja'): ('like', 'ceu'),
 ('jantar', 5, 'corrosa'): ('like', 'ceu'),
}
OVR[('sabado', 2, 'tem')] = [sam([760, 440, 850, 730], [(790, 580), (800, 650), (812, 550), (795, 500)], [(700, 600), (900, 600)])]
import pickle as _pk
_M = _pk.load(open('/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/b4p2new/masks.pkl', 'rb'))
_PPL = ('mask', (_M['rita'] | _M['ana']).astype('uint8'))
OVR[('jantar', 1, 'piscinas')] = [('mask', _M['pool'].astype('uint8')), sub(_PPL)]
OVR[('jantar', 1, 'ondas')] = [('mask', _M['waves'])]
OVR[('jantar', 1, 'portomoniz')] = [poly((1060, 250), (1060, 170), (1150, 110), (1330, 85), (1600, 45), (1600, 335), (1180, 335)), ('mask', _M['harb'].astype('uint8')), sam([1150, 330, 1560, 400], [(1260, 360), (1350, 365), (1500, 375)])]
OVR[('jantar', 1, 'rochas')] = [poly((250, 300), (1600, 300), (1600, 898), (640, 898), (250, 700)), sub(('mask', _M['sea'].astype('uint8'))), sub(('mask', _M['pool'].astype('uint8'))), sub(('mask', _M['harb'].astype('uint8'))), sub(_PPL), sub(poly((1000, 0), (1600, 0), (1600, 415), (1320, 425), (1000, 340))), sub(poly((0, 898), (0, 560), (300, 560), (1090, 898)))]
OVR[('pico', 3, 'carro')] = [sam([1128, 516, 1216, 580], [(1165, 545), (1190, 560), (1150, 535)], [(1100, 560), (1230, 530)])]   # modern hatchback (b6p4v2)
# book 3 page 2: modern mint hatchback (b3p2v2)
OVR[('domingo', 1, 'carro')] = [sam([75, 350, 1030, 892], [(300, 700), (500, 520), (900, 650), (450, 800)], [(790, 380), (850, 850)], 'big')]
OVR[('domingo', 1, 'cao')] = [sam([650, 415, 752, 545], [(690, 450), (700, 510)], [(780, 420)])]

# action cue: the walkers move whole (backpacks included)
OVR[('domingo', 2, 'caminhar')] = [sam([405, 90, 610, 705], [(520, 200), (520, 450), (500, 650), (440, 300)], [], 'big'), sam([600, 90, 800, 705], [(690, 200), (690, 450), (690, 650)], [], 'big'), sam([385, 200, 470, 440], [(418, 320), (430, 280)], [(370, 320)])]
