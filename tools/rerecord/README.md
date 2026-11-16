# Books 1–17 re-recorded in Marta + Pedro (Nov 15, 2026)

All narration, word sounds and titles of books 1–17 were re-recorded in the native European Portuguese
ElevenLabs voices (Krea `elevenlabs/tts`, `eleven_v4`, plain text): Marta `bBNhdwrIjl4fcVYiRbT2` narrates and reads
the women's lines, the word sounds and the titles; Pedro `XxTHUwWTW2conYBz0vvk` reads the men's lines (`speakers.py`)
and book 16's echo lines (all Tiago's). Book 18 was already recorded this way.

## How (about 60 recordings instead of ~350)
1. `segments.py` cuts every page at its dashes; men's lines go to Pedro → `data/segs.json` (304 segments).
2. `takes.py` packs segments into long takes, one paragraph per segment (≤ 1700 chars; 14 Marta takes, 1 Pedro take,
   1 title take) and the 507 word sounds into batches of 15 → `data/takes.json`.
3. Each take recorded once (`data/urls.tsv`); `cuttake.py`/`cutall.py` align the take, cut each segment at its pauses,
   transcribe each piece and flag low matches. Page segments matched 95–98%.
4. Short one-syllable words (*chá, dá, pé, vê, nó*), plus *café, cartaz, sinal* and two of Pedro's lines, were
   recorded singly and trimmed to the first saying (`data/singles.tsv`).
5. `assemble.py pages clips write`: pages joined with 0.3 s between segments and aligned (NARR); one new
   `words.mp3` (538 clips, book 18's carried over) and `titles.mp3` (18 titles) with WCLIP/TCLIP/TWORDS; a new
   narration pack per book, old packs removed from the artifact.

A Krea API key could not be used for scripting: API keys bill a separate prepaid API balance, not the plan's units.
