# Histórias da Madeira — rigged stand-in characters (armature + IK) for Blender previz.
# A person faces -Y at rest, feet on the floor at the armature origin.
# Controls (bone collection "Controls"): root (move/turn the whole person), hips (body), foot_ik.L/R, hand_ik.L/R,
# knee_pole.L/R, elbow_pole.L/R. Spine, neck, head are rotated directly (FK). Arms and legs follow the IK targets.
# Each limb has an "ik" influence on its IK constraint (set to 0 to pose that limb by rotating bones instead).
# Every mesh keeps the 'group' tag used by the mask render.
import bpy, math
from mathutils import Vector, Matrix

def mat(name, rgb, rough=0.8):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1.0)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    if b:
        b.inputs["Base Color"].default_value = (*rgb, 1.0); b.inputs["Roughness"].default_value = rough
    return m

def _link(o, coll):
    for c in o.users_collection: c.objects.unlink(o)
    coll.objects.link(o)

def _join(objs, name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join(); objs[0].name = name
    return objs[0]

def _capsule(name, p, q, r, m):
    p, q = Vector(p), Vector(q); d = q - p
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=r, depth=d.length, location=(p + q) / 2)
    c = bpy.context.active_object; c.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=r * 1.05, location=p); s1 = bpy.context.active_object
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=r * 1.05, location=q); s2 = bpy.context.active_object
    o = _join([c, s1, s2], name); o.data.materials.clear(); o.data.materials.append(m)
    return o

def _widget(kind, coll):
    name = f'WGT_{kind}'
    if name in bpy.data.objects: return bpy.data.objects[name]
    if kind == 'circle':
        bpy.ops.mesh.primitive_circle_add(vertices=24, radius=1.0)
    elif kind == 'square':
        bpy.ops.mesh.primitive_plane_add(size=2.0)
        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.delete(type='ONLY_FACE'); bpy.ops.object.mode_set(mode='OBJECT')
    else:  # diamond
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1.0)
        bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.delete(type='ONLY_FACE'); bpy.ops.object.mode_set(mode='OBJECT')
    w = bpy.context.active_object; w.name = name; w['group'] = 'set'; w.hide_render = True
    _link(w, coll); return w

def person_rig(name, h=1.8, shirt=(0.08, 0.12, 0.30), legs=(0.08, 0.10, 0.25), skin=(0.78, 0.55, 0.40),
               socks=None, shoes=(0.05, 0.05, 0.05), hair=(0.06, 0.04, 0.03), hair_style='short',
               long_legs=False, long_sleeves=False, gloves=None, group='body', head_group=None):
    k = h / 1.8
    socks = socks or legs
    M = {n: mat(f'{name}_{n}', c) for n, c in dict(shirt=shirt, legs=legs, skin=skin, socks=socks, shoes=shoes, hair=hair).items()}
    if gloves: M['gloves'] = mat(f'{name}_gloves', gloves)
    sc = bpy.context.scene
    coll = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if coll.name not in sc.collection.children: sc.collection.children.link(coll)
    wcoll = bpy.data.collections.get('WGT')
    if not wcoll:
        wcoll = bpy.data.collections.new('WGT'); sc.collection.children.link(wcoll)
    V = lambda x, y, z: Vector((x * k, y * k, z * k))
    J = {  # rest joint positions (person facing -Y)
        'pelvis': V(0, 0, 0.95), 'chest': V(0, 0, 1.50), 'neck': V(0, 0, 1.53), 'headtop': V(0, 0, 1.80),
    }
    for s, sx in (('L', 1), ('R', -1)):
        J[f'sh{s}'] = V(0.20 * sx, 0, 1.47); J[f'el{s}'] = V(0.21 * sx, 0.04, 1.18); J[f'wr{s}'] = V(0.22 * sx, 0, 0.92); J[f'ht{s}'] = V(0.22 * sx, 0, 0.84)
        J[f'hp{s}'] = V(0.095 * sx, 0, 0.89); J[f'kn{s}'] = V(0.095 * sx, -0.04, 0.47); J[f'an{s}'] = V(0.095 * sx, 0, 0.06); J[f'to{s}'] = V(0.095 * sx, -0.16, 0.02)
    # --- armature
    ad = bpy.data.armatures.new(f'{name}_rig'); arm = bpy.data.objects.new(f'{name}_rig', ad)
    coll.objects.link(arm); ad.display_type = 'OCTAHEDRAL'; arm.show_in_front = True
    bpy.context.view_layer.objects.active = arm
    for o in bpy.context.selected_objects: o.select_set(False)
    arm.select_set(True); bpy.ops.object.mode_set(mode='EDIT')
    E = ad.edit_bones
    def bone(n, head, tail, parent=None, roll=0.0, deform=True, connect=False):
        b = E.new(n); b.head = head; b.tail = tail; b.roll = roll; b.use_deform = deform
        if parent: b.parent = E[parent]; b.use_connect = connect
        return b
    bone('root', V(0, 0, 0), V(0, 0.35, 0), deform=False)
    bone('hips', J['pelvis'], J['pelvis'] + V(0, 0, -0.12), 'root')
    bone('spine', J['pelvis'], J['chest'], 'hips')
    bone('neck', J['chest'], J['neck'] + V(0, 0, 0.05), 'spine')
    bone('head', J['neck'] + V(0, 0, 0.05), J['headtop'], 'neck', connect=True)
    for s in ('L', 'R'):
        bone(f'upperarm.{s}', J[f'sh{s}'], J[f'el{s}'], 'spine')
        bone(f'forearm.{s}', J[f'el{s}'], J[f'wr{s}'], f'upperarm.{s}', connect=True)
        bone(f'hand.{s}', J[f'wr{s}'], J[f'ht{s}'], f'forearm.{s}', connect=True)
        bone(f'thigh.{s}', J[f'hp{s}'], J[f'kn{s}'], 'hips')
        bone(f'shin.{s}', J[f'kn{s}'], J[f'an{s}'], f'thigh.{s}', connect=True)
        bone(f'foot.{s}', J[f'an{s}'], J[f'to{s}'], f'shin.{s}', connect=True)
        # controls: IK targets have exactly the same head/tail/roll as the foot/hand they drive
        f = bone(f'foot_ik.{s}', J[f'an{s}'], J[f'to{s}'], 'root', deform=False); f.roll = E[f'foot.{s}'].roll
        hnd = bone(f'hand_ik.{s}', J[f'wr{s}'], J[f'ht{s}'], 'root', deform=False); hnd.roll = E[f'hand.{s}'].roll
        bone(f'knee_pole.{s}', J[f'kn{s}'] + V(0, -0.6, 0), J[f'kn{s}'] + V(0, -0.7, 0), 'root', deform=False)
        bone(f'elbow_pole.{s}', J[f'el{s}'] + V(0, 0.6, 0), J[f'el{s}'] + V(0, 0.7, 0), 'root', deform=False)
    bpy.ops.object.mode_set(mode='POSE')
    P = arm.pose.bones
    ctrl = ad.collections.new('Controls'); defm = ad.collections.new('Body')
    for b in ad.bones:
        (ctrl if b.name.startswith(('root', 'hips', 'foot_ik', 'hand_ik', 'knee_pole', 'elbow_pole', 'spine', 'neck', 'head')) else defm).assign(b)
    defm.is_visible = False
    W = {'circle': _widget('circle', wcoll), 'square': _widget('square', wcoll), 'diamond': _widget('diamond', wcoll)}
    shapes = {'root': ('circle', 3.0), 'hips': ('circle', 2.5), 'spine': ('circle', 0.6), 'neck': ('circle', 0.8), 'head': ('circle', 0.6)}
    for s in ('L', 'R'):
        shapes[f'foot_ik.{s}'] = ('square', 0.5); shapes[f'hand_ik.{s}'] = ('square', 0.9)
        shapes[f'knee_pole.{s}'] = ('diamond', 0.5); shapes[f'elbow_pole.{s}'] = ('diamond', 0.5)
    for n, (w, sz) in shapes.items():
        P[n].custom_shape = W[w]; P[n].custom_shape_scale_xyz = (sz, sz, sz)
    # constraints
    for s in ('L', 'R'):
        for chain, tgt, pole in ((f'shin.{s}', f'foot_ik.{s}', f'knee_pole.{s}'), (f'forearm.{s}', f'hand_ik.{s}', f'elbow_pole.{s}')):
            c = P[chain].constraints.new('IK'); c.name = 'ik'; c.target = arm; c.subtarget = tgt
            c.pole_target = arm; c.pole_subtarget = pole; c.chain_count = 2
        for b, t in ((f'foot.{s}', f'foot_ik.{s}'), (f'hand.{s}', f'hand_ik.{s}')):
            c = P[b].constraints.new('COPY_ROTATION'); c.name = 'follow_ik'; c.target = arm; c.subtarget = t
    # pick the pole angle that leaves the rest pose unchanged
    bpy.ops.object.mode_set(mode='OBJECT'); ad.pose_position = 'POSE'
    for chain in [f'shin.{s}' for s in 'LR'] + [f'forearm.{s}' for s in 'LR']:
        c = P[chain].constraints['ik']; best = None
        for ang in (-180, -90, 0, 90, 180):
            c.pole_angle = math.radians(ang); bpy.context.view_layer.update()
            par = P[chain].parent
            err = (par.tail - ad.bones[par.name].tail_local).length + (P[chain].tail - ad.bones[chain].tail_local).length
            if best is None or err < best[0]: best = (err, ang)
        c.pole_angle = math.radians(best[1])
    # --- meshes, parented to bones (rest positions)
    ad.pose_position = 'REST'; bpy.context.view_layer.update()
    def parent_bone(o, b, grp):
        bpy.context.view_layer.update(); mw = o.matrix_world.copy(); o.parent = arm; o.parent_type = 'BONE'; o.parent_bone = b
        bpy.context.view_layer.update(); o.matrix_world = mw; o['group'] = grp; _link(o, coll)
    hg = head_group or group
    bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.15 * k, depth=0.55 * k, location=J['pelvis'] + V(0, 0, 0.275))
    t = bpy.context.active_object; t.name = f'{name}_torso'; t.scale = (1.15, 0.7, 1); t.data.materials.append(M['shirt']); parent_bone(t, 'spine', group)
    bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.16 * k, depth=0.2 * k, location=J['pelvis'] + V(0, 0, -0.05))
    p = bpy.context.active_object; p.name = f'{name}_pelvis'; p.scale = (1.05, 0.72, 1); p.data.materials.append(M['legs']); parent_bone(p, 'hips', group)
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.045 * k, depth=0.1 * k, location=J['neck'] + V(0, 0, 0.02))
    nk = bpy.context.active_object; nk.name = f'{name}_neckmesh'; nk.data.materials.append(M['skin']); parent_bone(nk, 'neck', hg)
    hc = J['neck'] + V(0, 0, 0.13)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=14, radius=0.11 * k, location=hc)
    hd = bpy.context.active_object; hd.name = f'{name}_head'; hd.scale = (0.9, 0.95, 1.1); hd.data.materials.append(M['skin']); parent_bone(hd, 'head', hg)
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.025 * k, depth=0.05 * k, location=hc + V(0, -0.105, 0), rotation=(math.radians(90), 0, 0))
    ns = bpy.context.active_object; ns.name = f'{name}_nose'; ns.data.materials.append(M['skin']); parent_bone(ns, 'head', hg)   # shows which way the face points
    hs = []
    if hair_style == 'curly':
        for dx, dy, dz in [(0, 0.0, 0.08), (0.07, 0.0, 0.05), (-0.07, 0.0, 0.05), (0, 0.06, 0.04), (0.06, 0.05, 0.0), (-0.06, 0.05, 0.0)]:
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.06 * k, location=hc + V(dx, dy, dz)); hs.append(bpy.context.active_object)
    elif hair_style == 'long':
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=0.118 * k, location=hc + V(0, 0.015, 0.02)); hs.append(bpy.context.active_object)
        bpy.ops.mesh.primitive_cube_add(location=hc + V(0, 0.06, -0.10)); b = bpy.context.active_object; b.scale = (0.11 * k, 0.05 * k, 0.17 * k); hs.append(b)
    else:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=0.113 * k, location=hc + V(0, 0.015, 0.03)); hs.append(bpy.context.active_object)
    hr = _join(hs, f'{name}_hair'); hr.data.materials.clear(); hr.data.materials.append(M['hair']); parent_bone(hr, 'head', hg)
    for s in ('L', 'R'):
        parent_bone(_capsule(f'{name}_uarm{s}', J[f'sh{s}'], J[f'el{s}'], 0.05 * k, M['shirt']), f'upperarm.{s}', group)
        parent_bone(_capsule(f'{name}_farm{s}', J[f'el{s}'], J[f'wr{s}'], 0.04 * k, M['shirt'] if long_sleeves else M['skin']), f'forearm.{s}', group)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8, radius=0.05 * k, location=(J[f'wr{s}'] + J[f'ht{s}']) / 2)
        hn = bpy.context.active_object; hn.name = f'{name}_hand{s}'; hn.data.materials.append(M['gloves'] if gloves else M['skin']); parent_bone(hn, f'hand.{s}', group)
        parent_bone(_capsule(f'{name}_thigh{s}', J[f'hp{s}'], J[f'kn{s}'], 0.07 * k, M['legs']), f'thigh.{s}', group)
        parent_bone(_capsule(f'{name}_shin{s}', J[f'kn{s}'], J[f'an{s}'], 0.055 * k, M['legs'] if long_legs else M['socks']), f'shin.{s}', group)
        bpy.ops.mesh.primitive_cube_add(location=(J[f'an{s}'] + J[f'to{s}']) / 2 + V(0, 0, -0.01))
        ft = bpy.context.active_object; ft.name = f'{name}_foot{s}'; ft.scale = (0.05 * k, 0.12 * k, 0.04 * k)
        ft.data.materials.append(M['shoes']); parent_bone(ft, f'foot.{s}', group)
    ad.pose_position = 'POSE'
    wcoll.hide_viewport = True; wcoll.hide_render = True
    return arm
