"""Book 21 «Uma Casa para Três» — Krea inputs (krea-3, 2K, thinking "high"; see madeira-book-illustrations "Krea cost").
Continuity sheet (the cycle, rule 5):
  people   Ana (row 2) teal cardigan over a white top, jeans; João (row 3) light-blue shirt, jeans; the corgi (row 2, tiles 3-4)
           Marta (row 4) teal blazer; Inês (row 7, first two tiles) navy blazer, white blouse, no visor; Rita (row 1) blue
           polka-dot blouse, jeans; Tiago (row 5) white t-shirt, jeans, red cap backwards; the landlady (refs: landlady).
  places   p1 café terrace at Funchal harbour, day; p2 modern flat in central Funchal; p3 old flat in Câmara de Lobos: kitchen
           with an old white enamel stove, window over the fishing harbour (p8 = the same flat, empty, at night: ref p3);
           p4 Câmara de Lobos harbour wall at night; p5 Inês's office; p6/p7 the landlady's ground floor (p7 ref p6).
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, '../b16/prompts.py')).read().split("P={}")[0])
R = {}
for f in ('../b17/refs.txt', '../b18/refs.txt', '../b19/refs.txt', '../b20/refs.txt', 'refs.txt'):
    p = os.path.join(HERE, f)
    if os.path.exists(p): R.update(dict(l.split() for l in open(p) if l.strip() and not l.startswith('#')))
R['sheet'] = R['sheet4']
ROWS = {'Rita': 'row 1 is Rita', 'Ana': 'row 2 (first two tiles) is Ana', 'João': 'row 3 is João', 'Marta': 'row 4 is Marta',
        'Tiago': 'row 5 is Tiago', 'Inês': 'row 7 (first two tiles) is Inês', 'dog': "row 2, last two tiles, is Ana's corgi"}
def faces(names, extra=""):
    nodog = "" if 'dog' in names else " (there is no dog in this picture)"
    return ("The characters' faces and hair must match the character sheet (the second image) exactly: " + "; ".join(ROWS[n] for n in names)
            + ". Same face shape, features, age and hair as in those tiles; ignore the clothes, caps and helmets in the tiles" + nodog + ". " + extra)
ANA = ("Ana: Portuguese woman, 30s, heart-shaped face, warm brown eyes, defined arched brows, warm smile; voluminous chin-length wavy chestnut-brown bob "
       "with golden highlights and a side part (not red); a teal cardigan over a white top, blue jeans.")
JOAO = "João: Portuguese man, late 20s, athletic, short thick wavy dark-brown hair, warm brown eyes, light stubble, friendly grin; a light-blue shirt with rolled sleeves, jeans."
DOG = "The dog: Ana's small red-and-white Pembroke Welsh corgi with a white blaze and chest, large upright ears, black collar."
MARTA = "Marta: Portuguese woman, mid-30s, short light-brown pixie hair, freckles, bright smile; a teal blazer over a white top, dark trousers, a folder in her hand."
INES = "Inês: Portuguese woman about 40, tall and slim, sleek straight jaw-length black bob, dark brown eyes, olive skin, calm elegant smile; a navy blazer, white blouse, small reading glasses."
RITA21 = RITA + "a blue blouse with small white polka dots, jeans."
TIAGO21 = "Tiago: Portuguese man, about 30, curly black hair, short black beard, big grin; a white t-shirt, jeans, his red cap worn backwards."
LADY = ("The landlady: a small Portuguese widow about 80, kind round wrinkled face, bright dark eyes, white hair in a neat bun, small gold earrings; "
        "a black dress with a grey knitted cardigan, black shoes.")
NEG = N + ", logos, words, letters, numbers, dog collar tag text"
NEG_OLD = NEG.replace(', aged faces, wrinkles', '')   # pages with the landlady
def mk(scene, refs, people, names, neg="", light=None, extra="", old=False):
    p = S if not light else S.replace("Soft natural daylight, gentle shadows.", light)
    return dict(prompt=p + " " + faces(names, extra) + " " + " ".join(people) + " Scene: " + scene + " No text.",
                negative_prompt=(NEG_OLD if old else NEG) + neg, image_urls=[R[r] for r in refs], aspect_ratio="16:9", resolution="2K", thinking_mode="high")
P = {}
P['landlady'] = dict(prompt=S + " The new character is the landlady. " + LADY + " Scene: a character design sheet on a plain warm cream paper background, no setting: "
    "the same old woman drawn three times side by side at the same scale — on the left full-length from the front, hands folded; in the middle head and shoulders "
    "in three-quarter view, smiling warmly; on the right head and shoulders in profile. Plenty of empty space around each. No text.",
    negative_prompt=NEG_OLD + ", background scenery, other people, young woman", image_urls=[R['b1p7'], R['sheet']], aspect_ratio="16:9", resolution="2K", thinking_mode="high")
P['p1'] = mk("A café terrace on the harbour front of Funchal, Madeira, on a sunny autumn morning: small round metal tables, white parasols, the marina with white sailing boats behind and the green hills of Funchal with white houses beyond. "
    "At a table in the foreground, Ana and João sit with two small coffee cups (bicas); Ana, smiling and a little shy, holds João's hand across the table and says yes; João laughs, delighted. "
    "Ana's corgi lies under the table at their feet, looking up at them. The coffee cups, the harbour and the dog clear.",
    ['b1p7', 'sheet'], [ANA, JOAO, DOG], ['Ana', 'João', 'dog'])
P['p2'] = mk("Inside a bright modern flat in central Funchal: white walls, big glass sliding doors open onto a huge balcony with a view over the red roofs of Funchal to the sea, a shiny modern kitchen corner. "
    "Marta, the estate agent, shows the flat with an open hand, proud. Ana stands on the balcony admiring the view; João, beside Marta, looks at a paper with the price in his hand, worried, eyebrows raised. "
    "In the background, through the open door of the flat, the metal doors of a lift in the corridor. The balcony and the lift clearly visible.",
    ['b1p7', 'sheet'], [MARTA, ANA, JOAO], ['Marta', 'Ana', 'João'], neg=", dog, corgi")
P['p3'] = mk("Inside an old flat in Câmara de Lobos, a fishing village on Madeira: a small old-fashioned kitchen with blue-and-white azulejo tiles, a worn wooden table, an old white enamel gas stove with four burners, a little crooked shelf. "
    "A big open window shows the small harbour of Câmara de Lobos below: brightly painted wooden fishing boats (red, yellow, blue, white) pulled up on the pebble beach and floating in the bay, the cliffs behind. "
    "João stands at the window with one hand on the frame, moved, looking at the boats; Ana stands by the stove, looking at him tenderly. Two old fishermen mend a net on the beach below. The stove, the window and the boats large and clear.",
    ['b1p7', 'sheet'], [JOAO, ANA], ['João', 'Ana'], neg=", dog, corgi")
P['p4'] = mk("Night at the small harbour of Câmara de Lobos, Madeira: Ana and João sit on the low stone harbour wall, a little apart at first, after their first argument; Ana now reaches out and takes João's hand. "
    "Behind them the painted fishing boats rest on the pebbles; a full moon hangs above the dark sea and lays a silver path on the water; a few warm lights in the houses of the village. The moon, the hands and the wall clear.",
    ['b1p7', 'sheet'], [ANA, JOAO], ['Ana', 'João'], light="Night: cool moonlight and a few warm lamp lights, soft shadows.", neg=", dog, corgi, sun")
P['p5'] = mk("Inês's law office in Funchal: a tidy wooden desk with papers, a green desk lamp, shelves of law books, a window onto a street. Inês sits behind the desk in small reading glasses, pointing with one finger at a line in a printed contract lying open on the desk. "
    "Ana and João sit opposite her; Ana leans forward reading, her face falling, sad; João looks at Ana. The contract with the pointing finger large and clear in the foreground.",
    ['b1p7', 'sheet'], [INES, ANA, JOAO], ['Inês', 'Ana', 'João'], neg=", dog, corgi")
P['p6'] = mk("The ground floor of an old house in Câmara de Lobos: a small cosy front room with a lace tablecloth, family photos, a crucifix, a window with geraniums. The old landlady (exactly the woman in the third image) sits in an armchair, "
    "looking up at João, who stands in front of her, surprised and touched; she points at him with delight, remembering his father. Through the open front door Ana's corgi has trotted in and lies down at the old woman's feet, looking up at her; "
    "Ana stands in the doorway behind, hopeful. The old woman, João and the dog at her feet clear.",
    ['b1p7', 'sheet', 'landlady'], [LADY, JOAO, ANA, DOG], ['João', 'Ana', 'dog'], extra="The landlady is the old woman in the third image: same face, hair and clothes.", old=True)
P['p7'] = mk("Exactly the same ground-floor house as in the fourth image, now its small kitchen next to the front room: a wooden kitchen table with a lace cloth. The old landlady (exactly the woman in the third image), smiling, strikes out one line of the contract on the table with a pen; "
    "Ana and João, signing beside her, look happy; on the table lie the signed contract and a ring of two old iron keys, which the old woman is holding out to them. The corgi sits by the table. The pen, the contract and the keys large and clear in the foreground.",
    ['b1p7', 'sheet', 'landlady', 'p6'], [LADY, ANA, JOAO, DOG], ['Ana', 'João', 'dog'], extra="The landlady is the old woman in the third image: same face, hair and clothes.", old=True)
P['p8'] = mk("Exactly the same old flat as in the third image (the same kitchen, azulejo tiles and window over the harbour), now at night and completely empty of furniture except the old stove; a bare bulb gives warm light; through the window the lights of the harbour and the boats. "
    "Ana, João, Rita and Tiago sit on the floor in a circle around an open pizza box, eating pizza slices; a potted green plant with a red ribbon stands on the floor beside them; the corgi begs for a piece. Ana, laughing, says something to Rita, and Rita blushes red, while Tiago grins. The pizza, the plant and the floor clear.",
    ['b1p7', 'sheet', 'p3'], [ANA, JOAO, RITA21, TIAGO21, DOG], ['Ana', 'João', 'Rita', 'Tiago', 'dog'], light="Night indoors: warm light from a bare bulb, soft shadows.")
json.dump(P, open(os.path.join(HERE, 'inputs21.json'), 'w'), ensure_ascii=False, indent=1)
print({k: len(v['prompt']) for k, v in P.items()})
