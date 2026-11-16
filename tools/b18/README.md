# Book 18: «Antes que Mudes de Ideias» — id `ribeira` (published Nov 15, 2026)

Canyoning at Ribeira do Lajeado with Bruno, a firefighter and canyoning guide. Ends with Tiago asking Rita to dinner
on Saturday, no answer yet. Language step: *caso / para que / antes que* + present subjunctive.

## What is in the book
- 8 pages, 21 new tappable words (incl. *homem* and *cabeça*, tagged at the picture review), 54 tappable words in all.
- Pictures: Krea 3, reviewed as a set; after the user's review p1 (cap forwards), p5 (smaller pigeon), p7 (João's face)
  were fixed by regional edits and p8 repainted with p1 as reference so the car and van stand where they did on p1
  (`books/18-ribeira/art/krea_urls.txt`).
- Action cues (`act18.json`): hold — distribui, inclina, tremem, mãos dadas, arrumam; arrow — desce, corre, escorrega,
  salta; sound — gritar, ri-se, está a rir. *Espreita* has a look-at beam (Rita's eyes → the pool) instead of a region.
- Not shown: *sobe* (p7: Tiago climbing back up; the picture is the jump) — in `NOT_SHOWN`.
- Scene life (`life18.py`): waterfall + pool (p2, p3), water running down the chute + pool (p4), ferns (p5), pools (p6, p7).
- Narration: Marta narrates, Pedro reads Bruno's and Tiago's lines (first book in the new voices); word clips and title in
  Marta. Segments in `narr_segments.tsv`.
- Meanings: `gloss18.json` (six languages); *asas* widened to "wings", *corre* to "runs, flows".

## Rebuild
WORK=/home/claude/work/b18 (scratch: masters/, hlcache/, audio/). `data/` keeps narr18.json, clips18.json, life18.json:
copy them into WORK (`audio/` for the first two) to rebuild without re-recording. Steps: `hlmask.py cut <0..7>` (one page
per process), `hlmask.py sheet`, `life18.py build`, `narr.py`, `cutwords.py`, `build18.py text media`.

## Ledger (after tagging homem and cabeça)
readability 79% (rule ≥ 80%), recycling 36 (≥ 15), new tappable words in the top 2,000: 4 of 21 (rule: about half).
Book 19 should lean the other way: a practical-life story full of everyday words.

## Still open (from the Oct review, unchanged)
- The daily Review skips words without a region on their first page (beam words *vê*, *olha*, now *espreita*; and the
  not-shown actions). See the note in the stories skill.
- Books 1–17 are still in the old narrator (Matilda); re-recording them in Marta/Pedro is planned.
