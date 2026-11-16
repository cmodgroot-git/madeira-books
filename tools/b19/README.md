# Book 19: «Um Jantar a Três» — id `jantar3` (published Nov 16, 2026)

Rita's mother flies in from Lisbon on the day of Rita's first dinner with Tiago. Rita asks «Sim. Mas seria um problema se
fôssemos três?» — «Claro!». The mother's suitcase is sent to Porto by mistake (lost-luggage form at the desk); at home she
picks a blue dress for Rita; dinner for three in the Zona Velha; Tiago holds Rita's hand: «da próxima vez, poderíamos
jantar só os dois?»; the suitcase is found; the mother sees them holding hands: «E eu que pensava que a surpresa era eu…»
Language step: passive with *ser* (foi enviada, vai ser entregue, foi encontrada) + conditional (seria, poderíamos).

## What is in the book
- 8 pages, 15 new tappable keys (mãe, bilhete, aeroporto, avião, mala, tapete rolante, passageiros, funcionária,
  formulário, armário, roupas, vestido, sala, prato, cadeira), 29 tappable words in all; `balcao` widened to "counter".
- Pictures: Krea 3, reviewed as a set (`books/19-jantar3/art/krea_urls.txt`). After the review p7 was fixed by a regional
  edit (one tablecloth, the table the size of p6/p8, the smudge gone).
- Tap regions `hl_book19.py` (SAM, `hlmask.py`); action cues `act19.json`: *mãos dadas* hold, *sorri* sound.
- Scene life `life19.py`: curtain in the breeze (p1, p2), lamps (p5), street lamps and a flickering candle (p6–p8).
- Narration: Marta (narration, Rita, the mother, the clerk), Pedro (Tiago's line on p7). Recorded as one Marta take,
  one Pedro take, one word batch and the title (`takes19.py`), cut with `tools/rerecord/cuttake.py`, assembled and aligned
  with `audio19.py pages clips`. All 8 pages aligned with no gaps; all 15 word clips and the title checked.
- Meanings: `gloss19.json`.

## Rebuild
WORK=/home/claude/work/b19: masters/ (copy of `books/19-jantar3/art/b19p*.jpg`), hlcache/, seg/, audio/.
`takes19.py` → record → `cuttake.py <take> <url>` (from tools/rerecord, WORK set) → `audio19.py pages clips` →
`hlmask.py cut <0..7>` (one page per process) → `life19.py build` → `build19.py text media`.
`data/` keeps narr19.json, clips19.json, life19.json, takes.json and segs.json (copy narr19/clips19 into WORK/audio and
life19 into WORK to rebuild without re-recording; the segment wavs are not kept).

## Ledger
Book 19 text: readability 79% (rule ≥ 80%), recycling 31, 27 of 50 new forms in the top 2,000.
