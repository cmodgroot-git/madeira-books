#!/usr/bin/env bash
# Recreate the book-building workspace from this repo.
# usage: bash tools/core/setup.sh [WORKDIR]      (default: ~/madeira-work)
# Afterwards every script in WORKDIR runs as it did when books 1–15 were built.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
WORK="${1:-$HOME/madeira-work}"
OLD='/tmp/claude-0/-home-claude/c592c827-54c1-535b-90c3-a38173d9efc0/scratchpad'
AID='87e1712e-5e90-4175-b828-2581544915d4'
mkdir -p "$WORK"
cp -r "$REPO/tools/core/." "$WORK/"
# source of the reader (unpacked: PHOTOS inline, PACK=null) + the published media it needs
SRC="$WORK/artifact-files/$AID"
mkdir -p "$SRC"
cp -r "$WORK/artifact/." "$SRC/" && rm -rf "$WORK/artifact"
mkdir -p "$SRC/img" "$SRC/audio"
cp -rn "$REPO/docs/img/." "$SRC/img/"
cp "$REPO/docs/audio/words.mp3" "$REPO/docs/audio/titles.mp3" "$SRC/audio/"
mkdir -p "$WORK/audio/tmpcat" && mv "$WORK/audio/sil.mp3" "$WORK/audio/sil4.mp3" "$WORK/audio/tmpcat/"
# point every script at the new workspace
grep -rl "$OLD" "$WORK" --include='*.py' --include='*.js' --include='*.json' | xargs -r sed -i "s#$OLD#$WORK#g"
echo "Workspace ready in $WORK"
echo "Still needed (not stored in git):"
echo "  - Segment Anything: git clone https://github.com/facebookresearch/segment-anything $WORK/sam/repo"
echo "    and the ViT-H checkpoint as $WORK/sam/vit_h.pth (sam_vit_h_4b8939.pth from the SAM README)"
echo "  - pip install --break-system-packages torch transformers opencv-python pillow numpy"
echo "    (word alignment downloads jonatasgrosman/wav2vec2-large-xlsr-53-portuguese on first use)"
echo "  - ffmpeg, node + playwright (for the test scripts)"
