"""Add book 10 (novacasa) to the library."""
import json
from PIL import Image
S = '/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'
A = S + 'artifact-files/87e1712e-5e90-4175-b828-2581544915d4/'
for n in range(1, 9):
    im = Image.open(S + f'gen/masters/b10p{n}.jpg').convert('RGB')
    im.resize((1200, 674), Image.LANCZOS).save(A + f'img/b10p{n}.jpg', quality=86)
    Image.open(A + f'img/b10p{n}.jpg').convert('RGB').resize((192, 108), Image.LANCZOS).save(A + f'img/t/b10p{n}.webp', quality=72, method=6)

pages = [
"No sábado de manhã, uma [carrinha|carrinha] branca para à porta do prédio velho da Rita. Quem conduz é o [Tiago|tiago], um amigo do João: é [mecânico|mecanico] e corre de karts aos domingos. — Bom dia! Onde estão as caixas? — pergunta ele, com o [boné|bone] ao contrário.",
"O João e o Tiago [carregam|carregam] o [colchão|colchao] pela [escada|escada]. A Rita leva uma [planta|planta] e a Ana, o [espelho|espelho]. — Cuidado! — grita a Rita. Tarde demais: o espelho bate na parede e [parte-se|partese]. — Sete anos de azar — ri-se o Tiago.",
"Na Zona Velha, a [rua|rua] é estreita demais para a carrinha, por isso têm de levar tudo à mão. Uma [vizinha|vizinha] idosa espreita da [janela|janela] e oferece-lhes [água|agua] fresca. — Bem-vinda ao bairro, menina!",
"Dentro de casa, o Tiago [monta|monta] a [estante|estante] com uma [chave de fendas|chavefendas]. Faltam dois [parafusos|parafusos]. — Talvez estejam no [chão|chao]… — diz a Ana, de joelhos, à procura deles.",
"A Rita [pendura|pendura] um [quadro|quadro] na [parede|parede]: uma fotografia da praia do Seixal. O João segura a escada. — Está [torto|torto]! — dizem a Ana e o Tiago ao mesmo tempo.",
"Ao fim da tarde, a casa está quase pronta: o [sofá|sofa], o [tapete|tapete] azul e as [cortinas|cortinas] brancas a dançar ao vento. A Rita [arruma|arruma] os [livros|livros] na estante e pensa: «Se não fossem os meus amigos, ainda estaria a carregar caixas!»",
"Ao jantar, pedem [pizza|pizza] pelo telemóvel e comem sentados no chão, entre as caixas vazias. O João dá a última [fatia|fatia] à Ana. O Tiago [pisca o olho|piscaolho] à Rita.",
"À noite, na varanda, [brindam|brindam] com [poncha|poncha] à casa nova. Lá em baixo brilham as [luzes|luzes] da cidade e o [porto|porto]. — À casa nova! — E aos vizinhos simpáticos! — diz a senhora da janela ao lado, com o seu [copo|copo] na mão.",
]
G = {
 'carrinha': ['van', 'Lieferwagen', 'camionnette', 'furgoneta', 'busje', 'furgonetka'],
 'tiago': ['Tiago (a name)', 'Tiago (Name)', 'Tiago (prénom)', 'Tiago (nombre)', 'Tiago (naam)', 'Tiago (imię)'],
 'mecanico': ['mechanic', 'Mechaniker', 'mécanicien', 'mecánico', 'monteur (automonteur)', 'mechanik'],
 'bone': ['cap (baseball cap)', 'Schirmmütze, Kappe', 'casquette', 'gorra', 'pet', 'czapka z daszkiem'],
 'carregam': ['(they) carry', '(sie) tragen', '(ils) portent', '(ellos) cargan, llevan', '(zij) dragen', '(oni) niosą'],
 'colchao': ['mattress', 'Matratze', 'matelas', 'colchón', 'matras', 'materac'],
 'planta': ['plant (pot plant)', 'Pflanze', 'plante', 'planta', 'plant', 'roślina'],
 'espelho': ['mirror', 'Spiegel', 'miroir', 'espejo', 'spiegel', 'lustro'],
 'partese': ['(it) breaks', '(er) zerbricht', '(il) se casse', 'se rompe', 'breekt', 'tłucze się'],
 'monta': ['assembles, puts together', 'baut zusammen', 'monte, assemble', 'monta', 'zet in elkaar', 'składa'],
 'estante': ['bookcase, shelves', 'Regal', 'étagère, bibliothèque', 'estantería', 'boekenkast', 'regał'],
 'chavefendas': ['screwdriver', 'Schraubenzieher', 'tournevis', 'destornillador', 'schroevendraaier', 'śrubokręt'],
 'parafusos': ['screws', 'Schrauben', 'vis', 'tornillos', 'schroeven', 'śruby'],
 'chao': ['floor', 'Boden', 'sol (par terre)', 'suelo', 'vloer', 'podłoga'],
 'pendura': ['hangs (up)', 'hängt auf', 'accroche', 'cuelga', 'hangt op', 'wiesza'],
 'quadro': ['picture (in a frame)', 'Bild (gerahmt)', 'tableau, cadre', 'cuadro', 'schilderij, ingelijste foto', 'obraz (w ramie)'],
 'torto': ['crooked', 'schief', 'de travers', 'torcido', 'scheef', 'krzywo'],
 'tapete': ['rug', 'Teppich', 'tapis', 'alfombra', 'kleed', 'dywan'],
 'cortinas': ['curtains', 'Vorhänge', 'rideaux', 'cortinas', 'gordijnen', 'zasłony'],
 'arruma': ['puts away, tidies', 'räumt ein', 'range', 'ordena, coloca', 'ruimt op', 'układa'],
 'livros': ['books', 'Bücher', 'livres', 'libros', 'boeken', 'książki'],
 'pizza': ['pizza', 'Pizza', 'pizza', 'pizza', 'pizza', 'pizza'],
 'fatia': ['slice', 'Stück', 'part', 'porción', 'punt', 'kawałek'],
 'piscaolho': ['winks', 'zwinkert', "fait un clin d'œil", 'guiña el ojo', 'knipoogt', 'puszcza oko'],
 'brindam': ['(they) toast, clink glasses', '(sie) stoßen an', '(ils) trinquent', '(ellos) brindan', '(zij) proosten', '(oni) wznoszą toast'],
}
h = open(A + 'index.html').read()
if 'const pages10=' not in h:
    k = h.find('const pages9=['); e = h.find('];', k) + 2
    h = h[:e] + '\nconst pages10=[\n' + ',\n'.join(json.dumps(p, ensure_ascii=False) for p in pages) + '\n];' + h[e:]
    old = "{id:'garajau',title:'O Mergulho no Garajau',cams:[],scenes:pages9.map(()=>()=>''),pages:pages9,cover:4},"
    assert old in h
    h = h.replace(old, old + "\n  {id:'novacasa',title:'A Casa Nova',cams:[],scenes:pages10.map(()=>()=>''),pages:pages10,cover:7},", 1)
    h = h.replace("garajau:'img/b9p5.jpg'}", "garajau:'img/b9p5.jpg',novacasa:'img/b10p8.jpg'}", 1)
    assert "novacasa:'img/b10p8.jpg'" in h
    i = h.find("'garajau:7':"); j = h.find('\n', i)
    ent = ''.join(f"\n'novacasa:{n}':{{w:465.8,svg:()=>`<image id=\"novacasa{n}ph\" href=\"img/b10p{n+1}.jpg\" x=\"0\" y=\"0\" width=\"465.8\" height=\"260\" preserveAspectRatio=\"none\"/><rect class=\"dimmer\" x=\"0\" y=\"0\" width=\"465.8\" height=\"260\" fill=\"#1B1512\"/>`}}," for n in range(8))
    line = h[i:j]
    if not line.rstrip().endswith(','): line += ','
    h = h[:i] + line + ent + h[j:]
# GLOSS
i = h.find('const GLOSS=') + len('const GLOSS='); j = h.find('};', i) + 1
GL = json.loads(h[i:j]); GL.update({k: v for k, v in G.items() if k not in GL})
h = h[:i] + json.dumps(GL, ensure_ascii=False) + h[j:]
import re
keys = set(re.findall(r'\|([a-z]+)\]', '\n'.join(pages)))
assert not (keys - set(GL)), keys - set(GL)
open(A + 'index.html', 'w').write(h)
print('ok', len(keys))
