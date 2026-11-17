# Book 21: «Uma Casa para Três» — id `casa3`

Status: PUBLISHED Nov 16, 2026 (book 21 in the library; artifact version 1794882500-1066).
Story (practical): Ana says yes to moving in with João, but her dog comes too. Marta shows a modern flat in central
Funchal (lift, big balcony, €1,200 rent — too dear); an old flat in Câmara de Lobos with an old stove and the fishing
boats in the window (João's father fished there forty years). Their first argument on the harbour wall at night (far from
Ana's work, two cars needed), then Ana takes his hand. Inês reads the contract: «Não são aceites animais». The landlady,
an old widow on the ground floor, recognises João as Manuel's son, the dog lies at her feet, she strikes out the line,
gives them the keys — «Visitem-me ao domingo». Pizza on the empty floor with Rita and Tiago; Ana asks Rita when *they*
will move in together, and Rita blushes.
Language step: para + personal infinitive (pagarmos, irmos, ficarem), antes de + personal infinitive (assinarem).
Ledger: readability 91% counting forms, well known 70%, 31 old words back, 14 conversation words, 7 new tappable words.
New character: the landlady (`books/21-casa3/art/landlady_design.jpg`; needs a character-sheet row if she returns).

## Pictures
Krea 3, 2K, thinking high (`prompts21.py`, `refs.txt`, ids in `books/21-casa3/art/krea_urls.txt`); about 1,700 units.
Fixed by regional edits before review: p3 Ana's hair (had Rita's bangs), p5 Inês's bangs, p6 João (grey, moustache) and Ana.

## Build
- Tap regions `hl_book21.py` (24 keys, all tested); action cues none (`act21.json` empty).
- Scene life `life21.py`: marina water (p1), moonlit sea + moon glow (p4), harbour water in the window + bulb (p8).
- Narration: Marta (narration, Ana, Inês, the landlady), Pedro (João's 3 lines). One take each + word batch + title
  (`takes21.py`), all cut at ≥ 0.97 similarity; `audio21.py pages clips`; all 8 pages aligned, no gaps.
- Meanings `gloss21.json` (7 new keys); plain-word meanings for 40 new forms in `tools/fgloss/fg5.tsv`.
- Rebuild as book 19 (`tools/b19/README.md`), WORK=/home/claude/work/b21; `data/` keeps narr/clips/life/takes/segs.
