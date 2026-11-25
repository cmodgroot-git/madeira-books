# grey previz video + per-group ID masks (flat colours, no anti-aliasing) for every frame
import bpy, os
import os; bpy.ops.wm.open_mainfile(filepath=os.environ.get('BLEND','/home/claude/work/bl/b22p4.blend'))
OUT=os.environ.get('OUT','/home/claude/work/bl')
FR=[int(x) for x in os.environ['FRAMES'].split(',')] if os.environ.get('FRAMES') else None
s = bpy.context.scene; s.render.resolution_x = 1280; s.render.resolution_y = 720; s.render.engine = 'BLENDER_WORKBENCH'; s.view_settings.view_transform = 'Standard'
os.makedirs(OUT+'/grey', exist_ok=True); os.makedirs(OUT+'/ids', exist_ok=True)
sh = s.display.shading
# pass 1: shaded previz
sh.light = 'STUDIO'; sh.color_type = 'MATERIAL'; sh.show_shadows = True; sh.show_cavity = True; s.display.render_aa = '8'
for f in (FR or range(s.frame_start, s.frame_end + 1)):
    s.frame_set(f); s.render.filepath = f'{OUT}/grey/{f:03d}.png'; bpy.ops.render.render(write_still=True)
# pass 2: ID colours per group
ID = {'bola': (1, 0, 0), 'cabeca': (0, 1, 0), 'golo': (0, 0, 1), 'rita': (1, 1, 0), 'keeper': (1, 0, 1), 'tiago': (0, 1, 1), 'ana': (1, 0.5, 0), 'graca': (0.5, 0, 1), 'set': (0, 0, 0)}
for o in s.objects:
    if o.type == 'MESH': o.color = (*ID.get(o.get('group', 'set'), (0, 0, 0)), 1)
sh.light = 'FLAT'; sh.color_type = 'OBJECT'; sh.show_shadows = False; sh.show_cavity = False; sh.show_specular_highlight = False
s.display.render_aa = 'OFF'; s.view_settings.view_transform = 'Standard'
w = s.world; w.color = (0, 0, 0)
sh.background_type = 'VIEWPORT'; sh.background_color = (0, 0, 0)
for f in (FR or range(s.frame_start, s.frame_end + 1)):
    s.frame_set(f); s.render.filepath = f'{OUT}/ids/{f:03d}.png'; bpy.ops.render.render(write_still=True)
