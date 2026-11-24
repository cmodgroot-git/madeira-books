# Replace the empty-based mannequins in a previz .blend with rigged characters (rig.py), carrying over the poses
# at every keyed frame: whole-body placement -> root bone; spine/neck -> FK; hands/feet -> IK targets; elbows/knees -> poles.
import bpy, sys, os
sys.path.insert(0, '/home/claude/work/bl')
from mathutils import Vector, Matrix
import rig

SRC = os.environ.get('SRC'); DST = os.environ.get('DST')
SPEC = {
    'tiago': dict(h=1.8, shirt=(0.07, 0.10, 0.28), legs=(0.07, 0.09, 0.24), socks=(0.07, 0.09, 0.24), skin=(0.62, 0.42, 0.30),
                  hair=(0.05, 0.035, 0.03), hair_style='curly', group='tiago', head_group='cabeca'),
    'keeper': dict(h=1.82, shirt=(0.92, 0.75, 0.10), legs=(0.06, 0.06, 0.06), socks=(0.06, 0.06, 0.06), skin=(0.70, 0.50, 0.36),
                   hair=(0.06, 0.04, 0.03), hair_style='short', gloves=(0.9, 0.9, 0.88), group='keeper'),
    'rita': dict(h=1.64, shirt=(0.30, 0.45, 0.72), legs=(0.32, 0.42, 0.62), shoes=(0.92, 0.92, 0.9), skin=(0.85, 0.66, 0.52),
                 hair=(0.20, 0.12, 0.07), hair_style='long', long_legs=True, long_sleeves=True, group='rita'),
    'ana': dict(h=1.66, shirt=(0.10, 0.50, 0.50), legs=(0.32, 0.42, 0.62), shoes=(0.3, 0.2, 0.15), skin=(0.85, 0.66, 0.52),
                hair=(0.35, 0.22, 0.12), hair_style='long', long_legs=True, long_sleeves=True, group='ana'),
    'graca': dict(h=1.52, shirt=(0.25, 0.22, 0.22), legs=(0.22, 0.20, 0.20), shoes=(0.1, 0.1, 0.1), skin=(0.80, 0.62, 0.50),
                  hair=(0.85, 0.85, 0.85), hair_style='short', long_legs=True, long_sleeves=True, group='graca'),
}

def fcurves(obj):
    ad = obj.animation_data
    if not ad or not ad.action: return []
    a = ad.action
    try: return list(a.fcurves)
    except AttributeError:
        out = []
        for l in a.layers:
            for st in l.strips:
                for cb in st.channelbags: out += list(cb.fcurves)
        return out

bpy.ops.wm.open_mainfile(filepath=SRC)
sc = bpy.context.scene
samples = {}
for n, sp in SPEC.items():
    objs = [o for o in bpy.data.objects if o.name.startswith(n + '_')]
    if not objs: continue
    frames = {sc.frame_start, sc.frame_end}
    for o in objs:
        for fc in fcurves(o): frames |= {int(round(kp.co[0])) for kp in fc.keyframe_points}
    frames = sorted(f for f in frames if sc.frame_start <= f <= sc.frame_end)
    k = sp['h'] / 1.8; S = {}
    for f in frames:
        sc.frame_set(f); bpy.context.view_layer.update()
        g = lambda j: bpy.data.objects[f'{n}_{j}'].matrix_world.copy()
        d = {'root': g('root'), 'spine': g('spine'), 'neck': g('neck')}
        for s in 'LR':
            el, kn = g(f'el{s}'), g(f'kn{s}')
            d[f'sh{s}'] = g(f'sh{s}').translation; d[f'el{s}'] = el; d[f'kn{s}'] = kn; d[f'hp{s}'] = g(f'hip{s}').translation
            d[f'wr{s}'] = el @ Vector((0, 0, -0.26 * k)); d[f'an{s}'] = kn @ Vector((0, 0, -0.42 * k))
        S[f] = d
    samples[n] = (frames, k, S)
    for o in objs: bpy.data.objects.remove(o, do_unlink=True)
print({n: v[0] for n, v in samples.items()})

def key(pb, f):
    pb.keyframe_insert('location', frame=f); pb.keyframe_insert('rotation_quaternion', frame=f)

for n, (frames, k, S) in samples.items():
    arm = rig.person_rig(n, **SPEC[n]); P = arm.pose.bones; B = arm.data.bones
    for pb in P: pb.rotation_mode = 'QUATERNION'
    bpy.context.view_layer.objects.active = arm
    for f in frames:
        sc.frame_set(f); d = S[f]
        # whole-person placement: old root sits at the pelvis, the rig's root at the floor
        T = d['root'] @ Matrix.Translation((0, 0, -0.95 * k))
        P['root'].matrix = T @ B['root'].matrix_local
        bpy.context.view_layer.update()
        for bn, old in (('spine', 'spine'), ('neck', 'neck')):
            rot = (d[old].to_3x3() @ B[bn].matrix_local.to_3x3())
            P[bn].matrix = Matrix.Translation(P[bn].head) @ rot.to_4x4()
            bpy.context.view_layer.update()
        for s in 'LR':
            for tgt, oldrot, loc in ((f'foot_ik.{s}', d[f'kn{s}'], d[f'an{s}']), (f'hand_ik.{s}', d[f'el{s}'], d[f'wr{s}'])):
                rot = oldrot.to_3x3() @ B[tgt].matrix_local.to_3x3()
                P[tgt].matrix = Matrix.Translation(loc) @ rot.to_4x4()
            for pole, a, mid, b in ((f'knee_pole.{s}', d[f'hp{s}'], d[f'kn{s}'].translation, d[f'an{s}']),
                                    (f'elbow_pole.{s}', d[f'sh{s}'], d[f'el{s}'].translation, d[f'wr{s}'])):
                line = (a + b) / 2; out = mid - line
                if out.length < 1e-4: out = (d['root'].to_3x3() @ Vector((0, -1 if 'knee' in pole else 1, 0)))
                P[pole].matrix = Matrix.Translation(mid + out.normalized() * 0.6) @ B[pole].matrix_local.to_3x3().to_4x4()
        bpy.context.view_layer.update()
        for bn in ['root', 'spine', 'neck'] + [f'{c}.{s}' for c in ('foot_ik', 'hand_ik', 'knee_pole', 'elbow_pole') for s in 'LR']:
            key(P[bn], f)
bpy.ops.object.select_all(action='DESELECT')
sc.frame_set(0)
bpy.ops.wm.save_as_mainfile(filepath=DST)
print('saved', DST)
