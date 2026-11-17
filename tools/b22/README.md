# Book 22: «O Jogo de Domingo» — id `jogo`

Status: PUBLISHED Nov 16, 2026 (artifact version 1794890924-33e7).
Story (sports): a charity football match for the firefighters on the Câmara de Lobos pitch, Tiago's workshop (navy) against
João's restaurant (white); Dona Graça comes with her Marítimo scarf (her late husband played there 30 years); Bruno referees;
Tiago heads a goal, fouls João (yellow card); Graça scolds them at half-time, they shake hands; João's penalty: 1–1, €800 raised;
dinner at Graça's; Tiago to Rita: «Tenho pensado muito no que a Ana te perguntou.» — «Eu também tenho pensado nisso.»
Language step (rung 15): ter + past participle, pretérito perfeito composto (tenho treinado, tens falado, tenho visto, tenho pensado).
Spiral: imperfeito (jogavam), pretérito perfeito (jogou, deram).
Ledger: readability 91% counting forms, 31 old words back, 26 recycled, 13 conversation words, 6 new tappable words (3 common).

## Pictures
Krea 3, 2K, high (`prompts22.py`; ids `books/22-jogo/art/krea_urls.txt`). Fixes: car badge (p1), referee's shirt logo (p3, before
p3 became the pitch reference), João's face (p5, p7), p6 repainted (the handshake), p8 hand-hold, p7 repainted after the user
said it made no sense (keeper far from the goal, scorer at midfield, floating women): now seen from behind João at the spot,
ball low in the right corner, keeper diving left. ~1,850 units for the set.

## Build
- Tap regions `hl_book22.py` (12 regions; *jogo* on p1 not shown). Action cues none.
- Scene life `life22.py`: sea beyond the pitch (p3), street lamp (p8).
- Narration: Marta (narration, Rita, Graça), Pedro (Tiago ×3, João ×1). `takes22.py`, `audio22.py pages clips`, `build22.py text media`.
- Meanings `gloss22.json`; plain forms `tools/fgloss/fg7.tsv`.
