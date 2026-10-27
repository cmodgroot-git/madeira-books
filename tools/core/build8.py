"""Add book 8 (casa) to the library: pictures, thumbnails, text, story entry, empty page entries, cover."""
import re, json
from PIL import Image
S = '/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'
A = S + 'artifact-files/87e1712e-5e90-4175-b828-2581544915d4/'
SRC = ['p1c', 'p2a', 'p3a', 'p4e', 'p5b', 'p6a', 'p7a', 'p8b']
for n, s in enumerate(SRC, 1):
    im = Image.open(S + f'b8/{s}.png').convert('RGB').resize((1600, 898), Image.LANCZOS)
    im.save(S + f'gen/masters/b8p{n}.jpg', quality=92)
    im.resize((1200, 674), Image.LANCZOS).save(A + f'img/b8p{n}.jpg', quality=86)
    Image.open(A + f'img/b8p{n}.jpg').convert('RGB').resize((192, 108), Image.LANCZOS).save(A + f'img/t/b8p{n}.webp', quality=72, method=6)

pages = [
"A [Rita|rita] mora num apartamento pequeno em Funchal. Hoje chegou uma [carta|carta]: o [prédio|predio] foi vendido e vai ser um bed and breakfast! A Rita tem de sair até ao fim do mês. Ela [liga|liga] à Marta pelo [telemóvel|telemovel]: — Gostaria de ver apartamentos. Podia ajudar-me?",
"No dia seguinte, a [Marta|marta] espera-a à [porta|porta] da [agência|agencia], na [avenida|avenida] do mar. Tem o cabelo [curto|curto] e um molho de [chaves|chaves] na mão. — O João falou-me de ti — diz ela. — E da Ana também... muitas vezes! Talvez ele goste mesmo dela, pensa a Rita.",
"O primeiro apartamento fica no quinto andar, sem elevador. Quando chegam lá acima, a Rita está [cansada|cansada]. Ela [abre|abre] a [janela|janela]... e só vê uma [parede|parede] [cinzenta|cinzento]! — Bem, pelo menos é sossegado — diz a Marta, a rir.",
"O segundo fica num [prédio|predio] moderno, com [elevador|elevador] e uma [cozinha|cozinha] nova. Mas, na [varanda|varanda], há muito barulho do [trânsito|transito] e dos [táxis|taxis]. A Rita [tapa|tapa] os [ouvidos|ouvidos]. — Espero que o terceiro seja mais calmo!",
"Ao almoço, numa [esplanada|esplanada] da [marina|marina], entre os [barcos|barcos], a Rita come uma [salada|salada], um pouco [desiludida|desiludida]. A Marta mostra-lhe no [telemóvel|telemovel] fotografias do fundo do mar: peixes e uma tartaruga. Aos fins de semana, ela mergulha no Garajau.",
"O terceiro fica na Zona Velha, numa [rua|rua] estreita de [pedra|pedra]. As [portas|porta] estão [pintadas|pintadas] com cores alegres. A casa tem [azulejos|azulejos] azuis à entrada e uma [varanda|varanda] cheia de [vasos|vasos] com [flores|flores].",
"Da varanda, a Rita vê o [mar|mar], os [telhados|telhados] vermelhos e o [teleférico|teleferico] a subir para o Monte. Ela [fecha os olhos|olhos] e imagina-se ali todas as manhãs, com um café. — Gostaria de ficar com este! — Eu sabia — [sorri|sorri] a Marta.",
"À noite, entre as [caixas|caixas], a Rita liga à Ana por [videochamada|videochamada] no [portátil|portatil]: — A Marta convidou-nos para mergulhar no Garajau, no sábado. O João também vai! A Ana [tapa|tapa] a [cara|cara]. O [cão|cao], no [sofá|sofa], [abana|abana] a [cauda|cauda].",
]
h = open(A + 'index.html').read()
if 'const pages8=' not in h:
    k = h.find('const pages7=['); e = h.find('];', k) + 2
    h = h[:e] + '\nconst pages8=[\n' + ',\n'.join(json.dumps(p, ensure_ascii=False) for p in pages) + '\n];' + h[e:]
    old = "{id:'seixal',title:'A Ana Volta ao Norte',cams:[],scenes:pages7.map(()=>()=>''),pages:pages7,cover:5},"
    assert old in h
    h = h.replace(old, old + "\n  {id:'casa',title:'A Rita Procura Casa',cams:[],scenes:pages8.map(()=>()=>''),pages:pages8,cover:6},", 1)
    h = h.replace("seixal:'img/b7p6.jpg'}", "seixal:'img/b7p6.jpg',casa:'img/b8p7.jpg'}", 1)
    assert "casa:'img/b8p7.jpg'" in h
    i = h.find("'seixal:7':"); j = h.find('\n', i)
    ent = ''.join(f"\n'casa:{n}':{{w:465.8,svg:()=>`<image id=\"casa{n}ph\" href=\"img/b8p{n+1}.jpg\" x=\"0\" y=\"0\" width=\"465.8\" height=\"260\" preserveAspectRatio=\"none\"/><rect class=\"dimmer\" x=\"0\" y=\"0\" width=\"465.8\" height=\"260\" fill=\"#1B1512\"/>`}}," for n in range(8))
    line = h[i:j]
    if not line.rstrip().endswith(','): line = line + ','
    h = h[:i] + line + ent + h[j:]
    open(A + 'index.html', 'w').write(h)
print('ok')
