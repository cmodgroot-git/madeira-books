"""Add book 11 (corridas) to the library."""
import json, re, shutil
from PIL import Image
S = '/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'
A = S + 'artifact-files/87e1712e-5e90-4175-b828-2581544915d4/'
SRC = {1:'b11/v2/p1h.png',2:'b11/p2b.png',3:'b11/v2/p3d.png',4:'b11/v2/p4c.png',5:'b11/v2/p5c.png',6:'b11/v2/p6d.png',7:'b11/v2/p7c.png',8:'b11/p8c.png'}
for n, f in SRC.items():
    im = Image.open(S + f).convert('RGB')
    im.save(S + f'gen/masters/b11p{n}.jpg', quality=95)
    im.resize((1200, 674), Image.LANCZOS).save(A + f'img/b11p{n}.jpg', quality=86)
    Image.open(A + f'img/b11p{n}.jpg').convert('RGB').resize((192, 108), Image.LANCZOS).save(A + f'img/t/b11p{n}.webp', quality=72, method=6)

pages = [
"No domingo de manhã, o Tiago leva os amigos ao [kartódromo|kartodromo] do Faial, no norte da ilha. Por cima da [pista|pista] ergue-se a [Penha d'Águia|penhadaguia], uma rocha enorme ao pé do [mar|mar]. — Hoje é dia de corrida! — diz o [Tiago|tiago].",
"No [balcão|balcao], um [funcionário|funcionario] dá-lhes [fatos de corrida|fatocorrida], [luvas|luvas] e [capacetes|capacete]. A Rita escolhe um capacete vermelho. — Fica-te bem — diz o Tiago. A Rita fica [vermelha|vermelha] como o capacete, e a Ana ri-se.",
"O Tiago mostra-lhes um [kart|kart]: o [pedal|pedal] da direita é para acelerar e o da esquerda é para travar. A [bandeira|bandeira] verde quer dizer «partida» e a bandeira de [xadrez|xadrez] quer dizer «fim». — E se eu bater? — pergunta a Ana. — Os [pneus|pneus] protegem-te.",
"Partida! Os karts [arrancam|arrancam] com um barulho enorme e deixam [fumo|fumo] azul no ar. Na primeira [curva|curva], o João [ultrapassa|ultrapassa] a Ana. Nas [bancadas|bancada], o [público|publico] grita e bate palmas.",
"A meio da corrida começa a [chover|chover] e a pista fica [molhada|molhado]. A [viseira|viseira] do capacete da Rita enche-se de [gotas|gotas]. Ela trava tarde demais e o kart [dá um pião|piao]! «Talvez devesse ter travado mais cedo», pensa ela, a rir.",
"Mas a Rita não desiste. Na última volta, passa o João e o Tiago e cruza a [meta|meta] em primeiro lugar! O Tiago tira o capacete e bate [palmas|palmas]. — Se calhar devias ser [piloto|piloto]!",
"No [pódio|podio], o funcionário [aperta|aperta]-lhe a [mão|mao] e dá-lhe uma [taça|taca] pequena e uma [medalha|medalha]. A Ana tira-lhe uma [fotografia|fotografia] com o [telemóvel|telemovel]. — Gostaria de agradecer ao meu [mecânico|mecanico] — diz a Rita, muito séria. Todos se riem.",
"No caminho para casa, na [carrinha|carrinha] do Tiago, ele pergunta: — Rita, já pensaste em comprar um carro? Eu podia ajudar-te. A Rita olha para o mar e [sorri|sorri]. No [banco|banco] de trás, a Ana [adormece|adormece] no [ombro|ombro] do João.",
]
G = {
 'kartodromo': ['kart track', 'Kartbahn', 'piste de karting', 'kartódromo, circuito de karts', 'kartbaan', 'tor kartingowy'],
 'pista': ['track (race track)', 'Strecke, Rennstrecke', 'piste', 'pista', 'baan, circuit', 'tor'],
 'penhadaguia': ["Penha d'Águia (Eagle Rock, a huge cliff on Madeira's north coast)", "Penha d'Águia (Adlerfelsen, riesiger Felsen an der Nordküste)", "Penha d'Águia (rocher de l'Aigle, falaise géante de la côte nord)", "Penha d'Águia (Peña del Águila, enorme roca de la costa norte)", "Penha d'Águia (Adelaarsrots, enorme rots aan de noordkust)", "Penha d'Águia (Orla Skała, ogromny klif na północnym wybrzeżu)"],
 'fatocorrida': ['racing suits', 'Rennanzüge', 'combinaisons de course', 'monos de carreras', 'racepakken', 'kombinezony wyścigowe'],
 'capacete': ['helmet', 'Helm', 'casque', 'casco', 'helm', 'kask'],
 'kart': ['go-kart', 'Gokart', 'kart', 'kart', 'kart', 'gokart'],
 'pedal': ['pedal', 'Pedal', 'pédale', 'pedal', 'pedaal', 'pedał'],
 'bandeira': ['flag', 'Flagge, Fahne', 'drapeau', 'bandera', 'vlag', 'flaga'],
 'xadrez': ['chequered (like a chessboard)', 'kariert (Schachbrett)', 'à damier', 'a cuadros (de ajedrez)', 'geblokt (schaakbord)', 'w szachownicę'],
 'pneus': ['tyres', 'Reifen', 'pneus', 'neumáticos', 'banden', 'opony'],
 'arrancam': ['(they) take off, pull away', '(sie) fahren los', '(ils) démarrent', '(ellos) arrancan', '(zij) trekken op', '(oni) ruszają'],
 'fumo': ['smoke', 'Rauch', 'fumée', 'humo', 'rook', 'dym'],
 'curva': ['bend, corner', 'Kurve', 'virage', 'curva', 'bocht', 'zakręt'],
 'ultrapassa': ['overtakes', 'überholt', 'dépasse', 'adelanta', 'haalt in', 'wyprzedza'],
 'bancada': ['stands (grandstand)', 'Tribüne', 'tribune, gradins', 'gradas, tribuna', 'tribune', 'trybuny'],
 'publico': ['crowd, spectators', 'Publikum, Zuschauer', 'public, spectateurs', 'público', 'publiek', 'publiczność'],
 'viseira': ['visor', 'Visier', 'visière', 'visera', 'vizier', 'szybka kasku'],
 'gotas': ['drops (raindrops)', 'Tropfen', 'gouttes', 'gotas', 'druppels', 'krople'],
 'piao': ['spins (dá um pião: spins round)', 'dreht sich (dreht sich um sich selbst)', 'fait un tête-à-queue', 'trompea, da un trompo', 'tolt, maakt een spin', 'obraca się (bączek)'],
 'meta': ['finish line', 'Ziellinie', "ligne d'arrivée", 'meta', 'finish', 'meta'],
 'piloto': ['racing driver', 'Rennfahrer(in)', 'pilote', 'piloto', 'coureur', 'kierowca wyścigowy'],
 'podio': ['podium', 'Siegerpodest', 'podium', 'podio', 'podium', 'podium'],
 'aperta': ['shakes (aperta a mão: shakes hands)', 'drückt (die Hand schütteln)', 'serre (la main)', 'estrecha (la mano)', 'schudt (de hand)', 'ściska (dłoń)'],
 'taca': ['cup, trophy', 'Pokal', 'coupe, trophée', 'copa, trofeo', 'beker', 'puchar'],
 'medalha': ['medal', 'Medaille', 'médaille', 'medalla', 'medaille', 'medal'],
 'adormece': ['falls asleep', 'schläft ein', "s'endort", 'se duerme', 'valt in slaap', 'zasypia'],
 'ombro': ['shoulder', 'Schulter', 'épaule', 'hombro', 'schouder', 'ramię'],
}
h = open(A + 'index.html').read()
if 'const pages11=' not in h:
    k = h.find('const pages10=['); e = h.find('];', k) + 2
    h = h[:e] + '\nconst pages11=[\n' + ',\n'.join(json.dumps(p, ensure_ascii=False) for p in pages) + '\n];' + h[e:]
    old = "{id:'novacasa',title:'A Casa Nova',cams:[],scenes:pages10.map(()=>()=>''),pages:pages10,cover:7},"
    assert old in h
    h = h.replace(old, old + "\n  {id:'corridas',title:'O Dia das Corridas',cams:[],scenes:pages11.map(()=>()=>''),pages:pages11,cover:5},", 1)
    h = h.replace("novacasa:'img/b10p8.jpg'}", "novacasa:'img/b10p8.jpg',corridas:'img/b11p6.jpg'}", 1)
    assert "corridas:'img/b11p6.jpg'" in h
    i = h.find("'novacasa:7':"); j = h.find('\n', i)
    ent = ''.join(f"\n'corridas:{n}':{{w:465.8,svg:()=>`<image id=\"corridas{n}ph\" href=\"img/b11p{n+1}.jpg\" x=\"0\" y=\"0\" width=\"465.8\" height=\"260\" preserveAspectRatio=\"none\"/><rect class=\"dimmer\" x=\"0\" y=\"0\" width=\"465.8\" height=\"260\" fill=\"#1B1512\"/>`}}," for n in range(8))
    line = h[i:j]
    if not line.rstrip().endswith(','): line += ','
    h = h[:i] + line + ent + h[j:]
i = h.find('const GLOSS=') + len('const GLOSS='); j = h.find('};', i) + 1
GL = json.loads(h[i:j]); GL.update({k: v for k, v in G.items() if k not in GL})
h = h[:i] + json.dumps(GL, ensure_ascii=False) + h[j:]
keys = set(re.findall(r'\|([a-z]+)\]', '\n'.join(pages)))
assert not (keys - set(GL)), keys - set(GL)
open(A + 'index.html', 'w').write(h)
print('ok', len(keys))
