import bpy
from math import radians

# create cube
bpy.ops.mesh.primitive_cube_add()
so  = bpy.context.active_object

# rotate object 45 degrees on the x axis:
so.rotation_euler[0] += radians(45)

# create modifier
modifier_subsurf = so.modifiers.new("My Modifier", 'SUBSURF')

# apply modifier to round the cube:
modifier_subsurf.levels = 3

# smooth the object:
bpy.ops.object.shade_smooth()