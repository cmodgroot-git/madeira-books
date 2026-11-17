"""Book 22 «O Jogo de Domingo» — Krea inputs (krea-3, 2K, thinking "high").
Continuity sheet:
  kits     Tiago's workshop team: plain navy-blue football shirts and navy shorts; João's restaurant team: plain white shirts and
           white shorts; Bruno the referee: plain black shirt and shorts, a whistle on a cord. No numbers, badges or writing.
  people   Rita (row 1) blue polka-dot blouse, jeans; Ana (row 2) teal cardigan, white top, jeans; João (row 3); Tiago (row 5;
           cap only on p1 and p8); Bruno (row 7, last two tiles: shaved head); Dona Graça (refs landlady): black dress, grey
           cardigan, white bun + a green-and-red striped wool scarf (Marítimo colours, no badge); Ana's corgi.
  places   p1 Tiago's workshop (ref workshop); p2 Graça's front room (ref b21p6); p3–p7 the Câmara de Lobos pitch: green
           artificial turf, white lines, white goals with nets, a low concrete stand with three rows of blue plastic seats,
           pastel houses on the hill behind, the sea and the Cabo Girão cliff beyond (p4–p7 use p3 as reference);
           p8 night, the doorstep of Graça's house, her lit kitchen through the open door (ref b21p7).
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, '../b16/prompts.py')).read().split("P={}")[0])
R = {}
for f in ('../b17/refs.txt', '../b18/refs.txt', '../b19/refs.txt', '../b20/refs.txt', 'refs21.txt', 'refs.txt'):
    p = os.path.join(HERE, f)
    if os.path.exists(p): R.update(dict(l.split() for l in open(p) if l.strip() and not l.startswith('#')))
R['sheet'] = R['sheet4']
R['b21p6'] = 'https://gen.krea.ai/images/e78622d1-e9e5-4324-a511-0e1e81eab5a3.png'
R['b21p7'] = 'https://gen.krea.ai/images/2c6c7b16-c574-440b-8a9d-b818b00ced7c.png'
ROWS = {'Rita': 'row 1 is Rita', 'Ana': 'row 2 (first two tiles) is Ana', 'João': 'row 3 is João', 'Tiago': 'row 5 is Tiago',
        'Bruno': 'row 7, last two tiles, is Bruno (the man with the shaved head)', 'dog': "row 2, last two tiles, is Ana's corgi"}
def faces(names, extra=""):
    nodog = "" if 'dog' in names else " (there is no dog in this picture)"
    return ("The characters' faces and hair must match the character sheet (the second image) exactly: " + "; ".join(ROWS[n] for n in names)
            + ". Same face shape, features, age and hair as in those tiles; ignore the clothes, caps and helmets in the tiles" + nodog + ". " + extra)
ANA = "Ana: Portuguese woman, 30s, heart-shaped face, warm brown eyes, voluminous chin-length wavy chestnut-brown bob with a side part (not red, no bangs); a teal cardigan over a white top, blue jeans."
JOAO = "João: Portuguese man, late 20s, athletic, short thick wavy dark-brown hair, light stubble, friendly grin"
TIAGO = "Tiago: Portuguese man, about 30, curly black hair, short black beard, big grin"
RITA22 = RITA + "a blue blouse with small white polka dots, jeans."
BRUNO = "Bruno, the referee: Portuguese man about 35, tall and broad-shouldered, shaved head, short dark stubble, sun-tanned; a plain black referee shirt and black shorts, a whistle on a cord round his neck."
DOG = "The dog: Ana's small red-and-white Pembroke Welsh corgi with a white blaze and chest, large upright ears, black collar."
LADY = ("Dona Graça: the small Portuguese widow about 80 from the third image, kind round wrinkled face, white hair in a neat bun, small gold earrings; "
        "a black dress, a grey knitted cardigan and a long green-and-red striped wool scarf with no badge or writing.")
NAVY = "a plain navy-blue football shirt and navy shorts with no numbers or writing"; WHITE = "a plain white football shirt and white shorts with no numbers or writing"
PITCH = ("A small town football pitch in Câmara de Lobos, Madeira: green artificial turf with white lines, white goals with nets, a low concrete stand with three rows of blue plastic seats along one side, "
         "pastel-coloured houses with red roofs climbing the hill behind, and beyond them the blue sea and the tall dark Cabo Girão cliff. Sunny Sunday afternoon.")
NEG = N + ", logos, words, letters, numbers, club badge, emblem, shirt numbers, sponsor, advertising boards with text"
NEG_OLD = NEG.replace(', aged faces, wrinkles', '')
def mk(scene, refs, people, names, neg="", light=None, extra="", old=False):
    p = S if not light else S.replace("Soft natural daylight, gentle shadows.", light)
    return dict(prompt=p + " " + faces(names, extra) + " " + " ".join(people) + " Scene: " + scene + " No text.",
                negative_prompt=(NEG_OLD if old else NEG) + neg, image_urls=[R[r] for r in refs], aspect_ratio="16:9", resolution="2K", thinking_mode="high")
LADYX = "Dona Graça is the old woman in the third image: same face, hair and clothes, plus her striped scarf."
P = {}
P['p1'] = mk("Inside Tiago's small mechanic workshop in Funchal, exactly as in the third image: a car on a lift, tool walls, a workbench. Tiago, in navy work overalls and his red cap worn backwards, proudly holds up a plain navy-blue football shirt with both hands; a white-and-black football sits on the workbench beside him. "
    "Rita stands opposite, laughing, arms crossed, teasing him. The shirt and the football large and clear.",
    ['b1p7', 'sheet', 'workshop'], [TIAGO + "; navy work overalls over a white t-shirt, red cap worn backwards.", RITA22], ['Tiago', 'Rita'], neg=", dog, corgi")
P['p2'] = mk("Exactly the same cosy front room as in the fourth image (lace tablecloth, family photos, crucifix, geraniums at the window). Dona Graça has just stood up from her armchair, excited, wrapping a long green-and-red striped scarf round her neck, pointing at João with delight. "
    "Ana and João, standing in front of her, laugh in surprise. The corgi wags beside them. The striped scarf large and clear.",
    ['b1p7', 'sheet', 'landlady', 'b21p6'], [LADY, ANA, JOAO + "; a light-blue shirt, jeans.", DOG], ['Ana', 'João', 'dog'], extra=LADYX, old=True)
P['p3'] = mk(PITCH + " In the foreground on the low stand sit Rita, Ana and Dona Graça (with her striped scarf) side by side in the sun, the corgi at Ana's feet. On the pitch, players in navy shirts and in white shirts warm up; "
    "near the stand Bruno, the referee in black, holds up his whistle with a very serious face. The stand, the pitch and the referee's whistle clear.",
    ['b1p7', 'sheet', 'landlady'], [RITA22, ANA, LADY, BRUNO, DOG], ['Rita', 'Ana', 'Bruno', 'dog'], extra=LADYX, old=True)
P['p4'] = mk("Exactly the same pitch as in the third image. Tiago, in " + NAVY + ", leaps high in front of the goal and heads the white-and-black ball into the net past the diving goalkeeper in a yellow jersey; "
    "behind the goal, on the low stand, Rita jumps up clapping. The ball, Tiago's head and the net large and clear.",
    ['b1p7', 'sheet', 'p3'], [TIAGO + "; " + NAVY + ", no cap.", RITA22], ['Tiago', 'Rita'], neg=", dog, corgi, cap")
P['p5'] = mk("Exactly the same pitch as in the third image, near one goal. João, in " + WHITE + ", has fallen on the green turf and protests with both arms up; Tiago, in " + NAVY + ", stands over him protesting too; "
    "Bruno, the referee in black, holds up a yellow card at Tiago and blows his whistle. The goal with its net behind them, the turf and the yellow card clear.",
    ['b1p7', 'sheet', 'p3'], [JOAO + "; " + WHITE + ".", TIAGO + "; " + NAVY + ", no cap.", BRUNO], ['João', 'Tiago', 'Bruno'], neg=", dog, corgi, cap, red card")
P['p6'] = mk("Exactly the same pitch as in the fourth image, at half-time. Small Dona Graça, with her striped scarf, stands on the turf between João (" + WHITE + ") and Tiago (" + NAVY + "), wagging her finger at them like a strict grandmother; "
    "the two tall young men look at the ground, embarrassed, and shake hands. Teammates watch, grinning, in the background.",
    ['b1p7', 'sheet', 'landlady', 'p3'], [LADY, JOAO + "; " + WHITE + ".", TIAGO + "; " + NAVY + ", no cap."], ['João', 'Tiago'], extra=LADYX, old=True, neg=", dog, corgi, cap")
P['p7'] = mk("Exactly the same pitch as in the fourth image, last minute. João, in " + WHITE + ", has just kicked a penalty: the ball hits the back of the net while the goalkeeper in a yellow jersey dives the wrong way. "
    "On the low stand behind, Ana, Rita and Dona Graça (with her striped scarf) jump up cheering; players in navy and white hug. The ball in the net large and clear.",
    ['b1p7', 'sheet', 'landlady', 'p3'], [JOAO + "; " + WHITE + ".", ANA, RITA22, LADY], ['João', 'Ana', 'Rita'], extra=LADYX, old=True, neg=", dog, corgi")
P['p8'] = mk("Night on the cobbled doorstep of Dona Graça's old house in Câmara de Lobos. Through the open door behind, her warm lit kitchen (as in the fourth image) where Ana, João and Dona Graça sit at the table looking at an old photograph. "
    "In the foreground, outside under a street lamp, Tiago (white t-shirt, jeans, red cap worn backwards) gently takes Rita's hand; she looks down, smiling shyly. The joined hands clear.",
    ['b1p7', 'sheet', 'landlady', 'b21p7'], [TIAGO + "; a white t-shirt, jeans, red cap worn backwards.", RITA22, ANA, JOAO + "; a light-blue shirt.", LADY.replace(" and a long green-and-red striped wool scarf with no badge or writing", "")],
    ['Tiago', 'Rita', 'Ana', 'João'], extra="Dona Graça is the old woman in the third image.", old=True, light="Night: warm light from the kitchen door and a street lamp, cool blue shadows.", neg=", dog, corgi")
json.dump(P, open(os.path.join(HERE, 'inputs22.json'), 'w'), ensure_ascii=False, indent=1)
print({k: len(v['prompt']) for k, v in P.items()})
