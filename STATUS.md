# Where we are (Nov 22, 2026)

Library (artifact 87e1712e-5e90-4175-b828-2581544915d4, version 1794902890-24cc): books 1–22 and retellings
1b–10b, 20b, 21b, 22b on the «Outra Vez» shelf. 328 of 511 published files (page pictures packed per book).
Krea: ~340 units left this month (plan resets monthly).

## Next, in order
1. Retellings 11b–19b: not started (user said "not yet"). Plan agreed in principle: draft all nine texts (free),
   then record ~120 units each. Narrator ideas: 11b Tiago (the podium, "my mechanic"), 12b the old lady who sold
   Rita the blue car, 16b Inês on the golf course, 19b Rita's mother.
2. Book 23 (practical-life book) after the Krea reset: rung 16 = future subjunctive (quando vierem, se puderes,
   quem quiser). Open threads: Rita and Tiago moving in together? Dona Graça's Sunday visits; João's mother.
3. Video pages ("Ver" / watch mode), paused by the user ("save for now"):
   - Prototype for book 22 p4: separate private artifact 7b9a0ceb-feeb-4f07-a2bc-f7d28de20666, source tools/video/watch/.
   - Done: per-frame AI cut-outs (MobileSAM), approved look (tools/video/look.py), skill skills/madeira-video-highlights.
   - Waiting on the user: test the prototype on a phone; make an 8 s Flow clip (Frames to Video, Veo 3.1 Lite or Fast)
     and extend it to cover the 13.3 s narration. Veo 3.1 Fast/Quality leave Flow on Dec 5, 2026.
   - Then: rotoscope the longer clip, decide whether a whole book gets video, and add "Ver" to the reader.
4. Pending features: reader practice (story questions, listen-first, repeat after Marta); character voices test.

## How (see skills/madeira-book-stories/SKILL.md)
- New book: tools/b22 is the newest working set; after the build run tools/pack/pack_pages.py before publishing.
- Old-book retelling: tools/retell/old.py (config tools/b<N>b/retell.json); commit after each build.
- After any text: python3 tools/fgloss/build.py, add missing forms to tools/fgloss/fg*.tsv.
