#!/usr/bin/env python3
"""Regenerate books/NN-id/story.md from the reader (docs/index.html).

The reader is the source of truth. Story text lives there as arrays
`pagesN` whose entries mark vocabulary as [shown word|word id].
This script writes a plain, readable copy of each book's text plus the
list of highlighted words per page, so the stories can be read and
diffed on GitHub without opening the reader.

Usage:  python3 tools/extract_stories.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "docs" / "index.html"
OUT = ROOT / "books"

BOOK_RE = re.compile(r"id:'([a-z]+)',title:'([^']+)',[^}]*?pages:pages(\d+)")
WORD_RE = re.compile(r"\[([^\]|]+)\|([^\]]+)\]")


def read_pages(src: str, n: str) -> list[str]:
    start = src.index(f"const pages{n}=[") + len(f"const pages{n}=")
    depth, i = 0, start
    while True:
        c = src[i]
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                break
        elif c == '"':  # skip string bodies
            i += 1
            while src[i] != '"':
                i += 2 if src[i] == "\\" else 1
        i += 1
    return json.loads(src[start : i + 1])


def main() -> None:
    src = HTML.read_text(encoding="utf-8")
    books = BOOK_RE.findall(src)
    for old in OUT.glob("[0-9][0-9]-*/story.md"):  # keep other files (art, notes) in book folders
        old.unlink()
    for num, (book_id, title, n) in enumerate(books, 1):
        pages = read_pages(src, n)
        folder = OUT / f"{num:02d}-{book_id}"
        folder.mkdir(parents=True, exist_ok=True)
        lines = [f"# {title}", "", f"Book {num} · id `{book_id}` · {len(pages)} pages", ""]
        for p, raw in enumerate(pages, 1):
            text = WORD_RE.sub(r"\1", raw)
            words = sorted({w for _, w in WORD_RE.findall(raw)})
            lines += [f"## Page {p}", "", text, ""]
            if words:
                lines += ["Highlighted: " + ", ".join(f"`{w}`" for w in words), ""]
        (folder / "story.md").write_text("\n".join(lines), encoding="utf-8")
        print(f"{folder.relative_to(ROOT)}  {title}  ({len(pages)} pages)")


if __name__ == "__main__":
    main()
