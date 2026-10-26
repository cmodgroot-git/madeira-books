# Book 16 build (golfe, «Com os Pés no Chão»)

Scripts used to make book 16 and the echo (tense-shift) feature. Working files (raw generations,
audio, SAM cache) live in a scratch folder set by `WORK`; the full-size masters are in
`books/16-golfe/art/`.

| Script | What it does |
|---|---|
| `prompts.py`, `prompts2.py` | Krea prompts for the pages (`prompts2` = pages 3–8 drawn from real photos of Santo da Serra) |
| `insets.py` | draws the phone message and the faded "earlier" insets with speech bubbles (Caveat, Alegreya Sans in `fonts/`) |
| `hl_book16.py`, `hlmask.py` | tap-region specs and the Segment Anything cutter (`cut <page>`, `sheet`) |
| `act16.json` | action cues |
| `life16.py` | animation sheets: pond ripples (p5), bay shimmer (p6), flag (p7) |
| `align.py`, `narr.py`, `cutwords.py` | speech alignment, page narration timings, word / title / echo-line clips |
| `echo16.py`, `echo.js`, `echo.css` | echo data and the reader code for it |
| `build16.py text media` | writes everything into `docs/` (idempotent; run on the committed `docs/index.html`) |

Needs: torch (CPU), segment-anything + `sam_vit_h_4b8939.pth`, transformers, soundfile, opencv, ffmpeg.
