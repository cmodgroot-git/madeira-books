# Histórias da Madeira — previz set: the Funchal-style seaside pitch from book 22 (O Jogo de Domingo).
# Units are metres. x = right, y = away from the camera, z = up. Goal line on y = 0, goal centred on x = 0.
import bpy, math
from mathutils import Vector

def mat(name, rgb, rough=0.8):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1.0)          # Workbench uses this
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    if b:
        b.inputs["Base Color"].default_value = (*rgb, 1.0)
        b.inputs["Roughness"].default_value = rough
    return m

def box(name, loc, size, m, coll=None):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.active_object; o.name = name
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(m)
    return o

def cyl(name, p, q, r, m, verts=16):
    p, q = Vector(p), Vector(q); d = q - p
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=d.length, location=(p + q) / 2)
    o = bpy.context.active_object; o.name = name
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    o.data.materials.append(m)
    return o

def join(objs, name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join(); objs[0].name = name
    return objs[0]

def build_pitch():
    M = {
        'grass': mat('grass', (0.20, 0.42, 0.16)), 'line': mat('line', (0.92, 0.92, 0.88)),
        'post': mat('post', (0.93, 0.91, 0.84), 0.5), 'net': mat('net', (0.85, 0.85, 0.82)),
        'wall': mat('wall', (0.55, 0.53, 0.50)), 'seat': mat('seat', (0.10, 0.25, 0.62), 0.4),
        'stone': mat('stone', (0.62, 0.60, 0.56)), 'sea': mat('sea', (0.18, 0.38, 0.58), 0.2),
        'cliff': mat('cliff', (0.30, 0.36, 0.22)), 'house': mat('house', (0.90, 0.80, 0.62)),
        'roof': mat('roof', (0.70, 0.33, 0.22)), 'rail': mat('rail', (0.35, 0.35, 0.36), 0.4),
    }
    objs = {}
    # pitch and markings
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -12, 0)); g = bpy.context.active_object
    g.name = 'pitch'; g.scale = (60, 40, 1); bpy.ops.object.transform_apply(scale=True); g.data.materials.append(M['grass'])
    lines = [box('l_goal', (0, 0, 0.003), (40, 0.12, 0.006), M['line']),
             box('l_6a', (-9.16, -2.75, 0.003), (0.12, 5.5, 0.006), M['line']),
             box('l_6b', (9.16, -2.75, 0.003), (0.12, 5.5, 0.006), M['line']),
             box('l_6c', (0, -5.5, 0.003), (18.32, 0.12, 0.006), M['line']),
             box('l_18c', (0, -16.5, 0.003), (40.3, 0.12, 0.006), M['line'])]
    objs['lines'] = join(lines, 'lines')
    # goal: posts, crossbar, back frame, net (wireframe grid)
    W2, H, D = 1.8, 2.4, 1.6; r = 0.05   # small local-pitch goal, as painted in book 22
    parts = [cyl('pl', (-W2, 0, 0), (-W2, 0, H + r), r, M['post']), cyl('pr', (W2, 0, 0), (W2, 0, H + r), r, M['post']),
             cyl('bar', (-W2 - r, 0, H), (W2 + r, 0, H), r, M['post'])]
    objs['goal'] = join(parts, 'goal')
    back = [cyl('bl', (-W2, D, 0), (-W2, D * 0.4, H), 0.025, M['post']), cyl('br', (W2, D, 0), (W2, D * 0.4, H), 0.025, M['post']),
            cyl('bb', (-W2, D, 0.02), (W2, D, 0.02), 0.025, M['post'])]
    objs['goal_back'] = join(back, 'goal_back')
    def net_plane(name, corners, nu, nv):
        bpy.ops.mesh.primitive_grid_add(x_subdivisions=nu, y_subdivisions=nv, size=1)
        o = bpy.context.active_object; o.name = name
        me = o.data; c = [Vector(v) for v in corners]
        for v in me.vertices:
            u, w = v.co.x + 0.5, v.co.y + 0.5
            v.co = c[0].lerp(c[1], u).lerp(c[3].lerp(c[2], u), w)
        md = o.modifiers.new('wire', 'WIREFRAME'); md.thickness = 0.012
        o.data.materials.append(M['net']); return o
    nets = [net_plane('net_back', [(-W2, D, 0), (W2, D, 0), (W2, D * 0.4, H), (-W2, D * 0.4, H)], 26, 18),
            net_plane('net_top', [(-W2, 0, H), (W2, 0, H), (W2, D * 0.4, H), (-W2, D * 0.4, H)], 26, 6),
            net_plane('net_l', [(-W2, 0, 0), (-W2, D, 0), (-W2, D * 0.4, H), (-W2, 0, H)], 14, 18),
            net_plane('net_r', [(W2, 0, 0), (W2, D, 0), (W2, D * 0.4, H), (W2, 0, H)], 14, 18)]
    for n in nets:
        bpy.context.view_layer.objects.active = n; bpy.ops.object.modifier_apply(modifier='wire')
    objs['net'] = join(nets, 'net')
    # stand: concrete step, a row of blue seats, low wall with a railing, Rita's plinth
    st = [box('step', (0, 4.6, 0.2), (40, 1.6, 0.4), M['stone']), box('wall', (0, 5.6, 0.6), (40, 0.4, 1.2), M['wall'])]
    for i in range(-30, 31):
        x = i * 0.62
        st.append(box(f'seat{i}', (x, 4.5, 0.62), (0.46, 0.42, 0.06), M['seat']))
        st.append(box(f'back{i}', (x, 4.72, 0.86), (0.46, 0.05, 0.46), M['seat']))
    objs['stand'] = join(st, 'stand')
    rl = [cyl('rail', (-20, 5.6, 1.6), (20, 5.6, 1.6), 0.03, M['rail'])] + [cyl(f'rp{i}', (i * 2, 5.6, 1.2), (i * 2, 5.6, 1.6), 0.025, M['rail']) for i in range(-10, 11)]
    objs['rail'] = join(rl, 'rail')
    objs['plinth'] = box('plinth', (-0.6, 3.0, 0.15), (0.9, 0.9, 0.3), M['stone'])
    # backdrop: sea, a green cliff on the right, white houses with red roofs climbing the hill on the left
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 300, 0)); s = bpy.context.active_object
    s.name = 'sea'; s.scale = (900, 590, 1); bpy.ops.object.transform_apply(scale=True); s.data.materials.append(M['sea'])
    # right: the green cliff dropping to the sea; left: a hillside of houses (as in the book 22 paintings)
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=160, radius2=15, depth=170, location=(150, 330, 60))
    c = bpy.context.active_object; c.name = 'cliff'; c.scale = (1, 0.5, 1); c.data.materials.append(M['cliff'])
    bpy.ops.mesh.primitive_cube_add(location=(-120, 150, -20)); h = bpy.context.active_object; h.name = 'hill'
    h.scale = (100, 70, 45); h.rotation_euler = (math.radians(14), math.radians(-12), math.radians(28))
    bpy.ops.object.transform_apply(scale=True, rotation=True); h.data.materials.append(M['cliff'])
    import random; random.seed(7); hs = []
    dep = bpy.context.evaluated_depsgraph_get()
    for i in range(160):
        x = random.uniform(-170, -25); y = random.uniform(60, 200)
        ok, loc, nrm, idx, ob, mx = bpy.context.scene.ray_cast(dep, Vector((x, y, 400)), Vector((0, 0, -1)))
        if not ok or ob.name != 'hill': continue
        z = loc.z
        hs.append(box(f'h{i}', (x, y, z + 2.5), (7, 7, 5), M['house']))
        hs.append(box(f'r{i}', (x, y, z + 5.5), (7.6, 7.6, 1.0), M['roof']))
    objs['houses'] = join(hs, 'houses')
    return objs

def build_camera():
    cam = bpy.data.cameras.new('cam'); cam.lens = 26.0; cam.sensor_width = 36
    o = bpy.data.objects.new('camera', cam); bpy.context.scene.collection.objects.link(o)
    o.location = (2.0, -5.0, 1.4)   # matched to page 4 by fitting the goal corners
    d = Vector((-0.5, 0, 1.4)) - o.location
    o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = o
    return o

def build_light():
    sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 3.5; sun.angle = math.radians(8)
    o = bpy.data.objects.new('sun', sun); bpy.context.scene.collection.objects.link(o)
    o.rotation_euler = (math.radians(50), math.radians(10), math.radians(-35))
    w = bpy.context.scene.world or bpy.data.worlds.new('world'); bpy.context.scene.world = w
    w.use_nodes = True; bg = w.node_tree.nodes.get('Background')
    if bg: bg.inputs[0].default_value = (0.62, 0.75, 0.88, 1); bg.inputs[1].default_value = 0.9
    w.color = (0.62, 0.75, 0.88)
