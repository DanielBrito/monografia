import bpy 
import math 
from mathutils import Matrix

# Settings:
name = 'Mass' 

# Origin point transformation settings:
mesh_offset = (0, 0, 0) 
origin_offset = (0, 0, 0) 

# Matrices settings:
translation = (0, 0, 0) 
scale_factor = 1 
scale_axis = (1, 1, 1) 
rotation_angle = math.radians(0) 
rotation_axis = 'X' 

# Utility Functions:
def vert(x,y,z): 
    """ Make a vertex """ 
    return (x + origin_offset[0], y + origin_offset[1], z + origin_offset[2]) 

# Cube Code:
verts = [vert(1.0, 1.0, -1.0), 
         vert(1.0, -1.0, -1.0), 
         vert(-1.0, -1.0, -1.0), 
         vert(-1.0, 1.0, -1.0), 
         vert(1.0, 1.0, 1.0), 
         vert(1.0, -1.0, 1.0), 
         vert(-1.0, -1.0, 1.0), 
         vert(-1.0, 1.0, 1.0)] 

faces = [(0, 1, 2, 3), 
         (4, 7, 6, 5), 
         (0, 4, 5, 1), 
         (1, 5, 6, 2), 
         (2, 6, 7, 3), 
         (4, 0, 3, 7)] 

# Add Object to Scene:
mesh = bpy.data.meshes.new(name) 
mesh.from_pydata(verts, [], faces) 

obj = bpy.data.objects.new(name, mesh) 
bpy.context.scene.collection.objects.link(obj) 

bpy.context.view_layer.objects.active = obj 
bpy.data.objects['Mass'].select_set(True)

# Offset mesh to move origin point:
obj.location = [(i * -1) + mesh_offset[j] for j, i in enumerate(origin_offset)] 

# Matrix Magic:
translation_matrix = Matrix.Translation(translation) 
scale_matrix = Matrix.Scale(scale_factor, 4, scale_axis) 
rotation_mat = Matrix.Rotation(rotation_angle, 4, rotation_axis) 
obj.matrix_world @= translation_matrix @ rotation_mat @ scale_matrix 

# Scale on X-axis:
bpy.context.object.scale[0] = 2