import bpy
import bmesh

bpy.ops.object.mode_set(mode = 'OBJECT')
obj = bpy.context.active_object

bpy.ops.object.mode_set(mode = 'EDIT') 
bpy.ops.mesh.select_mode(type="VERT")

bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

obj.data.vertices[6].select = True
obj.data.vertices[2].select = True

bpy.ops.object.mode_set(mode = 'EDIT')

bpy.ops.mesh.bevel(offset=2.25466, offset_pct=0, segments=20, vertex_only=False)

bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')