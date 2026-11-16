# Book 19 (in progress): «Um Jantar a Três» — id `jantar3` (proposed)

Status (Nov 15, 2026, paused at the user's request): text APPROVED (checkpoint 1); pictures in progress (checkpoint 2 not yet shown).

Story: Rita's mother (from Lisbon, unnamed, about 60) announces by video call she arrives Saturday — the day of Rita's
first dinner with Tiago. Rita writes «Sim. Mas seria um problema se fôssemos três?» — «Claro!». At the airport the
mother's suitcase was sent to Porto by mistake (lost-luggage form); at home she picks a blue dress for Rita; dinner for
three in the Zona Velha; Tiago: «da próxima vez, poderíamos jantar só os dois?»; the suitcase is found; the mother sees
them holding hands: «E eu que pensava que a surpresa era eu…»
Language step: passive with *ser* (foi enviada, vai ser entregue, foi encontrada) + conditional (seria, poderíamos).
Ledger: readability 79% (rule 80), recycling 31, 27 of 50 new forms in the top 2,000; 15 new tappable words.

- `pages19.json` — approved text with tags
- `prompts19.py` — builds `inputs19.json` (Krea inputs); `refs.txt` — `mum` = the mother's design sheet
- Outfits: Rita cream cable-knit jumper + jeans (p1–5), cobalt-blue knee-length dress (p6–8, chosen by her mother on p5);
  Tiago white shirt, sleeves rolled, dark jeans, no cap; the mother: camel coat, cream blouse, burgundy scarf, grey
  trousers, brown handbag (her clothes are in the lost suitcase), short grey-brown layered hair, gold earrings.

## Krea results so far (https://gen.krea.ai/images/<id>.png)
- mum design sheet: 4897ca87-b723-42ec-849c-056a166f07c4 (good)
- p1: 7bc6a308-ee21-4630-847f-dc20e7135135 (good; Rita smiles rather than surprised — minor; an old moving box in the corner)
- p2: 09bdd48f-c321-4c10-a3ba-83e56fcc0b15 (good; paint out the garbled status-bar characters on the phone inset and
  write «Claro!» into the empty white bubble in code)
- p3: c541b70b-c997-4e40-b49d-bf990043d911 (good)
- p4: 2cae6881-3ca3-49e8-a0de-c5bfa6e67eab (good; regional edit to blank the garbled airport signs, top left and top right)
- p5: 2d08e512-fd23-4dc1-9ab4-390808d46f1e (good)
- p6 first try 84c01c74-db68-4c73-b51b-feb6bd23c69f REJECTED (mother standing; street beside the sea)
- p6 retry 7e0091e2-6479-4699-9ec4-b32a744412d2 — NOT YET CHECKED (narrow street, all three seated)

## Next steps
1. Check p6 retry; then write p7 and p8 in `prompts19.py` with the approved p6 as the third reference (same table and
   street): p7 dessert plates, the mother's chair empty (she is a few steps away on her phone), Tiago holding Rita's
   hand across the table; p8 the mother back with her phone, smiling at the two still holding hands.
2. Fixes above (p2 screen, p4 signs); contact sheet → user review (checkpoint 2).
3. Build as book 18 (`tools/b18/` working set; narration in Marta, Pedro for Tiago's lines; record in long takes,
   cut with `tools/rerecord/cuttake.py`). GLOSS: widen `balcao` to "counter".
