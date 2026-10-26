# Histórias da Madeira

A library of illustrated Portuguese picture books for adults learning the language by comprehension, not translation. Each story is everyday life on Madeira, the pictures carry the meaning, and every book reuses earlier vocabulary while adding new words. Tap a highlighted word in the reader to see what it points to and hear it spoken.

## Books

| # | Title | Folder |
|---|-------|--------|
| 1 | A Manhã da Rita | [books/01-manha](books/01-manha/story.md) |
| 2 | O Sábado da Rita | [books/02-sabado](books/02-sabado/story.md) |
| 3 | O Domingo da Rita | [books/03-domingo](books/03-domingo/story.md) |
| 4 | O Jantar da Rita | [books/04-jantar](books/04-jantar/story.md) |
| 5 | O Passeio da Rita | [books/05-passeio](books/05-passeio/story.md) |
| 6 | A Madrugada da Rita | [books/06-pico](books/06-pico/story.md) |
| 7 | A Ana Volta ao Norte | [books/07-seixal](books/07-seixal/story.md) |
| 8 | A Rita Procura Casa | [books/08-casa](books/08-casa/story.md) |
| 9 | O Mergulho no Garajau | [books/09-garajau](books/09-garajau/story.md) |
| 10 | A Casa Nova | [books/10-novacasa](books/10-novacasa/story.md) |
| 11 | O Dia das Corridas | [books/11-corridas](books/11-corridas/story.md) |
| 12 | O Carro da Rita | [books/12-carro](books/12-carro/story.md) |
| 13 | O Veleiro | [books/13-veleiro](books/13-veleiro/story.md) |
| 14 | O Voo da Rita | [books/14-voo](books/14-voo/story.md) |
| 15 | A Festa da Casa Nova | [books/15-festa](books/15-festa/story.md) |

## Layout

```
docs/            The reader: a static site, ready for GitHub Pages
  index.html     The app — library, page reader, story text, word data
  img/           Page paintings (bNpM.jpg), highlight cut-out sheets (*_sheet.webp),
                 action-cue frames (act/), covers (c/) and thumbnails (t/)
  audio/         Narration per book (book/), word pronunciations, titles
  photos/        Real reference photos shown for word meanings, one bundle per book
books/           Plain-text copy of each story with its highlighted words
tools/           Helper scripts
```

`docs/index.html` is the source of truth. The `books/*/story.md` files are generated from it — after changing the reader, refresh them with:

```
python3 tools/extract_stories.py
```

## Reading locally

Open `docs/index.html` through any static server, for example:

```
cd docs && python3 -m http.server 8000
```

then visit http://localhost:8000. Reading progress (known words, last page) is kept in the browser.

## Publishing

To put the reader online, turn on GitHub Pages for this repo (Settings → Pages → Deploy from a branch → `main`, folder `/docs`).
