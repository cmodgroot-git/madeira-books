import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, '../b16/prompts.py')).read().split("P={}")[0])
R = dict(l.split() for l in open(os.path.join(HERE, '../b17/refs.txt')))
if os.path.exists(os.path.join(HERE, 'refs.txt')):
    R.update(dict(l.split() for l in open(os.path.join(HERE, 'refs.txt'))))

GEAR = "a black full-length canyoning wetsuit, a black climbing harness at the hips, black neoprene gloves, black canyoning boots and"
RITA18 = RITA + GEAR + " a white open-face helmet; her bangs and dark hair visible under the helmet."
ANA18 = "Ana: Portuguese woman, 30s, heart-shaped face, warm brown eyes, defined arched brows, wide warm smile showing her teeth; voluminous chin-length wavy chestnut-brown bob with golden highlights and a side part (not red, not copper), the bob visible under the helmet; " + GEAR + " a mustard-yellow open-face helmet."
JOAO18 = "João: Portuguese man, late 20s, athletic, short thick wavy dark-brown hair, warm brown eyes, light stubble, broad friendly grin; " + GEAR + " a blue open-face helmet."
TIAGO18 = "Tiago: Portuguese man, about 30, curly black hair, short black beard, big friendly grin; " + GEAR + " a red open-face helmet."
BRUNO18 = "Bruno: Portuguese man about 35, tall and broad-shouldered, shaved head, short dark stubble, dark brown eyes, sun-tanned skin, a warm wide laugh; the canyoning guide; " + GEAR + " an orange open-face helmet and an orange guide's rope bag on his back."
# everyday clothes (pages 1 and 8)
RITA_D = RITA + "a terracotta-red hoodie, black leggings and white trainers."
ANA_D = ANA18.split("; " + GEAR)[0].replace(", the bob visible under the helmet", "") + "; a deep teal hoodie and blue jeans."
JOAO_D = JOAO18.split("; " + GEAR)[0] + "; a navy t-shirt and grey jeans."
TIAGO_D = TIAGO18.split("; " + GEAR)[0] + "; a light grey t-shirt, jeans and his red baseball cap worn forwards."
BRUNO_D = BRUNO18.split("; " + GEAR)[0] + "; a plain dark-red t-shirt with no writing, khaki shorts."

def faces(names, men=None):
    rows = {"Rita": "its top row is Rita", "Ana": "the first two tiles of the second row are Ana", "João": "the third row is João"}
    s = "The characters' faces and hair must match the character sheet (the second image) exactly: " + "; ".join(rows[n] for n in names if n in rows) + ". Same face shape, features, age and hair as in those tiles (ignore the dog tiles and any other rows: there is no dog in this picture)."
    if men:
        s += " " + men
    return s

MEN_T = "Tiago is the man in the {i} image: same face, curly black hair and short black beard."
MEN_TB = "The {i} image shows two men's faces: on the left Tiago (curly black hair, short black beard), on the right Bruno (shaved head, dark stubble). Draw Tiago and Bruno with exactly those faces."
NEG = N + ", dog, corgi, logos, words, letters, numbers, full-face closed helmet hiding the face, bicycle helmet, life jacket"
CANYON = "a canyon of the Ribeira do Lajeado in the laurel forest above Rabaçal, Madeira: dark basalt rock walls covered in bright green moss and small ferns, laurel trees overhead, clear water; the forest drawn light and airy in pale washes with plenty of white paper and soft daylight, not dark"

def mk(scene, refs, people, names, men=None, neg="", light=None, think="fast"):
    p = S if not light else S.replace("Soft natural daylight, gentle shadows.", light)
    return dict(prompt=p + " " + faces(names, men) + " " + " ".join(people) + " Scene: " + scene + " No text.",
                negative_prompt=NEG + neg, image_urls=[R[r] for r in refs], aspect_ratio="16:9", resolution="2K", thinking_mode=think)

def men_ref(i):
    return (['men'], MEN_TB.format(i=i)) if 'men' in R else (['tiago'], MEN_T.format(i=i))

P = {}
m3, t3 = men_ref("third"); m4, t4 = men_ref("fourth")
P['p1'] = mk("a sunny Sunday morning on the Paul da Serra plateau, Madeira: a wide flat high moorland of short golden-green grass and low bracken, a few grey rocks, a small flock of white sheep grazing on the left; far behind, a soft white sea of clouds below the edge of the plateau and a few slim white wind turbines in the distance; a pale blue sky. Two separate vehicles parked on a gravel area, several metres apart: on the left, Rita's small pale-blue 2010s five-door hatchback car (exactly the small car in the third image: short, low, not a van; no badge on the grille); on the right, a separate small white delivery van with its two rear doors open, crates inside. In the foreground between them, Bruno hands a folded black wetsuit and a white helmet to Rita, who takes them smiling; more black wetsuits and helmets in an open wooden crate at his feet. Behind them by the white van, Tiago, Ana and João chat, already holding helmets. The sheep, the small car, the van and the clouds each clearly separate and visible.",
             ['b1p7', 'sheet', 'b12p8'] + m4, [RITA_D, ANA_D, JOAO_D, TIAGO_D, BRUNO_D], ["Rita", "Ana", "João"], t4, ", retro car, vintage car, 1970s, red car, cows, minivan, blue van, car badge, emblem, cap worn backwards")
P['p2'] = mk("the Lagoa Dona Beja in the laurel forest above Rabaçal, Madeira: a round clear green pool at the foot of a small waterfall, ringed by mossy dark rocks and ferns, a narrow stream (the Ribeira do Lajeado) flowing out of it over stones towards the right; on the left, a narrow stone levada channel with a footpath beside it runs along the slope; tall laurel trees overhead, soft light through the leaves. In the foreground on the rocky bank, seen side-on, Bruno clips a large silver-and-orange carabiner onto the front loop of Rita's harness at her hip, both looking down at it; an orange plastic whistle hangs on a cord round Rita's neck, and Bruno holds another orange whistle on a cord out to Ana. Behind them, Ana, João and Tiago stand on the bank in their wetsuits and helmets, each with an orange whistle on a cord. The carabiner and whistles large and clear; whole bodies visible.",
             ['b1p7', 'sheet'] + m3, [RITA18, ANA18, JOAO18, TIAGO18, BRUNO18], ["Rita", "Ana", "João"], t3)
P['p3'] = mk(CANYON + ". A small waterfall about four metres high pours down a near-vertical dark rock face into a pool. The picture is seen exactly side-on: the rock face rises in the centre-right. Rita is abseiling down that rock face beside the waterfall in the correct way: she faces the rock (her chest towards the rock, her back towards the pool), her body leaning back away from the rock at about 45 degrees, legs straight out in front of her with the soles of both boots planted flat against the wet rock, her knees a little shaky; her blue rope runs from the descender on the front of her harness straight up the rock face to a steel anchor bolt at the top of the rock, one gloved hand above on the rope and one hand below her hip holding the rope; she looks over her shoulder down towards the pool, nervous. Beside the anchor at the top of the rock, Bruno kneels and watches her, smiling encouragingly. Below in the pool on the left, Tiago stands waist-deep in the water facing her, both arms wide open, smiling. Rita's legs, the rope and Tiago's open arms clearly visible.",
             ['b1p7', 'sheet'] + m3, [RITA18, TIAGO18, BRUNO18], ["Rita"], t3, ", person hanging in the air, back to the rock, rope held by hand", think="high")
P['p4'] = mk(CANYON + ". In the middle, a long smooth rock slide covered in bright green moss, with a thin sheet of clear water running down it into a round green pool. Ana slides down it on her back, feet first, arms up, mouth wide open shouting with joy, spray around her. On the right, João dives head first into the pool after her, his body stretched out in the air just above the water. On the left bank, Rita sits on a rock laughing at them, one hand on her helmet. The moss, the water and the pool clearly visible; plenty of space around each person.",
             ['b1p7', 'sheet'], [RITA18, ANA18, JOAO18], ["Rita", "Ana", "João"], None, ", bruno, bald man")
P['p5'] = mk("a small clearing on a flat rock beside the stream in the laurel forest above Rabaçal, Madeira: big old laurel trees with dark glossy leaves casting cool shade, a bank of large green ferns on the right. In the shade, Rita, Ana, João, Tiago and Bruno sit on the rocks in their wetsuits, helmets off beside them, eating sandwiches wrapped in paper. Bruno, with a finger to his lips, points up. On a laurel branch above the ferns, about six metres from the group, a Madeira laurel pigeon (pombo-trocaz: a large dark slate-grey pigeon with a silvery-white patch on the side of the neck, a soft wine-red tinge on the breast, a red bill with a pale tip) flaps its wings as it takes off, wings spread. The pigeon clearly separate against pale sky between the leaves, at natural size.",
             ['b1p7', 'sheet'] + m3, [RITA18.replace(" a white open-face helmet; her bangs and dark hair visible under the helmet.", " a white helmet lying beside her; her dark hair and bangs uncovered."), ANA18.replace(" a mustard-yellow open-face helmet.", " a mustard-yellow helmet beside her."), JOAO18, TIAGO18, BRUNO18], ["Rita", "Ana", "João"], t3, ", parrot, dove, white bird")
P['p6'] = mk(CANYON + ", a deep narrow gorge. On the left, a high rock ledge about six metres above a deep, dark green pool. Bruno is in mid-air in the middle of the picture, jumping feet first towards the middle of the pool, arms crossed on his chest, shouting cheerfully. Rita stands at the very edge of the ledge, leaning forward a little to peer down at the water, one foot already stepping back, her face worried. Below, Tiago, Ana and João swim in the pool, looking up. The ledge, the deep pool and Rita at the edge clearly visible.",
             ['b1p7', 'sheet'] + m3, [RITA18, ANA18, JOAO18, TIAGO18, BRUNO18], ["Rita", "Ana", "João"], t3)
P['p7'] = mk(CANYON + ", a deep narrow gorge with a high rock ledge on the left above a deep, dark green pool. Rita and Tiago jump off the ledge together, both in mid-air feet first side by side, holding hands tightly, their joined hands clearly visible between them; Rita laughs with her mouth open, Tiago grins at her. Below them the water of the pool waits, with Bruno, Ana and João swimming at the side and cheering.",
             ['b1p7', 'sheet'] + m3, [RITA18, ANA18, JOAO18, TIAGO18, BRUNO18], ["Rita", "Ana", "João"], t3)
P['p8'] = mk("late afternoon on the gravel parking area of the Paul da Serra plateau, Madeira, golden low sunlight, long soft shadows, a sea of pink-gold clouds below the plateau edge. Rita's small pale-blue 2010s hatchback (exactly the car in the third image, no badge) and the small white van with its rear doors open. Everyone is wrapped in big striped beach towels round their shoulders over their wetsuits, hair wet. In the middle, Bruno and Ana coil long blue ropes into loops; Bruno talks to the group, cheerful. On the right, by Rita's car, Tiago stands close to Rita and looks only at her, shy and hopeful; Rita, holding her coiled rope, looks back at him, surprised. João leans on the van, smiling. The ropes, towels and cars clearly visible.",
             ['b1p7', 'sheet', 'b12p8'] + m4, [RITA18.replace(" a white open-face helmet; her bangs and dark hair visible under the helmet.", " no helmet, her wet dark hair and bangs uncovered; a cobalt-and-white striped towel round her shoulders."), ANA18.replace(" a mustard-yellow open-face helmet.", " no helmet; a terracotta striped towel."), JOAO18.replace(" a blue open-face helmet.", " no helmet; a green towel."), TIAGO18.replace(" a red open-face helmet.", " no helmet; a red striped towel."), BRUNO18.replace(" an orange open-face helmet", " no helmet")], ["Rita", "Ana", "João"], t4, ", retro car, vintage car, 1970s, red car", light="Warm low late-afternoon sunlight, gentle long shadows.")

json.dump(P, open(os.path.join(HERE, 'inputs18.json'), 'w'), ensure_ascii=False, indent=1)
for k, v in P.items():
    print(k, len(v['prompt']), [u[-30:] for u in v['image_urls']])
