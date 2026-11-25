# Book 22 page 4 as a storyboard: only the key poses sent to Flow, still camera, poses set on the rig controls.
# Starts just before Tiago jumps. Keys (frame @24fps -> narration):
#   K1   0  "a bola vem alta e o Tiago salta"  Tiago crouched to jump, ball coming in high, keeper set
#   K2  36  header: Tiago in the air, ball at his head, keeper diving
#   K3  96  "Marca golo de cabeça!"  ball in the net, keeper down, Tiago landed with arms going up, Rita jumps up
#   K4 165  "Corre ... com os braços no ar"  Tiago running across, arms up; Rita walking out onto the pitch, clapping
#   K5 230  "manda um beijo à Rita"  Tiago in front of Rita, hand held out after the kiss; she blushes, hands at her chest
import bpy, sys, os, math
sys.path.insert(0, '/home/claude/work/bl')
from mathutils import Vector, Matrix, Euler
import bg_madeira

SRC = os.environ.get('SRC', '/home/claude/work/bl/b22p4_rig.blend'); DST = os.environ.get('DST', '/home/claude/work/bl/b22p4_story.blend')
KEYS = [0, 36, 96, 165, 230]

bpy.ops.wm.open_mainfile(filepath=SRC)
sc = bpy.context.scene; sc.frame_start = 0; sc.frame_end = 283
bg_madeira.build()
for _m in bpy.data.objects['pitch'].data.materials: _m.diffuse_color = (0.36, 0.55, 0.24, 1)

# ---- clear every pose and keyframe
for o in bpy.data.objects:
    o.animation_data_clear()
    if o.type == 'ARMATURE':
        for pb in o.pose.bones:
            pb.rotation_mode = 'QUATERNION'; pb.matrix_basis = Matrix.Identity(4)

# ---- still camera: sees the goal, Tiago's run and the stand
cam = bpy.data.objects['camera']; cam.data.lens = 24.0
cam.location = (-1.4, -6.4, 1.75)
cam.rotation_euler = (Vector((-1.9, 0.0, 1.3)) - cam.location).to_track_quat('-Z', 'Y').to_euler()

def RX(a, b, c): return Euler((math.radians(a), math.radians(b), math.radians(c))).to_matrix().to_4x4()
def T(v): return Matrix.Translation(Vector(v))

def pose(name, f, root, hips=(0, 0, 0, 0, 0, 0), spine=(0, 0, 0), neck=(0, 0, 0), feet=None, hands=None, knees=None, elbows=None):
    """All positions/rotations in the person's own frame: x = their left, y = behind them, z = up, from the root on the floor.
    root=(x, y, turn_deg[, z]); turn 0 faces -Y (the camera side), +90 faces +X (towards the goal side), -90 faces -X."""
    arm = bpy.data.objects[name + '_rig']; P = arm.pose.bones; B = arm.data.bones
    upd = bpy.context.view_layer.update
    rx, ry, rt = root[0], root[1], root[2]; rz = root[3] if len(root) > 3 else 0.0
    M = T((rx, ry, rz)) @ RX(0, 0, rt)
    P['root'].matrix = M @ B['root'].matrix_local; upd()
    hh = B['hips'].head_local
    H = T(hh + Vector(hips[:3])) @ RX(*hips[3:]) @ T(-hh)
    P['hips'].matrix = M @ H @ B['hips'].matrix_local; upd()
    sh = B['spine'].head_local; S = T(sh) @ RX(*spine) @ T(-sh)
    P['spine'].matrix = M @ H @ S @ B['spine'].matrix_local; upd()
    nh = B['neck'].head_local; N = T(nh) @ RX(*neck) @ T(-nh)
    P['neck'].matrix = M @ H @ S @ N @ B['neck'].matrix_local; upd()
    P['head'].matrix_basis = Matrix.Identity(4)
    for s in 'LR':
        for ctl, spec in ((f'foot_ik.{s}', (feet or {}).get(s)), (f'hand_ik.{s}', (hands or {}).get(s))):
            h0 = B[ctl].head_local
            pos = Vector(spec[:3]) if spec else h0.copy(); rot = RX(*spec[3:6]) if spec and len(spec) > 3 else Matrix.Identity(4)
            P[ctl].matrix = M @ T(pos) @ rot @ T(-h0) @ B[ctl].matrix_local
        for ctl, spec in ((f'knee_pole.{s}', (knees or {}).get(s)), (f'elbow_pole.{s}', (elbows or {}).get(s))):
            h0 = B[ctl].head_local; pos = Vector(spec) if spec else h0.copy()
            P[ctl].matrix = M @ T(pos - h0) @ B[ctl].matrix_local
    upd()
    for n in ['root', 'hips', 'spine', 'neck'] + [f'{c}.{s}' for c in ('foot_ik', 'hand_ik', 'knee_pole', 'elbow_pole') for s in 'LR']:
        P[n].keyframe_insert('location', frame=f); P[n].keyframe_insert('rotation_quaternion', frame=f)

def ball(f, loc):
    b = bpy.data.objects['ball']; b.location = loc; b.keyframe_insert('location', frame=f)

def head_front(name, fwd=0.17, up=0.02):
    arm = bpy.data.objects[name + '_rig']; bpy.context.view_layer.update()
    hb = arm.pose.bones['head']; c = arm.matrix_world @ ((hb.head + hb.tail) / 2)
    face = (arm.matrix_world.to_3x3() @ hb.matrix.to_3x3()) @ Vector((0, 0, -1))   # bone local -Z = the face side for an upright bone
    face.z = 0; face = face.normalized() if face.length > 1e-3 else Vector((0, -1, 0))
    return c + face * fwd + Vector((0, 0, up))

def face_to(src, dst):   # turn angle so a person at src faces dst
    d = Vector(dst) - Vector(src); return math.degrees(math.atan2(d.x, -d.y))

# ---------- Tiago
TIAGO_K5 = (-3.05, -1.85); RITA_K5 = (-3.95, -2.05)
t = 'tiago'
pose(t, 0, (-1.25, -2.05, 112), hips=(0, 0.02, -0.26, 22, 0, 0), spine=(12, 0, 0), neck=(-28, 0, 0),
     feet={'L': (0.13, -0.18, 0.06), 'R': (-0.12, 0.2, 0.06, 0, 0, 0)},
     hands={'L': (0.30, 0.32, 0.66), 'R': (-0.30, 0.34, 0.66)}, knees={'L': (0.13, -0.8, 0.45), 'R': (-0.12, -0.6, 0.45)})
pose(t, 36, (-0.9, -1.55, 112, 0.5), hips=(0, 0, 0, 28, 0, 0), spine=(10, 0, 0), neck=(18, 0, 0),
     feet={'L': (0.12, 0.30, 0.42, 40, 0, 0), 'R': (-0.12, 0.22, 0.20, 25, 0, 0)},
     hands={'L': (0.58, -0.05, 1.22), 'R': (-0.58, -0.05, 1.22)}, elbows={'L': (0.7, 0.4, 1.3), 'R': (-0.7, 0.4, 1.3)})
pose(t, 96, (-0.75, -1.55, 25), hips=(0, 0, -0.04, 0, 0, 0), neck=(-12, 0, 0),
     feet={'L': (0.16, -0.02, 0.06), 'R': (-0.16, 0.02, 0.06)},
     hands={'L': (0.42, 0.02, 2.02), 'R': (-0.42, 0.02, 2.02)}, elbows={'L': (0.75, 0.45, 1.65), 'R': (-0.75, 0.45, 1.65)})
pose(t, 165, (-2.0, -2.15, face_to((-2.0, -2.15), TIAGO_K5), 0.05), hips=(0, 0, -0.06, 10, 0, 0), neck=(-8, 0, 0),
     feet={'L': (0.10, -0.42, 0.20, -15, 0, 0), 'R': (-0.10, 0.42, 0.28, 35, 0, 0)},
     knees={'L': (0.1, -0.9, 0.7), 'R': (-0.1, -0.5, 0.35)},
     hands={'L': (0.40, 0.06, 1.98), 'R': (-0.40, 0.06, 1.98)}, elbows={'L': (0.75, 0.45, 1.65), 'R': (-0.75, 0.45, 1.65)})
pose(t, 230, (TIAGO_K5[0], TIAGO_K5[1], face_to(TIAGO_K5, RITA_K5)), spine=(6, 0, 0), neck=(6, 0, 0),
     feet={'L': (0.13, 0.05, 0.06), 'R': (-0.11, -0.08, 0.06)},
     hands={'R': (-0.12, -0.58, 1.45, -80, 0, 0), 'L': (0.24, 0.02, 0.90)}, elbows={'R': (-0.6, 0.3, 1.25)})

# ---------- keeper (faces the pitch: turn 0)
g = 'keeper'
pose(g, 0, (0.05, 0.35, 0), hips=(0, 0.04, -0.16, 14, 0, 0), spine=(8, 0, 0), neck=(-10, 0, 0),
     feet={'L': (0.27, 0.0, 0.06), 'R': (-0.27, 0.0, 0.06)}, knees={'L': (0.4, -0.7, 0.45), 'R': (-0.4, -0.7, 0.45)},
     hands={'L': (0.46, -0.28, 0.98), 'R': (-0.46, -0.28, 0.98)})
pose(g, 36, (0.75, 0.42, 0, 0.42), hips=(0, 0, 0, 0, 70, 0), spine=(0, 8, 0),
     feet={'L': (-0.74, 0.0, 0.60), 'R': (-0.86, 0.05, 0.78)},
     hands={'L': (1.32, -0.06, 1.22), 'R': (1.18, -0.08, 1.60)}, elbows={'L': (0.6, 0.6, 0.6), 'R': (0.7, 0.6, 1.8)},
     knees={'L': (-0.5, -0.7, 0.4), 'R': (-0.5, -0.7, 0.9)})
pose(g, 96, (0.55, 0.55, 0), hips=(0, 0, -0.80, 0, 88, 0),
     feet={'L': (-0.84, 0.0, 0.10), 'R': (-0.84, 0.08, 0.28)}, knees={'L': (-0.5, -0.7, 0.1), 'R': (-0.5, -0.7, 0.4)},
     hands={'L': (1.30, -0.06, 0.10), 'R': (1.22, -0.12, 0.30)}, elbows={'L': (0.6, 0.6, -0.2), 'R': (0.6, 0.6, 0.7)})
sit = dict(hips=(0, 0.05, -0.78, -18, 0, 0), spine=(6, 0, 0), feet={'L': (0.17, -0.78, 0.08), 'R': (-0.15, -0.72, 0.08)},
           knees={'L': (0.2, -0.7, 0.9), 'R': (-0.2, -0.7, 0.9)}, hands={'L': (0.30, 0.32, 0.06), 'R': (-0.30, 0.32, 0.06)})
pose(g, 165, (0.75, 0.75, 8), neck=(0, 0, 0), **{k: v for k, v in sit.items()})
pose(g, 230, (0.75, 0.75, 8), neck=(5, 0, 20), **{k: v for k, v in sit.items()})

# ---------- the women: front row of the stand, facing the pitch (+X)
SEAT_X = -9.75
def seated(name, f, y, k, hands, neck=(0, 0, 0)):
    pose(name, f, (SEAT_X, y, 90), hips=(0, 0.20, 0.74 - 0.95 * k, 0, 0, 0), neck=neck,
         feet={'L': (0.10 * k, -0.22, 0.06 * k), 'R': (-0.10 * k, -0.22, 0.06 * k)}, hands=hands)
kr, ka, kg = 1.64 / 1.8, 1.66 / 1.8, 1.52 / 1.8
lap = lambda k: {'L': (0.11, -0.12, 0.76), 'R': (-0.11, -0.12, 0.76)}
clasp_seated = {'L': (0.03, -0.27, 1.08), 'R': (-0.03, -0.27, 1.08)}
clap_open = lambda k: {'L': (0.15, -0.30, 1.20 * k + 0.0), 'R': (-0.15, -0.30, 1.20 * k)}
clap_shut = lambda k: {'L': (0.03, -0.30, 1.20 * k), 'R': (-0.03, -0.30, 1.20 * k)}
# Rita
seated('rita', 0, -1.38, kr, clasp_seated, neck=(-5, 0, 0))
seated('rita', 36, -1.38, kr, clasp_seated, neck=(-8, 0, 0))
pose('rita', 96, (-9.25, -1.40, 90, 0.0), hips=(0, 0, 0.03, 0, 0, 0), neck=(-6, 0, 0), hands=clap_open(kr))
pose('rita', 165, (-4.55, -1.95, face_to((-4.55, -1.95), TIAGO_K5)), neck=(-4, 0, 0),
     feet={'L': (0.09 * kr, -0.30, 0.06 * kr), 'R': (-0.09 * kr, 0.30, 0.12 * kr, 25, 0, 0)}, hands=clap_shut(kr))
pose('rita', 230, (RITA_K5[0], RITA_K5[1], face_to(RITA_K5, TIAGO_K5)), neck=(16, 0, -6), spine=(4, 0, 0),
     hands={'L': (0.035, -0.24, 1.17 * kr), 'R': (-0.035, -0.24, 1.17 * kr)})
# Ana: watches, then claps from her seat
seated('ana', 0, -2.0, ka, lap(ka)); seated('ana', 36, -2.0, ka, lap(ka))
seated('ana', 96, -2.0, ka, {'L': (0.15, -0.30, 1.10), 'R': (-0.15, -0.30, 1.10)})
seated('ana', 165, -2.0, ka, {'L': (0.03, -0.30, 1.10), 'R': (-0.03, -0.30, 1.10)})
seated('ana', 230, -2.0, ka, {'L': (0.15, -0.30, 1.10), 'R': (-0.15, -0.30, 1.10)}, neck=(0, 0, 15))
# Dona Graça: stays seated, hands in her lap, looks on
for f in KEYS:
    seated('graca', f, -0.76, kg, lap(kg), neck=(0, 0, 10 if f >= 165 else 0))

# ---------- ball (only at the keys)
ball(0, (-2.9, -2.6, 2.75))
bpy.context.scene.frame_set(36); ball(36, tuple(head_front('tiago')))
ball(96, (1.15, 1.30, 0.12)); ball(165, (1.25, 1.18, 0.11)); ball(230, (1.25, 1.18, 0.11))

sc.frame_set(0)
bpy.ops.wm.save_as_mainfile(filepath=DST)
print('saved', DST)
