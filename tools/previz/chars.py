# Histórias da Madeira — previz stand-ins: simple jointed mannequins with the cast's colours.
# A person faces -Y (towards the camera) at rest. Joint rotations are Euler degrees in the joint's parent space:
#   rx < 0 swings a limb forward (towards where the person faces), rx > 0 backward;
#   ry swings sideways (left arm/leg out: ry < 0; right arm/leg out: ry > 0); rz twists.
# Masks: every object gets a 'group' custom property (e.g. 'cabeca', 'rita', 'keeper') used by the mask render.
import bpy, math
from mathutils import Vector
from set_pitch import mat

def _empty(name, parent=None, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None); e.empty_display_size = 0.05
    bpy.context.scene.collection.objects.link(e)
    if parent: e.parent = parent
    e.location = loc; e.rotation_mode = 'XYZ'
    return e

def _limb(name, parent, length, r, m, group):
    # a capsule hanging down from the joint (-Z), parented to the joint
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=r, depth=length, location=(0, 0, -length / 2))
    c = bpy.context.active_object
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=r * 1.05, location=(0, 0, 0))
    s = bpy.context.active_object
    bpy.ops.object.select_all(action='DESELECT'); c.select_set(True); s.select_set(True)
    bpy.context.view_layer.objects.active = c; bpy.ops.object.join()
    c.name = name; c.data.materials.append(m); c.parent = parent; c['group'] = group
    return c

def person(name, h=1.8, shirt=(0.08, 0.12, 0.30), legs=(0.08, 0.10, 0.25), skin=(0.78, 0.55, 0.40),
           socks=(0.08, 0.10, 0.25), shoes=(0.05, 0.05, 0.05), hair=(0.06, 0.04, 0.03), hair_style='curly',
           long_legs=False, long_sleeves=False, gloves=None, group='body', head_group=None):
    k = h / 1.8
    M = {n: mat(f'{name}_{n}', c) for n, c in dict(shirt=shirt, legs=legs, skin=skin, socks=socks, shoes=shoes, hair=hair).items()}
    if gloves: M['gloves'] = mat(f'{name}_gloves', gloves)
    J = {}
    J['root'] = _empty(f'{name}_root', loc=(0, 0, 0.95 * k))
    J['spine'] = _empty(f'{name}_spine', J['root'])
    # torso (pelvis to shoulders), built upward from the spine joint
    bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.15 * k, depth=0.55 * k, location=(0, 0, 0.275 * k))
    t = bpy.context.active_object; t.name = f'{name}_torso'; t.scale = (1.15, 0.7, 1); t.data.materials.append(M['shirt'])
    t.parent = J['spine']; t['group'] = group
    bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.16 * k, depth=0.2 * k, location=(0, 0, -0.05 * k))
    p = bpy.context.active_object; p.name = f'{name}_pelvis'; p.scale = (1.05, 0.72, 1); p.data.materials.append(M['legs'])
    p.parent = J['root']; p['group'] = group
    J['neck'] = _empty(f'{name}_neck', J['spine'], (0, 0, 0.58 * k))
    hg = head_group or group
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=14, radius=0.11 * k, location=(0, 0, 0.13 * k))
    hd = bpy.context.active_object; hd.name = f'{name}_head'; hd.scale = (0.9, 0.95, 1.1); hd.data.materials.append(M['skin'])
    hd.parent = J['neck']; hd['group'] = hg
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.045 * k, depth=0.1 * k, location=(0, 0, 0.02 * k))
    nk = bpy.context.active_object; nk.name = f'{name}_neckmesh'; nk.data.materials.append(M['skin']); nk.parent = J['neck']; nk['group'] = hg
    if hair_style == 'curly':
        hs = []
        for dx, dy, dz in [(0, 0.03, 0.2), (0.07, 0.03, 0.17), (-0.07, 0.03, 0.17), (0, 0.08, 0.13), (0.06, 0.07, 0.1), (-0.06, 0.07, 0.1)]:
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.065 * k, location=(dx * k, dy * k, dz * k)); hs.append(bpy.context.active_object)
    elif hair_style == 'long':
        hs = []
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=0.118 * k, location=(0, 0.015 * k, 0.15 * k)); hs.append(bpy.context.active_object)
        bpy.ops.mesh.primitive_cube_add(location=(0, 0.06 * k, 0.03 * k)); b = bpy.context.active_object; b.scale = (0.11 * k, 0.05 * k, 0.17 * k); hs.append(b)
    else:  # short
        hs = []
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=0.113 * k, location=(0, 0.015 * k, 0.16 * k)); hs.append(bpy.context.active_object)
    bpy.ops.object.select_all(action='DESELECT')
    for o in hs: o.select_set(True)
    bpy.context.view_layer.objects.active = hs[0]; bpy.ops.object.join()
    hr = hs[0]; hr.name = f'{name}_hair'; hr.data.materials.append(M['hair']); hr.parent = J['neck']; hr['group'] = hg
    # arms
    for side, sx in (('L', 1), ('R', -1)):
        J[f'sh{side}'] = _empty(f'{name}_sh{side}', J['spine'], (sx * 0.2 * k, 0, 0.52 * k))
        _limb(f'{name}_uarm{side}', J[f'sh{side}'], 0.29 * k, 0.05 * k, M['shirt'], group)
        J[f'el{side}'] = _empty(f'{name}_el{side}', J[f'sh{side}'], (0, 0, -0.29 * k))
        _limb(f'{name}_farm{side}', J[f'el{side}'], 0.26 * k, 0.04 * k, M['shirt'] if long_sleeves else M['skin'], group)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8, radius=0.05 * k, location=(0, 0, -0.29 * k))
        hn = bpy.context.active_object; hn.name = f'{name}_hand{side}'; hn.data.materials.append(M['gloves'] if gloves else M['skin'])
        hn.parent = J[f'el{side}']; hn['group'] = group
    # legs
    for side, sx in (('L', 1), ('R', -1)):
        J[f'hip{side}'] = _empty(f'{name}_hip{side}', J['root'], (sx * 0.095 * k, 0, -0.06 * k))
        _limb(f'{name}_thigh{side}', J[f'hip{side}'], 0.43 * k, 0.07 * k, M['legs'], group)
        J[f'kn{side}'] = _empty(f'{name}_kn{side}', J[f'hip{side}'], (0, 0, -0.43 * k))
        _limb(f'{name}_shin{side}', J[f'kn{side}'], 0.42 * k, 0.055 * k, M['legs'] if long_legs else M['socks'], group)
        bpy.ops.mesh.primitive_cube_add(location=(0, -0.06 * k, -0.45 * k))
        ft = bpy.context.active_object; ft.name = f'{name}_foot{side}'; ft.scale = (0.05 * k, 0.12 * k, 0.04 * k)
        ft.data.materials.append(M['shoes']); ft.parent = J[f'kn{side}']; ft['group'] = group
    return J

def pose(J, frame, p, root=None):
    """p: {joint: (rx, ry, rz) degrees}; joints not given go back to 0. root: dict(loc=(x,y,z), rot=(rx,ry,rz))."""
    for n, e in J.items():
        if n == 'root': continue
        r = p.get(n, (0, 0, 0))
        e.rotation_euler = tuple(math.radians(v) for v in r)
        e.keyframe_insert('rotation_euler', frame=frame)
    if root:
        if 'loc' in root: J['root'].location = root['loc']; J['root'].keyframe_insert('location', frame=frame)
        if 'rot' in root: J['root'].rotation_euler = tuple(math.radians(v) for v in root['rot']); J['root'].keyframe_insert('rotation_euler', frame=frame)
