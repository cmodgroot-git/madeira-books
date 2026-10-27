"""Add book 14 (voo) to the library."""
import json, re
from PIL import Image
S = '/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'
A = S + 'artifact-files/87e1712e-5e90-4175-b828-2581544915d4/'
FIN = open(S + 'b14/final.txt').read().split()
for n, f in enumerate(FIN, 1):
    im = Image.open(S + f'b14/{f}.png').convert('RGB').resize((1600, 898), Image.LANCZOS)
    im.save(S + f'gen/masters/b14p{n}.jpg', quality=95)
    im.resize((1200, 674), Image.LANCZOS).save(A + f'img/b14p{n}.jpg', quality=86)
    Image.open(A + f'img/b14p{n}.jpg').convert('RGB').resize((192, 108), Image.LANCZOS).save(A + f'img/t/b14p{n}.webp', quality=72, method=6)
pages = json.load(open(S + 'b14pages.json'))
G = {
 'bananeiras': ['banana plants', 'Bananenstauden', 'bananiers', 'plataneras', 'bananenplanten', 'bananowce'],
 'maosdadas': ['holding hands', 'Hand in Hand', 'main dans la main', 'de la mano', 'hand in hand', 'trzymając się za ręce'],
 'rampa': ['launch ramp, take-off slope', 'Startplatz, Startrampe', 'aire de décollage', 'rampa de despegue', 'startplaats, starthelling', 'startowisko'],
 'mangavento': ['windsock', 'Windsack', 'manche à air', 'manga de viento, catavientos', 'windzak', 'rękaw lotniskowy, wiatrowskaz'],
 'pilotos': ['pilots (paraglider pilots)', 'Piloten (Gleitschirmflieger)', 'pilotes (de parapente)', 'pilotos (de parapente)', 'piloten (paragliders)', 'piloci (paralotniarze)'],
 'asas': ['wings (of a paraglider)', 'Schirme, Flügel', 'ailes (de parapente)', 'alas, velas (de parapente)', 'vleugels, schermen', 'skrzydła (paralotni)'],
 'francelho': ['kestrel (Madeiran name)', 'Turmfalke', 'faucon crécerelle', 'cernícalo', 'torenvalk', 'pustułka'],
 'paranoar': ['hangs still in the air, hovers', 'steht in der Luft, rüttelt', 'fait du surplace en vol', 'se queda quieto en el aire', 'hangt stil in de lucht', 'zawisa w powietrzu'],
 'instrutor': ['instructor', 'Fluglehrer', 'moniteur, instructeur', 'instructor', 'instructeur', 'instruktor'],
 'arnes': ['harness', 'Gurtzeug', 'sellette, harnais', 'arnés', 'harnas, gordel', 'uprząż'],
 'fivelas': ['buckles', 'Schnallen', 'boucles', 'hebillas', 'gespen', 'klamry, sprzączki'],
 'enchese': ['fills up', 'füllt sich', 'se remplit', 'se llena', 'vult zich', 'napełnia się'],
 'respira': ['takes a deep breath', 'atmet tief durch', 'respire profondément', 'respira hondo', 'haalt diep adem', 'bierze głęboki oddech'],
 'corre': ['runs', 'läuft, rennt', 'court', 'corre', 'rent', 'biegnie'],
 'pes': ['feet', 'Füße', 'pieds', 'pies', 'voeten', 'stopy'],
 'voar': ['flying', 'fliegen', 'voler', 'volar', 'vliegen', 'lecieć, latać'],
 'manta': ['buzzard (Madeiran name, "the eagle of Madeira")', 'Mäusebussard (madeirischer Name)', 'buse variable (nom madérien)', 'busardo ratonero (nombre madeirense)', 'buizerd (Madeirese naam)', 'myszołów (nazwa maderska)'],
 'circulos': ['climbs in circles', 'kreist nach oben', 'monte en cercles', 'sube en círculos', 'stijgt in cirkels', 'wznosi się kołami'],
 'aterram': ['they land', 'sie landen', 'ils atterrissent', 'aterrizan', 'ze landen', 'lądują'],
 'acena': ['waves (with)', 'winkt (mit)', "fait signe (avec)", 'saluda agitando', 'zwaait (met)', 'macha (czymś)'],
 'cartaz': ['sign, poster', 'Schild, Plakat', 'pancarte', 'cartel', 'bord, spandoek', 'transparent, plakat'],
 'lapas': ['limpets (grilled, a Madeiran favourite)', 'Napfschnecken (gegrillt, typisch Madeira)', 'patelles (grillées, spécialité de Madère)', 'lapas (a la plancha, típicas de Madeira)', 'napslakken (gegrild, Madeirese specialiteit)', 'skałoczepy (grillowane, przysmak Madery)'],
 'bolodocaco': ['bolo do caco (Madeiran flatbread with garlic butter)', 'bolo do caco (madeirisches Fladenbrot mit Knoblauchbutter)', "bolo do caco (pain plat de Madère au beurre d'ail)", 'bolo do caco (pan plano de Madeira con mantequilla de ajo)', 'bolo do caco (Madeirees platbrood met knoflookboter)', 'bolo do caco (maderski płaski chleb z masłem czosnkowym)'],
 'encosta': ['rests, leans (her head)', 'lehnt (den Kopf)', 'appuie (la tête)', 'apoya (la cabeza)', 'legt (haar hoofd)', 'opiera (głowę)'],
 'cagarras': ["Cory's shearwaters (seabirds with a wailing night call)", 'Gelbschnabel-Sturmtaucher', 'puffins cendrés', 'pardelas cenicientas', 'Kuhls pijlstormvogels', 'burzyki żółtodziobe'],
}
h = open(A + 'index.html').read()
if 'const pages14=' not in h:
    k = h.find('const pages13=['); e = h.find('];', k) + 2
    h = h[:e] + '\nconst pages14=[\n' + ',\n'.join(json.dumps(p, ensure_ascii=False) for p in pages) + '\n];' + h[e:]
    old = "{id:'veleiro',title:'O Veleiro',cams:[],scenes:pages13.map(()=>()=>''),pages:pages13,cover:4},"
    assert old in h
    h = h.replace(old, old + "\n  {id:'voo',title:'O Voo da Rita',cams:[],scenes:pages14.map(()=>()=>''),pages:pages14,cover:5},", 1)
    m = "veleiro:'img/b13p5.jpg'"; assert m in h
    h = h.replace(m, m + ",voo:'img/b14p6.jpg'", 1)
    i = h.find("'veleiro:7':"); j = h.find('\n', i)
    ent = ''.join(f"\n'voo:{n}':{{w:465.8,svg:()=>`<image id=\"voo{n}ph\" href=\"img/b14p{n+1}.jpg\" x=\"0\" y=\"0\" width=\"465.8\" height=\"260\" preserveAspectRatio=\"none\"/><rect class=\"dimmer\" x=\"0\" y=\"0\" width=\"465.8\" height=\"260\" fill=\"#1B1512\"/>`}}," for n in range(8))
    line = h[i:j]; end = ''
    if line.rstrip().endswith('};'):
        line = line.rstrip()[:-2]; end = '};'
    if not line.rstrip().endswith(','): line += ','
    h = h[:i] + line + ent + end + h[j:]
i = h.find('const GLOSS=') + len('const GLOSS='); j = h.find('};', i) + 1
GL = json.loads(h[i:j]); GL.update({k: v for k, v in G.items() if k not in GL}); GL['chao'] = ['floor, ground', 'Boden', 'sol', 'suelo', 'grond, vloer', 'podłoga, ziemia']
h = h[:i] + json.dumps(GL, ensure_ascii=False) + h[j:]
keys = set(re.findall(r'\|([a-z]+)\]', '\n'.join(pages)))
assert not (keys - set(GL)), keys - set(GL)
open(A + 'index.html', 'w').write(h)
print('ok', len(keys))
