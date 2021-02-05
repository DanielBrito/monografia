import bpy
import bmesh

# Assuming there is a subdivided (once) plane on the scene:

bpy.ops.object.mode_set(mode = 'OBJECT')
obj = bpy.context.active_object

bpy.ops.object.mode_set(mode = 'EDIT') 
bpy.ops.mesh.select_mode(type="EDGE")

bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Selecting internal edges:
obj.data.edges[8].select = True
obj.data.edges[9].select = True
obj.data.edges[10].select = True
obj.data.edges[11].select = True

bpy.ops.object.mode_set(mode = 'EDIT')

# Dissolving internal edges:
bpy.ops.mesh.dissolve_edges()

bpy.ops.mesh.select_all(action = 'SELECT')