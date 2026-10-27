"""Add book 9 (garajau) to the library."""
import json
from PIL import Image
S = '/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'
A = S + 'artifact-files/87e1712e-5e90-4175-b828-2581544915d4/'
SRC = ['p1f1.png', 'p2a.png', 'p3b.png', 'p4b.png', 'p5a.png', 'p6a.png', 'p7a.png', 'p8e.png']
for n, s in enumerate(SRC, 1):
    im = Image.open(S + 'b9/' + s).convert('RGB').resize((1600, 898), Image.LANCZOS)
    im.save(S + f'gen/masters/b9p{n}.jpg', quality=92)
    im.resize((1200, 674), Image.LANCZOS).save(A + f'img/b9p{n}.jpg', quality=86)
    Image.open(A + f'img/b9p{n}.jpg').convert('RGB').resize((192, 108), Image.LANCZOS).save(A + f'img/t/b9p{n}.webp', quality=72, method=6)

pages = [
"No sábado, a [Rita|rita], a [Ana|ana] e a [Marta|marta] vão ao Garajau. Ao lado da [estação|estacao] do [teleférico|teleferico], a [estátua|estatua] do Cristo Rei abre os [braços|braco] sobre o mar. As três [entram|entram] na [cabine|cabine]. — Espero que a água não esteja muito fria — diz a Rita.",
"Na praia há [seixos|seixos] em vez de areia. O [João|joao] já está à espera com as [garrafas|garrafas], as [máscaras|mascaras] e as [barbatanas|barbatanas]. Dá dois [beijinhos|beijinhos] à Ana, e a Ana fica [vermelha|vermelha] outra vez. A [Marta|marta] vai logo ver o equipamento.",
"A Rita, já de [fato de mergulho|fatomergulho], está [nervosa|nervosa]. — E se eu não conseguir respirar? A Marta explica os [sinais|sinais]: o [polegar|polegar] para cima quer dizer «subir», e um círculo com os [dedos|dedos] quer dizer «está tudo bem». — Vais adorar — diz ela.",
"Debaixo de [água|agua], tudo fica silencioso e [azul|azul]. Só se ouvem as [bolhas|bolhas]. À volta da Rita nadam [peixes|peixe] de todas as cores, e um [mero|mero] [gordo|gordo] olha para ela com cara de quem não está nada impressionado.",
"De repente, o João aponta para uma [tartaruga|tartaruga]! Ela [nada|nada] devagar entre as [rochas|rochas]. O João dá a [mão|mao] à Ana para ela se aproximar. A Rita pensa: «Talvez não seja só por causa da tartaruga…»",
"Numa [fenda|fenda] da rocha, a Rita descobre um [polvo|polvo]. Quando ela se aproxima, ele fica [cor-de-laranja|corlaranja]! A Rita esquece o medo e faz à Marta o [sinal|sinais] de «está tudo bem».",
"Mais tarde, sentados nas [toalhas|toalha], bebem [chocolate|chocolate] quente do [termo|termo]. Os [chinelos|chinelos] da Ana [secam|secam] ao sol. — Gostaria de voltar no próximo sábado — diz a Rita. — Eu também — diz a Ana, a olhar para o João.",
"Na estação, ao [pôr do sol|pordosol], o [telemóvel|telemovel] da Rita [vibra|vibra]. É uma [mensagem|mensagem] da agência: «O apartamento da Zona Velha é seu!» A Rita [grita|grita] de alegria e a Ana [abraça|abraca]-a. O João bate [palmas|palmas] e a Marta sorri: ela já sabia.",
]
h = open(A + 'index.html').read()
if 'const pages9=' not in h:
    k = h.find('const pages8=['); e = h.find('];', k) + 2
    h = h[:e] + '\nconst pages9=[\n' + ',\n'.join(json.dumps(p, ensure_ascii=False) for p in pages) + '\n];' + h[e:]
    old = "{id:'casa',title:'A Rita Procura Casa',cams:[],scenes:pages8.map(()=>()=>''),pages:pages8,cover:6},"
    assert old in h
    h = h.replace(old, old + "\n  {id:'garajau',title:'O Mergulho no Garajau',cams:[],scenes:pages9.map(()=>()=>''),pages:pages9,cover:4},", 1)
    h = h.replace("casa:'img/b8p7.jpg'}", "casa:'img/b8p7.jpg',garajau:'img/b9p5.jpg'}", 1)
    assert "garajau:'img/b9p5.jpg'" in h
    i = h.find("'casa:7':"); j = h.find('\n', i)
    ent = ''.join(f"\n'garajau:{n}':{{w:465.8,svg:()=>`<image id=\"garajau{n}ph\" href=\"img/b9p{n+1}.jpg\" x=\"0\" y=\"0\" width=\"465.8\" height=\"260\" preserveAspectRatio=\"none\"/><rect class=\"dimmer\" x=\"0\" y=\"0\" width=\"465.8\" height=\"260\" fill=\"#1B1512\"/>`}}," for n in range(8))
    line = h[i:j]
    if not line.rstrip().endswith(','): line += ','
    h = h[:i] + line + ent + h[j:]
    open(A + 'index.html', 'w').write(h)
print('ok')
