# "Ver" (watch mode) prototype — book 22 page 4

Published as its own private artifact, slug 7b9a0ceb-feeb-4f07-a2bc-f7d28de20666 (not in the library yet).

- **Media:** clip.mp4 is the 4 s Flow clip (crf 24, no audio). narr.mp3 is the page narration. w_*.mp3 are the word clips cut from docs/audio/words.mp3 with WCLIP.
- **Mattes:** m_<key>.webp holds one sheet per word. Each frame is a 480x270 cell, 8 columns by 12 rows, for 96 frames. R holds the matte (with a 1.2 px blur baked in) and G the halo (blur 7 minus matte, x1.6), as in tools/video/look.py. They are built from the rotoscope's roto_final.pkl; the build snippet is in the session notes in SKILL.md.
- **Drawing:** WebGL draws video plus matte with the approved look. Frame = floor(currentTime*24).
- **Timing:** the video starts at the narration word "salta" (2.785 s), then holds its last frame.
- **Read-along:** things light up as their word is spoken.
- **Taps:** tapping a word plays its clip and replays the video with that thing lit throughout.
