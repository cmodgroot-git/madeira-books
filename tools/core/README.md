# Build toolkit (books 1–15)

Everything used to write, paint, cut, animate, voice and publish books 1–15, so a new session can make the next book the same way. Books 16 and 17 have their own per-book folders in `tools/b16` and `tools/b17`.

Set up a workspace first — the scripts use absolute paths, and `setup.sh` rewrites them to wherever you put the workspace:

```
bash tools/core/setup.sh ~/madeira-work
```

## What is here

| Path | What it is |
|------|------------|
| `artifact/index.html` | **Build source** of the reader: the full page with all page regions (`PHOTOS`) inline and `PACK=null`. `docs/index.html` is the light published copy made from it by `split.py`. |
| `artifact/audio/bNpM.mp3`, `artifact/img/t/bNpM.webp` | Per-page narration and page thumbnails, which `split.py` packs into one file per book. |
| `gen/masters/bNpM.jpg` | 1600×898 page masters: what the region cutter and animation scripts read. |
| `gen/act.json` | Action cues (move, arrow, hold, rest, spin, sound) for every action word; `conv/actfx.py` writes them into the page. |
| `buildN.py` | Adds book N: pictures → masters, page images and thumbnails; `pagesN`, story entry, cover and meanings (`GLOSS`, six languages). |
| `conv/hl_bookN.py`, `hlmask.py`, `hlspecs.py` | Tap-region specs per book and the Segment Anything cutter (`hlmask.py sheet <id> [pages]` to review, `apply <id>` to write). |
| `bNlife.py`, `frames.py`, `windfx.py`, `repack.py`, `regutter.py` | Gentle animation layers per page (ripple, sway, steam, twinkle…). |
| `audio/narr.py`, `audio/cutwords.py`, `audio/titlealign.py`, `audio/*.json` | Narration alignment, word clips (`WCLIP` into `words.mp3`) and title clips (`TCLIP`/`TWORDS` into `titles.mp3`). |
| `split.py`, `dist/state.json` | Makes the publish copy in `dist/` (per-book photo bundles, covers, narration and thumbnail strips). |
| `tNN.js`, `aNN.js`, `pNN.js` | Playwright checks: tap every word, audit text/narration/meanings/sounds, packed build on desktop and phone. |
| `books/bNN/` | Each book's chosen pictures (`final.txt`), Krea image IDs (`refs.txt`) and prompts. |

The writing, picture, highlight and animation rules are in the skills under `skills/`.

## Making the next book (short version)

1. Write and approve the 8 pages (`bNNpages.json`), then generate pictures with Krea 3 using the style and character references in `books/*/refs.txt`.
2. `python3 buildNN.py` (copy the last one), `conv/hl_bookNN.py` + register in `hlspecs.py` and the `BOOK` map in `hlmask.py`, then `hlmask.py sheet` / `apply`.
3. Add cues to `gen/act.json` → `python3 conv/actfx.py`; animation `bNNlife.py` → `repack.py` → `regutter.py`.
4. Narration `audio/narr.py texts` / `build NN:1 …`; word clips `audio/cutwords.py`; title clip.
5. Check with the Playwright scripts, then `python3 split.py` and copy `dist/` over `docs/`.
