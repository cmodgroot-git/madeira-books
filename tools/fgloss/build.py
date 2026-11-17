#!/usr/bin/env python3
"""Meanings for every untagged word form, so any word in a story can be tapped (review, Nov 2026).
fg*.tsv: form<TAB>en<TAB>de<TAB>fr<TAB>es<TAB>nl<TAB>pl (written by hand, general senses of the form).
A form that is also a tappable word's shown text takes that word's GLOSS. Writes docs/fgloss.json and
lists forms in the published books (plus any --extra pages files) that still need a line."""
import glob, json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools")); import extract_stories as X
src = (ROOT / "docs/index.html").read_text(encoding="utf-8")
G = json.JSONDecoder().raw_decode(src, src.index("const GLOSS=") + 12)[0]
WRX = re.compile(r"[^\W\d_]+(?:[-'’][^\W\d_]+)*")
NAMES = {'rita','ana','joão','tiago','rui','bruno','marta','sofia','duarte','inês','funchal','madeira','lisboa','porto','fanal','seixal','garajau','machico','zona','velha'}
pages = [p for _, _, n in X.BOOK_RE.findall(src) for p in X.read_pages(src, n)]
for f in sys.argv[1:]: pages += json.loads(Path(f).read_text(encoding="utf-8"))
shown = {}
for p in pages:
    for sh, k in X.WORD_RE.findall(p): shown.setdefault(sh.lower(), k)
forms = sorted({w.lower() for p in pages for w in WRX.findall(X.WORD_RE.sub(lambda m: ' ' * len(m.group(0)), p))} - NAMES)
FG = {}
for f in sorted(glob.glob(str(ROOT / "tools/fgloss/fg*.tsv"))):
    for line in Path(f).read_text(encoding="utf-8").splitlines():
        if not line.strip(): continue
        c = line.split("\t"); assert len(c) == 7, (f, line)
        FG[c[0]] = c[1:]
out, missing = {}, []
for w in forms:
    if w in FG: out[w] = FG[w]
    elif w in shown and shown[w] in G: out[w] = G[shown[w]]
    else: missing.append(w)
(ROOT / "docs/fgloss.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
print(f"fgloss: {len(out)} forms with meanings, {len(missing)} missing" + (": " + " ".join(missing) if missing else ""))
