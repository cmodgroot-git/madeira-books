import bpy, sys
import os; bpy.ops.wm.open_mainfile(filepath=os.environ.get('BLEND','/home/claude/work/bl/b22p4.blend'))
s=bpy.context.scene; s.render.resolution_x=1280; s.render.resolution_y=720
s.render.engine='BLENDER_WORKBENCH'; s.view_settings.view_transform='Standard'; sh=s.display.shading; sh.light='STUDIO'; sh.color_type='MATERIAL'; sh.show_shadows=True; sh.show_cavity=True
frames=[int(x) for x in sys.argv[sys.argv.index('--')+1].split(',')] if '--' in sys.argv else list(range(0,284))
out=sys.argv[sys.argv.index('--')+2] if '--' in sys.argv and len(sys.argv)>sys.argv.index('--')+2 else '/home/claude/work/bl/prev/'
for f in frames:
    s.frame_set(f); s.render.filepath=f'{out}{f:03d}.png'; bpy.ops.render.render(write_still=True)
