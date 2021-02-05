import bpy
import bmesh

mode = bpy.context.active_object.mode

# We need to switch from Edit mode to Object mode so the selection gets updated:
bpy.ops.object.mode_set(mode='OBJECT')

# Storing selected vertexes form object:
selectedVerts = [v for v in bpy.context.active_object.data.vertices if v.select]

# Printing indexes of the selected vertexes:
for v in selectedVerts:
    print(v.index)

# Back to whatever mode we were in:
bpy.ops.object.mode_set(mode=mode)