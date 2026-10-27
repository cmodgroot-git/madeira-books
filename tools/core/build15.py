"""Add book 15 (festa) to the library."""
import json, re
from PIL import Image
S = '/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad/'
A = S + 'artifact-files/87e1712e-5e90-4175-b828-2581544915d4/'
FIN = open(S + 'b15/final.txt').read().split()
for n, f in enumerate(FIN, 1):
    im = Image.open(S + f'b15/{f}.png').convert('RGB').resize((1600, 898), Image.LANCZOS)
    im.save(S + f'gen/masters/b15p{n}.jpg', quality=95)
    im.resize((1200, 674), Image.LANCZOS).save(A + f'img/b15p{n}.jpg', quality=86)
    Image.open(A + f'img/b15p{n}.jpg').convert('RGB').resize((192, 108), Image.LANCZOS).save(A + f'img/t/b15p{n}.webp', quality=72, method=6)
pages = json.load(open(S + 'b15pages.json'))
G = {
 'grupo': ['group chat', 'Gruppenchat', 'groupe (de discussion)', 'grupo (de chat)', 'groepschat', 'czat grupowy'],
 'supermercado': ['supermarket', 'Supermarkt', 'supermarché', 'supermercado', 'supermarkt', 'supermarket'],
 'carrinho': ['shopping trolley, cart', 'Einkaufswagen', 'caddie, chariot', 'carrito', 'winkelwagen', 'wózek sklepowy'],
 'lista': ['(shopping) list', 'Einkaufsliste', 'liste (de courses)', 'lista (de la compra)', 'boodschappenlijst', 'lista zakupów'],
 'empurra': ['pushes', 'schiebt', 'pousse', 'empuja', 'duwt', 'pcha'],
 'prateleiras': ['shelves', 'Regale', 'étagères, rayons', 'estanterías', 'schappen, planken', 'półki'],
 'grade': ['crate (of beer bottles)', 'Bierkiste', 'casier (de bières)', 'caja (de botellas de cerveza)', 'krat (bier)', 'skrzynka (piwa)'],
 'coral': ['Coral (the Madeiran beer)', 'Coral (madeirisches Bier)', 'Coral (la bière de Madère)', 'Coral (la cerveza de Madeira)', 'Coral (het Madeirese bier)', 'Coral (piwo z Madery)'],
 'brisa': ['Brisa (Madeiran fruit soda)', 'Brisa (madeirische Limonade)', 'Brisa (soda madérien aux fruits)', 'Brisa (refresco de frutas de Madeira)', 'Brisa (Madeirese frisdrank)', 'Brisa (maderski napój owocowy)'],
 'gelo': ['ice', 'Eis (Eiswürfel)', 'glace, glaçons', 'hielo', 'ijs, ijsblokjes', 'lód'],
 'queijo': ['cheese', 'Käse', 'fromage', 'queso', 'kaas', 'ser'],
 'presunto': ['cured ham', 'Rohschinken', 'jambon cru', 'jamón curado', 'rauwe ham', 'szynka dojrzewająca'],
 'azeitonas': ['olives', 'Oliven', 'olives', 'aceitunas', 'olijven', 'oliwki'],
 'tremocos': ['lupin beans (salty bar snack)', 'Lupinenkerne (salziger Snack)', 'lupins (en saumure)', 'altramuces', 'lupinebonen (zoute snack)', 'łubin (słona przekąska)'],
 'batatasfritas': ['crisps, potato chips', 'Kartoffelchips', 'chips', 'patatas fritas (de bolsa)', 'chips', 'chipsy'],
 'chourico': ['chouriço (smoked sausage)', 'Chouriço (Räucherwurst)', 'chouriço (saucisson fumé)', 'chorizo portugués', 'chouriço (gerookte worst)', 'chouriço (wędzona kiełbasa)'],
 'caixa': ['checkout, till', 'Kasse', 'caisse', 'caja (del súper)', 'kassa', 'kasa'],
 'paga': ['pays', 'bezahlt', 'paie', 'paga', 'betaalt', 'płaci'],
 'sacos': ['bags', 'Taschen, Tüten', 'sacs', 'bolsas', 'tassen', 'torby'],
 'campainha': ['doorbell', 'Türklingel', 'sonnette', 'timbre', 'deurbel', 'dzwonek do drzwi'],
 'musica': ['music', 'Musik', 'musique', 'música', 'muziek', 'muzyka'],
 'gargalhadas': ['bursts of laughter', 'lautes Lachen', 'éclats de rire', 'carcajadas', 'gelach, schaterlachen', 'salwy śmiechu'],
 'lavaloica': ['wash the dishes', 'abwaschen', 'faire la vaisselle', 'fregar los platos', 'afwassen', 'zmywać naczynia'],
}
h = open(A + 'index.html').read()
if 'const pages15=' not in h:
    k = h.find('const pages14=['); e = h.find('];', k) + 2
    h = h[:e] + '\nconst pages15=[\n' + ',\n'.join(json.dumps(p, ensure_ascii=False) for p in pages) + '\n];' + h[e:]
    old = "{id:'voo',title:'O Voo da Rita',cams:[],scenes:pages14.map(()=>()=>''),pages:pages14,cover:5},"
    assert old in h
    h = h.replace(old, old + "\n  {id:'festa',title:'A Festa da Casa Nova',cams:[],scenes:pages15.map(()=>()=>''),pages:pages15,cover:6},", 1)
    m = "voo:'img/b14p6.jpg'"; assert m in h
    h = h.replace(m, m + ",festa:'img/b15p7.jpg'", 1)
    i = h.find("'voo:7':"); j = h.find('\n', i)
    ent = ''.join(f"\n'festa:{n}':{{w:465.8,svg:()=>`<image id=\"festa{n}ph\" href=\"img/b15p{n+1}.jpg\" x=\"0\" y=\"0\" width=\"465.8\" height=\"260\" preserveAspectRatio=\"none\"/><rect class=\"dimmer\" x=\"0\" y=\"0\" width=\"465.8\" height=\"260\" fill=\"#1B1512\"/>`}}," for n in range(8))
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
