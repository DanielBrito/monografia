import bpy
from math import radians

# create cube
bpy.ops.mesh.primitive_cube_add()

# store the active object (cube) in a variable:
so  = bpy.context.active_object

# move object 5 units on the x axis:
so.location[0] = 5

# rotate object 45 degrees on the x axis:
so.rotation_euler[0] += radians(45)