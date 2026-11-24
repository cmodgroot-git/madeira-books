# Blender previz (pilot: book 22 page 4)

Plan grey Blender scenes before spending credits on stills or video: fixed sets, stand-in cast, camera, blocking, and exact per-object masks.

- **Setup:** `pip install --break-system-packages bpy` (Blender 5.3 as a Python module; renders headless with Workbench, about 1 s per frame at 1280x720).
- **`set_pitch.py`:** the seaside pitch of book 22: small goal (3.6 x 2.4 m) with net, stand with blue seats, Rita's plinth, sea, cliff, hillside houses; camera and sun.
  - The camera was fitted to the page by matching the goal corners: (2.0, -5.0, 1.4), looking at (-0.5, 0, 1.4), 26 mm lens.
- **`chars.py`:** jointed mannequins in the cast's colours.
  - `person()` returns its joints; `pose(J, frame, {joint: (rx, ry, rz)}, root=...)` sets keyframes.
  - Each mesh carries a `group` tag (cabeca, tiago, keeper, rita, bola, golo, set) used for the masks.
- **`shot_b22p4.py`:** builds and animates the 12 s shot (284 frames, 24 fps) to match the Flow clip, and saves `b22p4.blend`.
  - `place_head()` and `on_ground()` put a character where the painting has them, by casting rays through the painting's pixel positions.
- **`render_all.py`:** renders the grey frames, plus flat-colour ID frames with no anti-aliasing for exact masks:
  - red = bola
  - green = cabeca
  - blue = golo
  - yellow = rita
  - magenta = keeper
  - cyan = tiago
- **`render_prev.py`:** renders chosen frames for a quick check.

## Staging fix (Nov 23, 2026)
The user asked why Rita stood on a plinth behind the goal. The text has her **in the stand with Ana and Dona Graça** (p3), and Tiago **runs to the stand** and blows her a kiss (p4).
- The p4 prompt had put her "behind the goal, on the low stand", and the image model turned that into a block.
- The user chose a **stand alongside the pitch**.
- The previz now:
  - removes the plinth and the stand behind the goal;
  - adds `side_stand()` along the left touchline near the goal end;
  - seats Rita between Ana and Dona Graça in the front row;
  - has Rita stand up and clap after the goal (Ana claps from her seat, Dona Graça stays seated);
  - has Tiago run to the stand, arms up, and blow the kiss;
  - pulls the camera back with a 22 mm lens so the goal and the stand fit together.
- Book pictures p4 and p7 still show the old staging and need repainting to match.

## The user's edits (Nov 23, 2026): the .blend is now the master
The user edited the scene in Blender 5.3 and sent it back. It is saved as `tools/previz/b22p4.blend`.
- **His changes:**
  - turned Rita, Ana and Dona Graça to face the pitch (the script had them facing -X, backs to the game);
  - rerouted Tiago's run right up to the stand and simplified his turns;
  - moved the ball's start closer to Tiago's head.
- **From now on, don't re-run `shot_b22p4.py`:** it would overwrite his edits. Make script changes by opening `b22p4.blend` and editing it.
- **To render:** `BLEND=tools/previz/b22p4.blend python3 render_all.py`.
- **To see what changed:** `dump.py <file.blend> <out.json>` dumps every object's transforms and keyframes; compare two dumps.
- **Rotation convention reminder:** a person faces -Y at rest. rot Z = +90° faces +X; rot Z = -90° faces -X.
