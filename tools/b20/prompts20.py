"""Book 20 «Se o Nevoeiro Levantasse» — Krea inputs. Style block and helpers from ../b16/prompts.py; refs from ../b17, ../b18, ../b19 and refs.txt.
Krea settings (skill madeira-book-illustrations, "Krea cost"): krea-3, 2K, thinking "high" (same price as "fast")."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, '../b16/prompts.py')).read().split("P={}")[0])
R = {}
for f in ('../b17/refs.txt', '../b18/refs.txt', '../b19/refs.txt', 'refs.txt'):
    p = os.path.join(HERE, f)
    if os.path.exists(p): R.update(dict(l.split() for l in open(p) if l.strip() and not l.startswith('#')))
R['sheet'] = R['sheet4']
ROWS = {'Rita': 'row 1 is Rita', 'Ana': 'row 2 (first two tiles) is Ana', 'João': 'row 3 is João', 'Tiago': 'row 5 is Tiago'}
def faces(names, rui=None):
    s = ("The characters' faces and hair must match the character sheet (the second image) exactly: " + "; ".join(ROWS[n] for n in names)
         + ". Same face shape, features, age and hair as in those tiles; ignore the clothes, caps, helmets and visors in the tiles (ignore the dog tiles: there is no dog in this picture).")
    if rui: s += f" Rui is the man in the {rui} image: exactly the same face, hair, age and clothes."
    return s
GEAR = ("a fitted long-sleeve mountain-bike jersey, dark grey baggy mountain-bike shorts over black knee pads, black full-finger gloves, "
        "dark flat-soled trail shoes and")
RITA20 = RITA + GEAR + " a white open-face bike helmet; her bangs and dark hair visible under the helmet; her jersey is terracotta red."
ANA20 = ("Ana: Portuguese woman, 30s, heart-shaped face, warm brown eyes, defined arched brows, wide warm smile showing her teeth; voluminous chin-length "
         "wavy chestnut-brown bob with golden highlights and a side part (not red, not copper), the bob visible under the helmet; " + GEAR
         + " a mustard-yellow open-face bike helmet; her jersey is deep teal.")
JOAO20 = ("João: Portuguese man, late 20s, athletic, short thick wavy dark-brown hair, warm brown eyes, light stubble, broad friendly grin; " + GEAR
          + " a blue open-face bike helmet; his jersey is navy blue.")
TIAGO20 = "Tiago: Portuguese man, about 30, curly black hair, short black beard, big friendly grin; " + GEAR + " a red open-face bike helmet; his jersey is light grey."
RUI = ("Rui: Portuguese man about 35, lean and wiry, a narrow tanned face, clean-shaven, light-brown eyes, short neat dark-brown hair going slightly grey "
       "at the temples, small smile lines, an easy confident smile; a PE teacher who guides mountain-bike rides; " + GEAR
       + " a dark grey open-face bike helmet; his jersey is forest green.")
BIKES = "The mountain bikes are all the same model: modern matte-black hardtail mountain bikes with front suspension forks, wide knobbly tyres and flat handlebars."
FANAL = ("Fanal in Madeira: a misty grassy upland clearing among huge ancient til trees (laurel-forest trees with massive gnarled trunks and twisting "
         "branches covered in green moss and ferns), soft white fog drifting between the trunks, damp green grass.")
NEG = N.replace(', aged faces, wrinkles', '') + ", dog, corgi, logos, words, letters, numbers, glasses, spectacles, bun hairstyle, road bike, racing bike, lycra, full-face helmet"
def mk(scene, refs, people, names, rui=None, neg="", light=None, think="high"):
    p = S if not light else S.replace("Soft natural daylight, gentle shadows.", light)
    return dict(prompt=p + " " + faces(names, rui) + " " + " ".join(people) + " " + BIKES + " Scene: " + scene + " No text.",
                negative_prompt=NEG + neg, image_urls=[R[r] for r in refs], aspect_ratio="16:9", resolution="2K", thinking_mode=think)
FOG = "Soft diffuse light through white fog, gentle shadows, the colours slightly muted by the mist but the outlines clean."
import re
def nohelm(x):   # page 8: helmets off
    x=x.replace(", the bob visible under the helmet","").replace("; her bangs and dark hair visible under the helmet","")
    return re.sub(r" and a [a-z -]+ open-face bike helmet;", "; no helmet, hair visible;", x)
P = {}
P['rui'] = dict(prompt=S + " The new character is Rui, a friend of the group. " + RUI
    + " Scene: a character design sheet on a plain warm cream paper background, no setting: the same man drawn three times side by side at the same scale — on the left full-length from the front, standing beside nothing, holding his helmet under one arm; in the middle head and shoulders in three-quarter view with the helmet on, smiling; on the right head and shoulders in profile without the helmet. Plenty of empty space around each. No text.",
    negative_prompt=NEG + ", background scenery, other people, beard, curly hair, shaved head, bicycle", image_urls=[R['b1p7'], R['sheet']], aspect_ratio="16:9", resolution="2K", thinking_mode="high")
P['p1'] = mk(FANAL + " Sunday morning. On the left a white van with its back doors wide open, parked on the grass; Rui (exactly the man in the third image) lifts a matte-black mountain bike out of the back of the van; three more bikes still inside, one already standing on the grass. Behind him, half in the fog, the huge mossy til trees. On the right, a little further back, Rita, Ana, João and Tiago walk towards him across the grass, already in their bike clothes, helmets in their hands. Rui, the van and the bikes large and clear in the foreground.",
    ['b1p7', 'sheet', 'rui'], [RUI, RITA20, ANA20, JOAO20, TIAGO20], ['Rita', 'Ana', 'João', 'Tiago'], rui='third', light=FOG, neg=", cows, animals, writing on the van")
P['p2'] = mk(FANAL + " Morning, the friends standing on the grass with their bikes. In the foreground on the left, Rui (exactly the man in the third image) holds a mountain bike by its handlebar and points with one finger at the brake lever on the handlebar, explaining; the handlebar and the brake levers large and clear. On the right, close to us, Ana is doing up the chin strap of her mustard-yellow helmet with both hands, laughing, a little nervous. Rita, João and Tiago stand behind with their bikes, listening.",
    ['b1p7', 'sheet', 'rui'], [RUI, ANA20, RITA20, JOAO20, TIAGO20], ['Ana', 'Rita', 'João', 'Tiago'], rui='third', light=FOG, neg=", cows, animals")
P['p3'] = mk("A narrow earth mountain-bike trail winding downhill through the laurel forest at Fanal, between huge mossy til trees, the ground full of twisting tree roots and loose grey stones; fog between the trunks. Seen from lower down the trail looking up: Tiago rides down towards us first, standing on the pedals, and Rita follows close behind him, standing on the pedals with bent arms and knees, the bike bouncing over the roots, concentrating hard. On the right at the side of the trail, Rui (exactly the man in the third image) stands beside his bike with one hand cupped at his mouth, shouting advice. The roots and stones on the trail large and clear in the foreground.",
    ['b1p7', 'sheet', 'rui'], [TIAGO20, RITA20, RUI], ['Tiago', 'Rita'], rui='third', light=FOG, neg=", cows, animals, Ana, João")
P['p4'] = mk("A muddy section of the mountain-bike trail in the laurel forest at Fanal, mossy til trees and fog, big ferns along the side of the trail. In the middle of the trail stands a calm brown cow (a Madeiran free-range cow), looking at the riders. In the foreground Rita brakes too late: the front wheel of her bike slides sideways in the brown mud and she is falling slowly to the side, onto a soft bed of large green ferns beside the trail, surprised but not hurt. Behind her, Tiago and Ana have stopped their bikes, braking, feet down. The cow, the mud, the front wheel and the ferns clearly visible.",
    ['b1p7', 'sheet'], [RITA20, TIAGO20, ANA20], ['Rita', 'Tiago', 'Ana'], light=FOG, neg=", several cows, bull, horns, blood, injury")
P['p5'] = mk("The muddy trail in the laurel forest at Fanal, ferns and mossy til trees, fog. Rita has just stood up, her bike lying on the ferns beside her: she has brown mud on her legs, on her arms and a smear of mud on her cheek, and she holds up a handful of mud in one gloved hand, pretending to threaten Tiago, half laughing. Tiago stands in front of her, his own hand over his mouth to hide a laugh, his eyes laughing. In the background, far down the trail, the brown cow walks away between the trees. Rita's muddy legs, arms and face and Tiago's hand over his mouth large and clear.",
    ['b1p7', 'sheet'], [RITA20, TIAGO20], ['Rita', 'Tiago'], light=FOG, neg=", blood, injury, several cows")
P['p6'] = mk("The edge of the high ground above the north coast of Madeira near Fanal, at midday: the group sits on mossy rocks at the edge of a grassy slope eating sandwiches, their five bikes lying on the grass behind them. The white fog is opening like a curtain in front of them, and through the gap, far below, appear the steep green north coast of Madeira, the dark blue sea and bright sunlight shining on the water. Rui (exactly the man in the third image) stands and points at the view; Rita (with dried mud on her legs and arm), Tiago, Ana and João turn to look, amazed. The opening in the fog, the coast and the shining sea large and clear.",
    ['b1p7', 'sheet', 'rui'], [RUI, RITA20, TIAGO20, ANA20, JOAO20], ['Rita', 'Tiago', 'Ana', 'João'], rui='third', light="Bright sunlight breaking through white fog, a gentle glow on the sea, soft shadows.", neg=", cows, animals, buildings in the foreground, road")
P['p7'] = mk("A forest track at the bottom of the last descent below Fanal, tall laurel trees and ferns, light fog. Tiago kneels on the track beside his bike, which stands upside down on its saddle and handlebar with the front wheel taken off; he holds the front wheel, with its new inner tube fitted, between his knees and pumps up the tyre with a small black hand pump, fast and expert. Rui (exactly the man in the third image) stands next to him with his bike, watching, arms crossed, amused and impressed; Rita (with dried mud on her legs) watches over Tiago's shoulder. The wheel, the tyre and the small pump large and clear in the foreground.",
    ['b1p7', 'sheet', 'rui'], [TIAGO20, RUI, RITA20], ['Tiago', 'Rita'], rui='third', light=FOG, neg=", cows, animals, car, workshop, toolbox, Ana, João")
P['p8'] = mk("Exactly the same clearing, white van and huge mossy til trees as in the fourth image (page 1), seen from the same spot. Late afternoon on the grass beside the white van at Fanal, the huge mossy til trees behind, the fog now thin and golden. In the background João and Tiago wash the muddy bikes with a green garden hose, water spraying, and Rui (exactly the man in the third image) leans a clean bike against the van. In the foreground on the right, Ana has taken Rita a few steps aside by the arm and talks to her quietly, close, a little shy and excited; Rita, still with dried mud on her legs and a smear on her cheek, listens with wide eyes, surprised. Helmets off now. The hose, the spraying water and the two women large and clear.",
    ['b1p7', 'sheet', 'rui', 'p1'], [nohelm(x) for x in (ANA20, RITA20, JOAO20, TIAGO20, RUI)], ['Ana', 'Rita', 'João', 'Tiago'], rui='third',
    light="Warm golden late-afternoon light through thin fog, gentle long shadows.", neg=", cows, animals, writing on the van, helmets on heads")
json.dump(P, open(os.path.join(HERE, 'inputs20.json'), 'w'), ensure_ascii=False, indent=1)
print({k: len(v['prompt']) for k, v in P.items()})
