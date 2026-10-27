"""Add book 12 (carro) to the library."""
import json, re
from PIL import Image
S = '/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'
A = S + 'artifact-files/87e1712e-5e90-4175-b828-2581544915d4/'
FIN = open(S + 'b12/final.txt').read().split()
for n, f in enumerate(FIN, 1):
    im = Image.open(S + f'b12/{f}.png').convert('RGB').resize((1600, 898), Image.LANCZOS)
    im.save(S + f'gen/masters/b12p{n}.jpg', quality=95)
    im.resize((1200, 674), Image.LANCZOS).save(A + f'img/b12p{n}.jpg', quality=86)
    Image.open(A + f'img/b12p{n}.jpg').convert('RGB').resize((192, 108), Image.LANCZOS).save(A + f'img/t/b12p{n}.webp', quality=72, method=6)
pages = [
"Numa manhã de sábado, a [Rita|rita] e o [Tiago|tiago] tomam um [café|cafe] numa [esplanada|esplanada]. No [portátil|portatil], ela vê [anúncios|anuncios] de carros usados. — Este [preço|preco] é bom demais — diz o Tiago. — Quando é bom demais, há sempre um problema.",
"No [stand|stand] de carros usados, um [vendedor|vendedor] de [gravata|gravata] mostra-lhes um [carro|carro] vermelho a brilhar. O Tiago abre o [capô|capo] e olha para o [motor|motor]. Depois [abana a cabeça|abanacabeca]. — Brilha muito por fora — diz ele baixinho — mas o motor está cansado.",
"O segundo carro parece novo, mas o [painel|painel] mostra duzentos mil [quilómetros|quilometros]. — Está como novo! — [jura|jura] o vendedor, com a mão no peito. O Tiago [ri-se|rise]. «Se calhar não devia confiar em vendedores de gravata», pensa a Rita.",
"Mesmo assim, a Rita quer experimentar. Senta-se ao [volante|volante], põe o [cinto|cinto] e mete a primeira [mudança|mudanca]. Numa rua muito inclinada, o carro [vai abaixo|vaiabaixo] e um [autocarro|autocarro] [buzina|buzina] atrás dela. — Calma — diz o Tiago. — Primeiro, o [travão de mão|travaomao].",
"Num [semáforo|semaforo] vermelho, o [telemóvel|telemovel] da Rita [vibra|vibra]. É uma [mensagem|mensagem] da Ana: «O João convidou-me para jantar. Hoje! O que é que eu visto?» A Rita sorri. — Finalmente! — diz o Tiago, que também leu a mensagem.",
"À tarde, vão ver o carro de uma [senhora|senhora] idosa, numa [garagem|garagem] com [vasos|vasos] de [flores|flores]. É pequeno, azul e muito [limpo|limpo]. — Só o conduzi para ir à igreja e ao mercado — explica ela. O Tiago olha para o motor e [sorri|sorri].",
"A Rita gostaria de pagar um pouco menos. — Podia fazer-me um desconto? A senhora pensa um pouco. — Desconto não, mas dou-lhe um [bolo de mel|bolodemel]. Riem-se todos, e a Rita [assina|assina] o [contrato|contrato] com a [caneta|caneta] da senhora.",
"Ao fim do dia, a Rita [estaciona|estaciona] à porta da [oficina|oficina] do Tiago. Ela dá-lhe um [beijinho|beijinhos] na [cara|cara], e ele fica [vermelho|vermelha] como um capacete. Depois olha para as [chaves|chaves] e pensa: «Espero que a Ana também esteja a ter uma boa noite.»",
]
G = {
 'anuncios': ['ads (listings)', 'Anzeigen, Inserate', 'annonces', 'anuncios', 'advertenties', 'ogłoszenia'],
 'preco': ['price', 'Preis', 'prix', 'precio', 'prijs', 'cena'],
 'stand': ['car dealership (stand de carros)', 'Autohaus, Gebrauchtwagenhändler', "concession automobile", 'concesionario de coches', 'autohandel, garage', 'komis samochodowy'],
 'vendedor': ['salesman', 'Verkäufer', 'vendeur', 'vendedor', 'verkoper', 'sprzedawca'],
 'gravata': ['tie (necktie)', 'Krawatte', 'cravate', 'corbata', 'stropdas', 'krawat'],
 'capo': ['bonnet (hood of a car)', 'Motorhaube', 'capot', 'capó', 'motorkap', 'maska (samochodu)'],
 'motor': ['engine', 'Motor', 'moteur', 'motor', 'motor', 'silnik'],
 'abanacabeca': ['shakes his head', 'schüttelt den Kopf', 'secoue la tête', 'niega con la cabeza', 'schudt zijn hoofd', 'kręci głową'],
 'painel': ['dashboard, instrument panel', 'Armaturenbrett, Anzeige', 'tableau de bord', 'salpicadero, cuadro de mandos', 'dashboard', 'deska rozdzielcza'],
 'quilometros': ['kilometres', 'Kilometer', 'kilomètres', 'kilómetros', 'kilometer', 'kilometry'],
 'jura': ['swears (promises)', 'schwört', 'jure', 'jura', 'zweert', 'przysięga'],
 'cinto': ['seatbelt', 'Sicherheitsgurt', 'ceinture de sécurité', 'cinturón de seguridad', 'veiligheidsgordel', 'pas bezpieczeństwa'],
 'mudanca': ['gear (mete a primeira mudança: puts it in first gear)', 'Gang (legt den ersten Gang ein)', 'vitesse (passe la première)', 'marcha (mete la primera)', 'versnelling (zet hem in de eerste)', 'bieg (wrzuca jedynkę)'],
 'vaiabaixo': ['stalls (the engine cuts out)', 'würgt ab (der Motor geht aus)', 'cale', 'se cala, se le cala', 'slaat af', 'gaśnie (silnik)'],
 'buzina': ['honks (the horn)', 'hupt', 'klaxonne', 'pita, toca el claxon', 'toetert', 'trąbi'],
 'travaomao': ['handbrake', 'Handbremse', 'frein à main', 'freno de mano', 'handrem', 'hamulec ręczny'],
 'semaforo': ['traffic light', 'Ampel', 'feu (de circulation)', 'semáforo', 'verkeerslicht', 'sygnalizacja świetlna'],
 'senhora': ['lady', 'Dame', 'dame', 'señora', 'dame, mevrouw', 'pani'],
 'garagem': ['garage', 'Garage', 'garage', 'garaje', 'garage', 'garaż'],
 'limpo': ['clean', 'sauber', 'propre', 'limpio', 'schoon', 'czysty'],
 'bolodemel': ['bolo de mel (Madeira honey cake, dark and spiced)', 'bolo de mel (Madeira-Honigkuchen, dunkel und gewürzt)', 'bolo de mel (gâteau au miel de Madère, sombre et épicé)', 'bolo de mel (bizcocho de miel de Madeira, oscuro y especiado)', 'bolo de mel (Madeirese honingcake, donker en gekruid)', 'bolo de mel (maderskie ciasto miodowe, ciemne i korzenne)'],
 'assina': ['signs', 'unterschreibt', 'signe', 'firma', 'ondertekent', 'podpisuje'],
 'contrato': ['contract', 'Vertrag', 'contrat', 'contrato', 'contract', 'umowa'],
 'caneta': ['pen', 'Kugelschreiber, Stift', 'stylo', 'bolígrafo', 'pen', 'długopis'],
 'estaciona': ['parks', 'parkt', 'se gare', 'aparca', 'parkeert', 'parkuje'],
 'oficina': ["workshop (a mechanic's garage)", 'Werkstatt', 'atelier, garage (de mécanicien)', 'taller', 'werkplaats, garage', 'warsztat'],
}
h = open(A + 'index.html').read()
if 'const pages12=' not in h:
    k = h.find('const pages11=['); e = h.find('];', k) + 2
    h = h[:e] + '\nconst pages12=[\n' + ',\n'.join(json.dumps(p, ensure_ascii=False) for p in pages) + '\n];' + h[e:]
    old = "{id:'corridas',title:'O Dia das Corridas',cams:[],scenes:pages11.map(()=>()=>''),pages:pages11,cover:5},"
    assert old in h
    h = h.replace(old, old + "\n  {id:'carro',title:'O Carro da Rita',cams:[],scenes:pages12.map(()=>()=>''),pages:pages12,cover:5},", 1)
    m = re.search(r"corridas:'img/b11p6v2\.jpg'", h); assert m
    h = h.replace(m.group(0), m.group(0) + ",carro:'img/b12p6.jpg'", 1)
    i = h.find("'corridas:7':"); j = h.find('\n', i)
    ent = ''.join(f"\n'carro:{n}':{{w:465.8,svg:()=>`<image id=\"carro{n}ph\" href=\"img/b12p{n+1}.jpg\" x=\"0\" y=\"0\" width=\"465.8\" height=\"260\" preserveAspectRatio=\"none\"/><rect class=\"dimmer\" x=\"0\" y=\"0\" width=\"465.8\" height=\"260\" fill=\"#1B1512\"/>`}}," for n in range(8))
    line = h[i:j]
    end = ''
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
