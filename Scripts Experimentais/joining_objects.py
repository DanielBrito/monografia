import bpy
import bmesh

# Assuming there are a 'Cube' and 'Plane' (over its face):

# Selecting objects to be joined:
bpy.data.objects["Cube"].select_set(True)
bpy.data.objects["Plane"].select_set(True)

# Joining selected objects:
bpy.ops.object.join()

bpy.ops.object.mode_set(mode = 'OBJECT')
obj = bpy.context.active_object

bpy.ops.object.mode_set(mode = 'EDIT') 
bpy.ops.mesh.select_mode(type="FACE")

bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Selecting especific face for future extrusion:
bpy.data.objects['Cube'].data.polygons[6].select = True

bpy.ops.object.mode_set(mode = 'EDIT')