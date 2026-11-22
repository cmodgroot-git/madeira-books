---
name: "madeira-video-highlights"
description: "Rotoscope tappable things through a Histórias da Madeira page video (or cut them on a still) and render the approved highlight look: AI cut-outs per frame, ball and goal tracking, soft dim-and-glow highlight."
---

# Histórias da Madeira — highlights that move with the picture

Use this when a page becomes a short video (Google Flow / Veo, Krea video) and its tappable words must light up on the moving picture, or when a still page needs cut-outs fast and `hlmask.py`'s SAM vit_h is too slow. For still-page tap regions in the reader itself, `madeira-book-highlights` is still the main skill; this one adds the video pipeline and the approved look.

Worked example (everything here was built and approved on it): book 22 `jogo` page 4 (`jogo:3`, words bola, cabeça, golo, Rita), the user's 4 s Flow clip `books/22-jogo/video/b22p4_flow_4s.mp4`, scripts in `tools/video/b22p4/`.

## The look (current default: the first one)
`tools/video/look.py` holds the numbers. Use the default unless the user asks:
- **"first" (default since Nov 22, 2026):**
  - the rest of the picture at 45% brightness, in full colour;
  - the thing itself unchanged;
  - a 3 px warm-yellow outline (RGB 255,230,80) just outside its edge.
  - The prototype draws it in WebGL, finding the outline from the matte in the shader.
- **"soft" (kept as an alternative):**
  - the rest 38% darker and 27.5% toward grey;
  - the thing slightly punchier;
  - a soft warm-white halo instead of a line.

**History:**
1. First demo: the yellow line.
2. The user asked for "more subtle" and then "more contrast".
3. Then "half as much pop" and "increase the dimming only", which produced the soft look.
4. Then: "go back to your original highlight settings".

If asked to change the look, change one number at a time and show a short MP4 or the prototype.

## Setup (each session)
1. `sh tools/video/setup.sh`: clones MobileSAM (code and 40 MB weights) from GitHub into `/home/claude/work/MobileSAM`. The user approved using it.
2. MobileSAM imports `timm` and `torchvision`, which do not match the installed torch. `tools/video/shim/` holds tiny stand-ins. Put it first on `sys.path`, as `sam_roto.py` does. Do not pip-install timm or torchvision.
3. Speed on the 2-CPU machine: MobileSAM is about 1.8 s per 1280×720 frame, and one embedding serves every object in that frame. SAM vit_h took over 400 s per frame here, so don't use it for video.

## Pipeline for a clip (order matters)
1. **Frames:** `ffmpeg -i clip.mp4 fr/%03d.png` (Flow gives 1280×720, 24 fps). The first frame is the page, so the page's own cut-outs (`hlcache` pickle: list of `(key, bool mask)` at 898×1600) are the seeds. ECC-align the master to frame 0 (`track.py`).
2. **Rough tracks:** run `track.py`. It uses a different method for each kind of thing:
   - **People and faces:** DIS optical flow plus a RANSAC similarity transform.
   - **The goal:** ORB/SIFT homography of the camera, with the people excluded.
   - **The ball:** a template tracker, which loses fast balls.
   - **Rita:** a hand polygon on the master, because her page cut-out was wrong.
   Output: `tracks2.pkl`.
3. **Per-object rotoscope.** Pick the method by the kind of thing:
   - **Face or person that deforms (Tiago's head):** `roto.py` (flow-carried prior, then GrabCut at 2×, then guided-filter alpha), then `sam_roto.py`. The second step re-cuts every frame with MobileSAM, prompted by the box plus 6 interior points of the current cut. It keeps the multimask output with the best IoU and takes soft alpha from the logits. When IoU is below 0.72, it keeps the old cut. That happened for 6 frames where the ball touches the head.
   - **Person standing still while the camera moves (Rita):** don't let the shape follow its own flow, because it shrinks or swells over 4 s. Carry the first-frame cut by the camera motion measured from SIFT features in a window around her (RANSAC ignores the keeper diving past). Re-cut only above the shoulders, so the clapping arms move. Then use MobileSAM. `sam_post.py` trims everything below the shoe soles and removes non-shoe, non-denim pixels in her bottom 14%, so the keeper's head never joins her outline.
   - **Ball:** `ballc.py` finds the real circle each frame with Hough near the guess. `ballfix2.py` keeps the finds that sit on the ball and applies hand corrections where they missed (measure each on a contact sheet). `ballmatte.py` draws an exact 4× supersampled disc and subtracts skin (the keeper's knee in front). Template tracking (CCORR) locks onto bright sky in the net, so don't use it.
   - **Rigid structure (the goal):** don't highlight an area, because people in front get lit. `golo.py` tracks the camera with a homography, then finds the posts and crossbar by the painted ink lines on either side of each post. It takes the median perpendicular brightness profile and the nearest dark dips around the brightest line, and subtracts arms or gloves crossing the posts. The net strings come from a 5×5 top-hat (thin bright lines) inside the goal polygon, dropping long flat streaks (fence rails). Brightness alone can't separate the posts from the sky.
4. **Temporal smoothing:** average each matte with its flow-aligned neighbours (weights 1-2-1), as `sam_post.py` and `roto.py` do. This removes edge flicker.
5. **Check before showing:** `sheet.py <keys>` makes a close-up contact sheet (6 frames per object) with a 1 px outline. Look at it, fix, and repeat. The user only sees the MP4.
6. **Render:** `render.py` (soft look) writes one pass per word with the look and the fade; for the default look call `look.look_first` instead, then encode with `libx264 -preset veryfast -crf 18 -pix_fmt yuv420p`.

## For a still page
Use the same cut steps without the tracking. Seed with the page's `hlcache` cut or a hand box, then run MobileSAM (box plus interior points), guided-filter alpha, and `look.py` for a preview. Check the cut on a 2× close-up sheet before replacing reader regions (`madeira-book-highlights` covers the reader side).

## Video sources and costs
- **Google Flow:** the user has credits. Veo 3.1 Lite costs 10 credits, Fast 20, Quality 100. Extend works only on 8 s Veo 3.1 clips. Fast and Quality retire from Flow on Dec 5, 2026. Make an 8 s Frames-to-Video clip and extend it to cover the narration (page 4's narration is 13.27 s, `b22p4_narracao.mp3`).
- **Krea video:** see the cost notes in `madeira-book-stories`.
- **Rotoscoping cost:** no credits. Plan on about 15 minutes of compute per 4 s clip, plus about 5 minutes of hand corrections for a small fast object like a ball.

## Still to build
A "watch" mode in the reader: the video plays with the page narration, words light up as they are read, and tapping a word shows its moving highlight. Store the per-frame mattes compactly (for example a small grey sprite or video per word) and sync them to `video.currentTime`. The user reviews a one-page prototype before any book gets it.
