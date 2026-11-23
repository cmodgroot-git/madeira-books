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
