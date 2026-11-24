import bpy, sys, json
bpy.ops.wm.open_mainfile(filepath=sys.argv[-2])
sc=bpy.context.scene; out={'frames':[sc.frame_start,sc.frame_end,sc.render.fps],'res':[sc.render.resolution_x,sc.render.resolution_y],'objs':{}}
for o in bpy.data.objects:
    d={'type':o.type,'loc':[round(v,3) for v in o.location],'rot':[round(v,3) for v in o.rotation_euler],'scale':[round(v,3) for v in o.scale],
       'parent':o.parent.name if o.parent else None,'group':o.get('group'),'hide':o.hide_render,
       'nverts':len(o.data.vertices) if o.type=='MESH' else None,'lens':round(o.data.lens,2) if o.type=='CAMERA' else None}
    if o.animation_data and o.animation_data.action:
        a=o.animation_data.action; ks={}
        try: fcs=a.fcurves
        except AttributeError:
            fcs=[fc for l in a.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves]
        for fc in fcs: ks[f'{fc.data_path}[{fc.array_index}]']=[(round(k.co[0],1),round(k.co[1],3)) for k in fc.keyframe_points]
        d['keys']=ks
    out['objs'][o.name]=d
json.dump(out,open(sys.argv[-1],'w'))
