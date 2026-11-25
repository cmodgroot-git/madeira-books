# Background for the book 22 pitch, modelled on the page paintings: a steep green hillside packed with
# white/cream houses with terracotta roofs, a tall cliff wall running to a headland, the sea on the right,
# a few bigger 2-3 storey buildings and trees just beyond the stand. All objects get group='set'.
import bpy, bmesh, math, random
from mathutils import Vector, noise

def mat(name, rgb, rough=0.8):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*rgb, 1.0); m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    if b: b.inputs["Base Color"].default_value = (*rgb, 1.0); b.inputs["Roughness"].default_value = rough
    return m

def coast(y):            # land is where x < coast(y): the cliff line runs away to the right and out to a headland
    return -6 + 0.55 * (y - 40)

def height(x, y):
    if y < 40: return -0.5
    h = 2 + max(0, y - 75) * 0.62 + max(0, -x - 20) * 0.12
    h += 260 * min(1, max(0, (y - 260) / 80)) ** 1.5          # the cliff band behind the town
    h += 14 * noise.noise(Vector((x / 60, y / 60, 0.3))) + 5 * noise.noise(Vector((x / 15, y / 15, 1.7)))
    d = coast(y) - x                                           # distance inland from the coastline
    if d < 0: return -6.0
    if d < 25: h *= (d / 25) ** 0.35                          # steep cliff face down to the sea
    return min(h, 480)

def build():
    for n in ('hill', 'cliff', 'houses', 'sea', 'terrain', 'town', 'near_buildings', 'trees'):
        o = bpy.data.objects.get(n)
        if o: bpy.data.objects.remove(o, do_unlink=True)
    grass = mat('bg_grass', (0.30, 0.43, 0.20)); rock = mat('bg_rock', (0.36, 0.33, 0.24)); sea = mat('sea', (0.16, 0.38, 0.60), 0.2)
    walls = [mat('bg_white', (0.94, 0.92, 0.87)), mat('bg_cream', (0.93, 0.86, 0.68)), mat('bg_ochre', (0.89, 0.74, 0.42)), mat('bg_pink', (0.93, 0.80, 0.72))]
    roof = mat('bg_roof', (0.72, 0.33, 0.20)); tree = mat('bg_tree', (0.20, 0.34, 0.15)); win = mat('bg_window', (0.25, 0.27, 0.30))
    # terrain
    me = bpy.data.meshes.new('terrain'); bm = bmesh.new()
    X0, X1, Y0, Y1, NX, NY = -520.0, 420.0, 30.0, 760.0, 190, 150
    vs = [[bm.verts.new((X0 + (X1 - X0) * i / NX, Y0 + (Y1 - Y0) * j / NY, 0)) for i in range(NX + 1)] for j in range(NY + 1)]
    for row in vs:
        for v in row: v.co.z = height(v.co.x, v.co.y)
    for j in range(NY):
        for i in range(NX):
            bm.faces.new((vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]))
    bm.normal_update()
    for f in bm.faces:
        f.material_index = 1 if f.normal.z < 0.55 else 0
        if all(v.co.z < -1 for v in f.verts): f.material_index = 0
    bm.to_mesh(me); bm.free()
    t = bpy.data.objects.new('terrain', me); bpy.context.scene.collection.objects.link(t)
    me.materials.append(grass); me.materials.append(rock); t['group'] = 'set'
    # sea
    bpy.ops.mesh.primitive_plane_add(size=1, location=(200, 600, -2.0)); s = bpy.context.active_object
    s.name = 'sea'; s.scale = (2400, 1600, 1); bpy.ops.object.transform_apply(scale=True); s.data.materials.append(sea); s['group'] = 'set'
    # town on the slope: many small houses, denser and smaller farther up
    random.seed(22); bm = bmesh.new(); me = bpy.data.meshes.new('town')
    def house(cx, cy, z, w, d, h, wall_i, ang):
        ca, sa = math.cos(ang), math.sin(ang)
        P = lambda x, y, zz: Vector((cx + x * ca - y * sa, cy + x * sa + y * ca, zz))
        b = [bm.verts.new(P(sx * w / 2, sy * d / 2, zz)) for zz in (z - 2, z + h) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        for q in ((0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7)):
            f = bm.faces.new([b[i] for i in q]); f.material_index = wall_i
        apex = bm.verts.new(P(0, 0, z + h + 0.45 * min(w, d)))
        e = [bm.verts.new(P(sx * (w / 2 + 0.4), sy * (d / 2 + 0.4), z + h - 0.2)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        for i in range(4):
            f = bm.faces.new((e[i], e[(i + 1) % 4], apex)); f.material_index = 4
        # a dark window band on the side facing the sea / camera
        wv = [bm.verts.new(P(sx * w * 0.3, -d / 2 - 0.05, z + h * zz)) for zz, sx in ((0.45, -1), (0.45, 1), (0.75, 1), (0.75, -1))]
        f = bm.faces.new(wv); f.material_index = 5
    n = 0
    while n < 1500:
        x = random.uniform(-330, 140); y = random.uniform(85, 290)
        if x > coast(y) - 8: continue
        z = height(x, y)
        if z > 140 or z < 3: continue
        sl = abs(height(x + 3, y) - height(x - 3, y)) + abs(height(x, y + 3) - height(x, y - 3))
        if sl > 9: continue
        far = (y - 55) / 245
        w = random.uniform(5, 8.5); d = w * random.uniform(0.7, 1.1); h = random.uniform(4.5, 7.5)
        house(x, y, z, w, d, h, random.choice([0, 0, 0, 1, 1, 2, 3]), math.radians(random.uniform(-12, 12)))
        n += 1
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('town', me); bpy.context.scene.collection.objects.link(o)
    for m in walls + [roof, win]: me.materials.append(m)
    o['group'] = 'set'
    # bigger buildings and trees just beyond the stand (left of picture)
    bm = bmesh.new(); me = bpy.data.meshes.new('near_buildings')
    for (x, y, w, d, h, wi) in [(-30, 14, 12, 9, 10, 2), (-42, 20, 13, 10, 12, 0), (-27, 30, 11, 9, 11, 3), (-52, 34, 12, 9, 13, 1), (-38, 40, 10, 9, 12, 0)]:
        house(x, y, 0.0, w, d, h, wi, math.radians(-8))
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('near_buildings', me); bpy.context.scene.collection.objects.link(o)
    for m in walls + [roof, win]: me.materials.append(m)
    o['group'] = 'set'
    bm = bmesh.new(); me = bpy.data.meshes.new('trees')
    for (x, y, r) in [(-22, 9, 2.2), (-35, 11, 2.6), (-47, 15, 2.8), (-20, 20, 2.0)]:
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r, matrix=__import__('mathutils').Matrix.Translation((x, y, r + 1.5)))
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('trees', me); bpy.context.scene.collection.objects.link(o); me.materials.append(tree); o['group'] = 'set'
    # low stone wall around the back of the pitch, under the existing railing
    o = bpy.data.objects.get('back_wall')
    if o: bpy.data.objects.remove(o, do_unlink=True)
    bpy.ops.mesh.primitive_cube_add(location=(0, 5.6, 0.6)); bw = bpy.context.active_object; bw.name = 'back_wall'
    bw.scale = (30, 0.25, 0.6); bpy.ops.object.transform_apply(scale=True); bw.data.materials.append(mat('bg_wall', (0.62, 0.60, 0.55))); bw['group'] = 'set'
    # sky
    w = bpy.context.scene.world; w.color = (0.62, 0.76, 0.90)
    if w.use_nodes and w.node_tree.nodes.get('Background'): w.node_tree.nodes['Background'].inputs[0].default_value = (0.62, 0.76, 0.90, 1)
