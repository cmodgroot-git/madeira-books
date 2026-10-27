"""Add book 13 (veleiro) to the library."""
import json, re
from PIL import Image
S = '/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'
A = S + 'artifact-files/87e1712e-5e90-4175-b828-2581544915d4/'
FIN = open(S + 'b13/final.txt').read().split()
for n, f in enumerate(FIN, 1):
    im = Image.open(S + f'b13/{f}.png').convert('RGB').resize((1600, 898), Image.LANCZOS)
    im.save(S + f'gen/masters/b13p{n}.jpg', quality=95)
    im.resize((1200, 674), Image.LANCZOS).save(A + f'img/b13p{n}.jpg', quality=86)
    Image.open(A + f'img/b13p{n}.jpg').convert('RGB').resize((192, 108), Image.LANCZOS).save(A + f'img/t/b13p{n}.webp', quality=72, method=6)
pages = json.load(open(S + 'b13pages.json'))
G = {
 'encolheombros': ['shrugs (her shoulders)', 'zuckt mit den Schultern', 'hausse les épaules', 'se encoge de hombros', 'haalt haar schouders op', 'wzrusza ramionami'],
 'cais': ['quay, pontoon (where boats tie up)', 'Kai, Anlegesteg', 'quai, ponton', 'muelle, pantalán', 'kade, steiger', 'nabrzeże, pomost'],
 'veleiro': ['sailing boat', 'Segelboot', 'voilier', 'velero', 'zeilboot', 'żaglówka'],
 'sofia': ['Sofia (a doctor friend who sails)', 'Sofia (eine befreundete Ärztin, die segelt)', 'Sofia (une amie médecin qui fait de la voile)', 'Sofía (una amiga médica que navega)', 'Sofia (een bevriende arts die zeilt)', 'Sofia (przyjaciółka lekarka, która żegluje)'],
 'medica': ['doctor (a woman)', 'Ärztin', 'médecin (une femme)', 'médica', 'arts (vrouw)', 'lekarka'],
 'colete': ['life jacket', 'Schwimmweste', 'gilet de sauvetage', 'chaleco salvavidas', 'reddingsvest', 'kamizelka ratunkowa'],
 'farol': ['lighthouse', 'Leuchtturm', 'phare', 'faro', 'vuurtoren', 'latarnia morska'],
 'leme': ['helm (the steering wheel of a boat)', 'Steuer, Ruder', 'barre (gouvernail)', 'timón', 'roer, stuurwiel', 'ster'],
 'ica': ['hoists (pulls up)', 'hisst', 'hisse', 'iza', 'hijst', 'podnosi (żagiel)'],
 'velabarco': ['sail (of a boat)', 'Segel', 'voile', 'vela', 'zeil', 'żagiel'],
 'inclina': ['leans over, heels', 'neigt sich, krängt', "s'incline, gîte", 'se inclina, escora', 'helt over', 'przechyla się'],
 'corda': ['rope', 'Seil, Tau', 'corde', 'cuerda', 'touw', 'lina'],
 'enjoada': ['seasick (a woman)', 'seekrank', 'qui a le mal de mer', 'mareada', 'zeeziek', 'ma chorobę morską'],
 'bolachas': ['crackers, biscuits', 'Kekse, Cracker', 'biscuits, crackers', 'galletas', 'koekjes, crackers', 'herbatniki, krakersy'],
 'aponta': ['points (at)', 'zeigt (auf)', 'montre du doigt', 'señala', 'wijst', 'wskazuje'],
 'golfinhos': ['dolphins', 'Delfine', 'dauphins', 'delfines', 'dolfijnen', 'delfiny'],
 'salta': ['jumps, leaps', 'springt', 'saute', 'salta', 'springt', 'skacze'],
 'desertas': ['Desertas islands (dry, empty islands near Madeira)', 'Desertas-Inseln (trockene, unbewohnte Inseln bei Madeira)', 'îles Desertas (îles sèches et désertes près de Madère)', 'islas Desertas (islas secas y deshabitadas cerca de Madeira)', 'Desertas-eilanden (droge, onbewoonde eilanden bij Madeira)', 'wyspy Desertas (suche, bezludne wyspy koło Madery)'],
 'mergulha': ['dives', 'taucht, springt hinein', 'plonge', 'se zambulle', 'duikt', 'nurkuje, skacze do wody'],
 'conves': ['deck (of a boat)', 'Deck', 'pont (du bateau)', 'cubierta', 'dek', 'pokład'],
 'no': ['knot', 'Knoten', 'nœud', 'nudo', 'knoop', 'węzeł'],
 'amarra': ['ties up, moors (the boat)', 'macht fest, vertäut', 'amarre', 'amarra', 'legt aan, maakt vast', 'cumuje, przywiązuje'],
 'parapente': ['paragliding (also the paraglider)', 'Gleitschirmfliegen, Gleitschirm', 'parapente', 'parapente', 'paragliden, paraglider', 'paralotniarstwo, paralotnia'],
}
h = open(A + 'index.html').read()
if 'const pages13=' not in h:
    k = h.find('const pages12=['); e = h.find('];', k) + 2
    h = h[:e] + '\nconst pages13=[\n' + ',\n'.join(json.dumps(p, ensure_ascii=False) for p in pages) + '\n];' + h[e:]
    old = "{id:'carro',title:'O Carro da Rita',cams:[],scenes:pages12.map(()=>()=>''),pages:pages12,cover:5},"
    assert old in h
    h = h.replace(old, old + "\n  {id:'veleiro',title:'O Veleiro',cams:[],scenes:pages13.map(()=>()=>''),pages:pages13,cover:4},", 1)
    m = "carro:'img/b12p6.jpg'"; assert m in h
    h = h.replace(m, m + ",veleiro:'img/b13p5.jpg'", 1)
    i = h.find("'carro:7':"); j = h.find('\n', i)
    ent = ''.join(f"\n'veleiro:{n}':{{w:465.8,svg:()=>`<image id=\"veleiro{n}ph\" href=\"img/b13p{n+1}.jpg\" x=\"0\" y=\"0\" width=\"465.8\" height=\"260\" preserveAspectRatio=\"none\"/><rect class=\"dimmer\" x=\"0\" y=\"0\" width=\"465.8\" height=\"260\" fill=\"#1B1512\"/>`}}," for n in range(8))
    line = h[i:j]; end = ''
    if line.rstrip().endswith('};'):
        line = line.rstrip()[:-2]; end = '};'
    if not line.rstrip().endswith(','): line += ','
    h = h[:i] + line + ent + end + h[j:]
i = h.find('const GLOSS=') + len('const GLOSS='); j = h.find('};', i) + 1
GL = json.loads(h[i:j]); GL.update({k: v for k, v in G.items() if k not in GL})
h = h[:i] + json.dumps(GL, ensure_ascii=False) + h[j:]
keys = set(re.findall(r'\|([a-z]+)\]', '\n'.join(pages)))
assert not (keys - set(GL)), keys - set(GL)
open(A + 'index.html', 'w').write(h)
print('ok', len(keys))
