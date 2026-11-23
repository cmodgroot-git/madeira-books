# Book 22, page 4 (jogo:3): "Aos dez minutos, a bola vem alta e o Tiago salta. Marca golo de cabeça! ..."
# 12 s at 24 fps = 284 frames (matches the Flow clip). Frame numbers below are 0-based like the clip.
import bpy, math, sys
SEATS = None; EXTRA = None
sys.path.insert(0, '/home/claude/work/bl')
from mathutils import Vector
import set_pitch as S, chars as C

def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene; sc.render.fps = 24; sc.frame_start = 0; sc.frame_end = 283
    S.build_pitch(); S.build_camera(); S.build_light()
    # staging fix (Nov 23): no stand or plinth behind the goal; the stand runs alongside the pitch
    for n in ('stand', 'plinth'):
        o = bpy.data.objects.get(n)
        if o: bpy.data.objects.remove(o, do_unlink=True)
    global SEATS; SEATS = S.side_stand(x0=-3.7, y_from=-5.5, y_to=2.5)
    cam = bpy.data.objects['camera']; cam.data.lens = 22.0; cam.location = (2.4, -6.0, 1.5)
    d = Vector((-1.4, 0, 1.2)) - cam.location; cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    for o in list(bpy.context.scene.objects):
        if o.type == 'MESH' and 'group' not in o: o['group'] = 'golo' if o.name in ('goal', 'goal_back', 'net') else 'set'
    T = C.person('tiago', 1.8, shirt=(0.07, 0.10, 0.28), legs=(0.07, 0.09, 0.24), socks=(0.07, 0.09, 0.24),
                 skin=(0.62, 0.42, 0.30), hair=(0.05, 0.035, 0.03), hair_style='curly', group='tiago', head_group='cabeca')
    G = C.person('keeper', 1.82, shirt=(0.92, 0.75, 0.10), legs=(0.06, 0.06, 0.06), socks=(0.06, 0.06, 0.06),
                 skin=(0.70, 0.50, 0.36), hair=(0.06, 0.04, 0.03), hair_style='short', gloves=(0.9, 0.9, 0.88), group='keeper')
    R = C.person('rita', 1.64, shirt=(0.30, 0.45, 0.72), legs=(0.32, 0.42, 0.62), socks=(0.32, 0.42, 0.62), shoes=(0.92, 0.92, 0.9),
                 skin=(0.85, 0.66, 0.52), hair=(0.20, 0.12, 0.07), hair_style='long', long_legs=True, long_sleeves=True, group='rita')
    A = C.person('ana', 1.66, shirt=(0.10, 0.50, 0.50), legs=(0.32, 0.42, 0.62), socks=(0.32, 0.42, 0.62), shoes=(0.3, 0.2, 0.15),
                 skin=(0.85, 0.66, 0.52), hair=(0.35, 0.22, 0.12), hair_style='long', long_legs=True, long_sleeves=True, group='ana')
    D = C.person('graca', 1.52, shirt=(0.25, 0.22, 0.22), legs=(0.22, 0.20, 0.20), socks=(0.22, 0.20, 0.20), shoes=(0.1, 0.1, 0.1),
                 skin=(0.80, 0.62, 0.50), hair=(0.85, 0.85, 0.85), hair_style='short', long_legs=True, long_sleeves=True, group='graca')
    global EXTRA; EXTRA = (A, D)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.11, location=(0, 0, 0))
    ball = bpy.context.active_object; ball.name = 'ball'; ball['group'] = 'bola'
    ball.data.materials.append(S.mat('ball', (0.95, 0.95, 0.95), 0.4))
    animate(T, G, R, ball)
    return T, G, R, ball

def key_ball(ball, f, x, y, z, spin=0):
    ball.location = (x, y, z); ball.keyframe_insert('location', frame=f)
    ball.rotation_euler = (spin, spin * 0.6, 0); ball.keyframe_insert('rotation_euler', frame=f)

def ray(u, v):
    # world ray through pixel (u, v) of the 1280x720 render
    cam = bpy.data.objects['camera']; cd = cam.data; f = cd.lens / cd.sensor_width * 1280
    d = Vector(((u - 640) / f, -(v - 360) / f, -1.0)); d = cam.matrix_world.to_3x3() @ d
    return cam.matrix_world.translation.copy(), d.normalized()
def on_ground(u, v, z=0.0):
    o, d = ray(u, v); t = (z - o.z) / d.z; return o + d * t
def on_plane_y(u, v, y):
    o, d = ray(u, v); t = (y - o.y) / d.y; return o + d * t
def place_head(J, frame, u, v, y, pose_fn):
    # move the root so this frame's head lands on pixel (u, v) at depth plane y
    sc = bpy.context.scene; target = on_plane_y(u, v, y)
    for _ in range(3):
        sc.frame_set(frame); bpy.context.view_layer.update()
        hd = bpy.data.objects[J['root'].name.replace('_root', '_head')].matrix_world.translation
        loc = J['root'].location + (target - hd); pose_fn(loc)
    return loc

def place_head_world(J, frame, target, pose_fn):
    sc = bpy.context.scene
    for _ in range(3):
        sc.frame_set(frame); bpy.context.view_layer.update()
        hd = bpy.data.objects[J['root'].name.replace('_root', '_head')].matrix_world.translation
        loc = J['root'].location + (target - hd); pose_fn(loc)
    return loc

def animate(T, G, R, ball):
    P = C.pose
    # --- Tiago: airborne header facing the goal (+X), lands, watches, celebrates with arms up, then waves
    face_goal = (0, 0, 90)
    P(T, 0, {'spine': (-38, 0, 0), 'neck': (25, 0, 0), 'shL': (-20, -65, 0), 'shR': (-20, 65, 0), 'elL': (-40, 0, 0), 'elR': (-40, 0, 0),
             'hipL': (-15, 0, 0), 'knL': (45, 0, 0), 'hipR': (35, 0, 0), 'knR': (80, 0, 0)},
      root=dict(loc=(-0.95, -2.5, 1.45), rot=face_goal))
    P_h0 = {'spine': (-38, 0, 0), 'neck': (25, 0, 0), 'shL': (-20, -65, 0), 'shR': (-20, 65, 0), 'elL': (-40, 0, 0), 'elR': (-40, 0, 0),
            'hipL': (-15, 0, 0), 'knL': (45, 0, 0), 'hipR': (35, 0, 0), 'knR': (80, 0, 0)}
    h0 = place_head_world(T, 0, Vector((-0.75, -1.9, 2.25)), lambda L: P(T, 0, P_h0, root=dict(loc=tuple(L), rot=face_goal)))
    P(T, 8, {'spine': (-30, 0, 0), 'neck': (-15, 0, 0), 'shL': (-10, -55, 0), 'shR': (-10, 55, 0), 'elL': (-30, 0, 0), 'elR': (-30, 0, 0),
             'hipL': (-25, 0, 0), 'knL': (40, 0, 0), 'hipR': (20, 0, 0), 'knR': (60, 0, 0)},
      root=dict(loc=(h0.x + 0.2, h0.y, h0.z - 0.12), rot=face_goal))
    P(T, 20, {'spine': (-25, 0, 0), 'shL': (-30, -25, 0), 'shR': (-30, 25, 0), 'elL': (-40, 0, 0), 'elR': (-40, 0, 0),
              'hipL': (-70, 0, 0), 'knL': (100, 0, 0), 'hipR': (-60, 0, 0), 'knR': (95, 0, 0)},
      root=dict(loc=(h0.x + 0.35, h0.y - 0.05, 0.68), rot=face_goal))
    # crouches, watching the ball go in (turns towards the camera a bit)
    crouch = {'spine': (-20, 0, 0), 'neck': (5, 0, 0), 'shL': (-35, -10, 0), 'shR': (-35, 10, 0), 'elL': (-60, 0, 0), 'elR': (-60, 0, 0),
              'hipL': (-75, -8, 0), 'knL': (105, 0, 0), 'hipR': (-75, 8, 0), 'knR': (105, 0, 0)}
    g1 = Vector((-0.45, -2.2, 0)); g2 = g1
    P(T, 40, crouch, root=dict(loc=(g1.x, g1.y, 0.66), rot=(0, 0, 55)))
    P(T, 90, crouch, root=dict(loc=(g1.x, g1.y, 0.66), rot=(0, 0, 35)))
    # runs to the stand with both arms up, stops in front of Rita, blows her a kiss
    rita_seat = SEATS[0][min(range(len(SEATS[0])), key=lambda i: abs(SEATS[0][i][1] - (-1.4)))]
    stop = Vector((rita_seat[0] + 1.7, rita_seat[1] + 1.1, 0.95))
    start = Vector((g1.x, g1.y, 0.95))
    up = {'shL': (-155, 38, 0), 'shR': (-155, -38, 0), 'elL': (-15, 0, 0), 'elR': (-15, 0, 0), 'neck': (12, 0, 0)}
    run_dir = math.degrees(math.atan2(-(stop - start).x, (stop - start).y))   # rotation about Z so -Y (front) points along the run
    P(T, 100, dict(up, hipL=(0, 0, 0), hipR=(0, 0, 0)), root=dict(loc=tuple(start), rot=(0, 0, run_dir + 180)))
    n = 8
    for i in range(1, n + 1):
        f = 100 + i * 10; q = start.lerp(stop, i / n); stride = 35 if i % 2 else -35
        P(T, f, dict(up, hipL=(-stride, 0, 0), hipR=(stride, 0, 0), knL=(40 if stride > 0 else 10, 0, 0), knR=(10 if stride > 0 else 40, 0, 0)),
          root=dict(loc=(q.x, q.y, 0.95 + (0.04 if i % 2 else 0)), rot=(0, 0, run_dir + 180)))
    face_rita = (0, 0, 125)   # -Y front turned to face -X (the stand)
    P(T, 190, up, root=dict(loc=tuple(stop), rot=face_rita))
    P(T, 214, {'shR': (-95, 10, 0), 'elR': (-130, 0, 0), 'neck': (5, 0, 0)}, root=dict(loc=tuple(stop), rot=face_rita))      # hand to lips
    P(T, 230, {'shR': (-80, 25, 0), 'elR': (-10, 0, 0), 'neck': (5, 0, 0)}, root=dict(loc=tuple(stop), rot=face_rita))       # sends it
    P(T, 283, {'shR': (-60, 25, 0), 'elR': (-10, 0, 0), 'neck': (5, 0, 0)}, root=dict(loc=tuple(stop), rot=face_rita))
    # --- Keeper: diving to his left (towards +X) with arms up, fingertips the ball, lands, then sits up inside the goal
    dive = {'shL': (-160, -25, 0), 'shR': (-160, 25, 0), 'elL': (-10, 0, 0), 'elR': (-10, 0, 0), 'hipL': (-20, -10, 0), 'knL': (40, 0, 0),
            'hipR': (10, 15, 0), 'knR': (30, 0, 0)}
    P(G, 0, dive, root=dict(loc=(0.55, 0.45, 1.05), rot=(0, -35, 0)))
    P(G, 26, dive, root=dict(loc=(1.05, 0.5, 1.25), rot=(0, -70, 0)))
    P(G, 44, dive, root=dict(loc=(1.25, 0.55, 0.32), rot=(0, -88, 0)))
    P(G, 70, {'shL': (-60, -20, 0), 'shR': (-40, 30, 0)}, root=dict(loc=(1.2, 0.55, 0.25), rot=(0, -90, 0)))
    sit = {'spine': (-15, 0, 0), 'neck': (20, 0, 0), 'hipL': (-85, -12, 0), 'knL': (40, 0, 0), 'hipR': (-85, 12, 0), 'knR': (60, 0, 0),
           'shL': (-15, -25, 0), 'shR': (-15, 25, 0), 'elL': (-20, 0, 0), 'elR': (-20, 0, 0)}
    P(G, 110, sit, root=dict(loc=(1.05, 0.6, 0.32), rot=(0, 0, 10)))
    P(G, 283, dict(sit, neck=(25, 0, 15)), root=dict(loc=(1.05, 0.6, 0.32), rot=(0, 0, 10)))
    # --- Rita sits in the front row of the side stand between Ana and Dona Graça, facing the pitch (+X).
    #     She jumps up when the ball goes in and claps; Ana claps sitting; Dona Graça stays seated.
    A, D = EXTRA
    row = SEATS[0]; mid = min(range(len(row)), key=lambda i: abs(row[i][1] - (-1.4)))
    face_pitch = (0, 0, -90)
    sit = {'hipL': (-90, 0, 0), 'knL': (90, 0, 0), 'hipR': (-90, 0, 0), 'knR': (90, 0, 0), 'shL': (-35, 0, 0), 'shR': (-35, 0, 0),
           'elL': (-50, 0, 0), 'elR': (-50, 0, 0)}
    def seated(J, seat, k, frame, extra=None, lift=0.0):
        p = dict(sit); p.update(extra or {})
        P(J, frame, p, root=dict(loc=(seat[0] + 0.05, seat[1], seat[2] + 0.1 * k + lift), rot=face_pitch))
    kr, ka, kd = 1.64 / 1.8, 1.66 / 1.8, 1.52 / 1.8
    for f in (0, 40): seated(R, row[mid], kr, f, {'shL': (-40, 12, 0), 'shR': (-40, -12, 0), 'elL': (-95, 0, 0), 'elR': (-95, 0, 0)})
    stand_loc = (row[mid][0] + 0.45, row[mid][1], row[mid][2] - 0.65 + 0.95 * kr)
    for i, f in enumerate(range(48, 284, 6)):
        o = i % 2 == 0
        P(R, f, {'shL': (-40, -5 if o else 12, 0), 'shR': (-40, 5 if o else -12, 0), 'elL': (-95, 0, 0), 'elR': (-95, 0, 0), 'neck': (-5, 0, 0)},
          root=dict(loc=(stand_loc[0], stand_loc[1], stand_loc[2] + (0.03 if (o and f < 120) else 0)), rot=face_pitch))
    seated(A, row[mid - 1], ka, 0)
    for i, f in enumerate(range(52, 284, 7)):
        o = i % 2 == 0
        seated(A, row[mid - 1], ka, f, {'shL': (-45, -5 if o else 12, 0), 'shR': (-45, 5 if o else -12, 0), 'elL': (-90, 0, 0), 'elR': (-90, 0, 0)})
    seated(D, row[mid + 1], kd, 0, {'shL': (-20, 0, 0), 'shR': (-20, 0, 0), 'elL': (-70, 0, 0), 'elR': (-70, 0, 0)})
    seated(D, row[mid + 1], kd, 283, {'shL': (-20, 0, 0), 'shR': (-20, 0, 0), 'elL': (-70, 0, 0), 'elR': (-70, 0, 0), 'neck': (0, 0, 15)})
    # --- Ball: off Tiago's head, past the keeper's fingertips, into the net, drops, bounces, rolls to rest inside the goal
    bpy.context.scene.frame_set(0); bpy.context.view_layer.update()
    hd = bpy.data.objects['tiago_head'].matrix_world.translation
    key_ball(ball, 0, hd.x + 0.16, hd.y, hd.z + 0.12)
    key_ball(ball, 14, 0.25, -1.2, 2.45, 3)
    key_ball(ball, 28, 1.15, 0.15, 2.2, 6)
    key_ball(ball, 38, 1.35, 1.15, 1.7, 8)      # hits the back of the net
    key_ball(ball, 48, 1.3, 1.0, 0.11, 10)
    key_ball(ball, 56, 1.25, 0.85, 0.42, 11)
    key_ball(ball, 64, 1.2, 0.75, 0.11, 12)
    key_ball(ball, 110, 1.45, 0.3, 0.11, 16)
    key_ball(ball, 283, 1.45, 0.3, 0.11, 16)

if __name__ == '__main__':
    build()
    bpy.ops.wm.save_as_mainfile(filepath='/home/claude/work/bl/b22p4.blend')
