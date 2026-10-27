# Book 18 (in progress): «Antes que Mudes de Ideias» — id `ribeira`

Status (Oct 27, 2026): text approved; first set of 8 pictures painted and shown to the user
(`books/18-ribeira/art/contact18.jpg`); waiting for the user's picture review. Paused for Krea credits
(about 450 units left; the plan renews about Nov 15, 2026).

Language step: *caso / para que / antes que* + present subjunctive (a canyoning safety briefing).
New friend: Bruno, firefighter and canyoning guide. Ends on Tiago asking Rita to dinner, no answer yet.

- `pages18.json` / `pages18.md` — the approved text with tags, new words, picture plan, outfits
- `prompts18.py` — builds `inputs18.json` (Krea inputs; uses `../b16/prompts.py` for the style block, `../b17/refs.txt` + `refs.txt`)
- `refs.txt` — `men`: a two-face reference (Tiago left, Bruno right), `books/18-ribeira/art/men18_faces.jpg`
- `books/18-ribeira/art/` — 1600×898 masters `b18p1..8.jpg`, `krea_urls.txt` (approved-candidate Krea URLs, edits, rejected tries)

## Open points to raise with the user at the picture review
- p7: *sobe* (Tiago climbs back up) is not shown — the picture is the jump; flag it as a not-shown action.
- p7: João (blue helmet) looks too much like Tiago (curly hair, beard).
- p1: Tiago's cap is backwards (asked forwards).
- p8: everyone barefoot on gravel; towel colours differ from the plan (minor).
- p5: the laurel pigeon is a little large and close.
- Forest pages are a bit darker/denser than book 1 (black wetsuits).

## Next steps
1. User review of the contact sheet → fix only the pages they mark (regional edits ~150 units each).
2. Build: `build18.py` (copy `tools/b16/build16.py`), highlights, action cues, animation, gloss (six languages).
3. Audio after credits renew: 8 page narrations, the title, word clips for the new forms.

Outfits: canyoning — black wetsuits, harness, gloves, boots; helmets Rita white, Ana mustard, João blue, Tiago red, Bruno orange (orange rope bag).
Page 1: Rita terracotta hoodie, black leggings; Ana deep teal hoodie, jeans; João navy t-shirt, grey jeans; Tiago light grey t-shirt, jeans, red cap; Bruno dark-red t-shirt, khaki shorts.

## Ledger check (Oct 27, 2026 — `python3 tools/ledger.py --draft tools/b18/pages18.json`)
Written before the ledger rules existed, so it is a baseline rather than a pass/fail:
- readability 79% (rule ≥ 80%; books 9–17 scored 73–82%) — about on par
- recycling 36 under-used words come back (rule ≥ 15) — passes
- new tappable words in the top 2,000: 2 of 19 (rule: about half) — misses; canyoning words are specific by nature
Low-cost fix to offer at the picture review, no text or picture change: tag *homem* (p1, "um homem alto" = Bruno,
rank 228, never met) and *cabeça* (p4, "de cabeça" = João's head as he dives, rank 333, met 3 times).
Book 19 should lean the other way: a practical-life story full of everyday words.

## Words left out of the daily Review (to fix when work resumes)
Nine words have no picture region on the page where they first appear, so the Review skips them:
- looking words shown by a look-at beam, not a region: *vê*, *olha* (book 1) — free fix in code: crop the card
  from the beam's looker and target;
- actions not visible in their picture: *acorda*, *abre* (book 1 p2), *apanha*, *sobe* (book 1 p8), *ouvem* (book 3 p6),
  *pede* (book 4 p5), *vai abaixo* (book 12 p4) — fix by showing them in later books (recycling rule) and letting the
  Review use any page where the word has a region, not only its first page (small change in `revQueue`/`drawReview`;
  set-aside entries have step -1 and must be released when a region appears).
