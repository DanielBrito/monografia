import bpy

bpy.ops.object.mode_set(mode = 'OBJECT')
obj = bpy.context.active_object

bpy.ops.object.mode_set(mode = 'EDIT') 
bpy.ops.mesh.select_mode(type="VERT")
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Selecting vertex by its index:
obj.data.vertices[6].select = True

bpy.ops.object.mode_set(mode = 'EDIT') 