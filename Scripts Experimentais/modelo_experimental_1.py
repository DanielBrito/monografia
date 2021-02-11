import bpy 
import math 
from mathutils import Matrix

# CREATING MASS MODEL:

# Settings 

name = 'Mass' 

# Origin point transformation settings 
mesh_offset = (0, 0, 0) 
origin_offset = (0, 0, 0) 

# Matrices settings 

translation = (0, 0, 0) 
scale_factor = 1 
scale_axis = (1, 1, 1) 
rotation_angle = math.radians(0) 
rotation_axis = 'X' 

# Utility Functions 

def vert(x,y,z): 
    """ Make a vertex """ 
    return (x + origin_offset[0], y + origin_offset[1], z + origin_offset[2]) 

# Cube Code 

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

# Add Object to Scene 

mesh = bpy.data.meshes.new(name) 
mesh.from_pydata(verts, [], faces) 

obj = bpy.data.objects.new(name, mesh) 
bpy.context.scene.collection.objects.link(obj) 

bpy.context.view_layer.objects.active = obj 
bpy.data.objects['Mass'].select_set(True)

# Offset mesh to move origin point 

obj.location = [(i * -1) + mesh_offset[j] for j, i in enumerate(origin_offset)] 

# Matrix Magic 

translation_matrix = Matrix.Translation(translation) 
scale_matrix = Matrix.Scale(scale_factor, 4, scale_axis) 
rotation_mat = Matrix.Rotation(rotation_angle, 4, rotation_axis) 
obj.matrix_world @= translation_matrix @ rotation_mat @ scale_matrix 

###########################################################################

# CREATING CUSTOM GRID:

facade = 'Facade'

mass_height = 1
mass_width = 1

floors = 5 # -> real floors = value - 1
columns = 5 #  -> real columns = value -1

size_floors = mass_height / ((floors-1) / 2)
size_columns = mass_width / ((columns-1) / 2)

# Utility functions
def vert(column, row):
    """ Create a single vert """
    return (column * size_columns, row * size_floors, 0)

def face(column, row):
    """ Create a single face """
    return (column * floors + row,
           (column + 1) * floors + row,
           (column + 1) * floors + 1 + row,
           column * floors + 1 + row)

# Looping to create the grid
verts = [vert(x, y) for x in range(columns) for y in range(floors)]
faces = [face(x, y) for x in range(columns - 1) for y in range(floors - 1)]

# Create Mesh Datablock
mesh = bpy.data.meshes.new(facade)
mesh.from_pydata(verts, [], faces)

# Create Object and link to scene
obj = bpy.data.objects.new(facade, mesh)
bpy.context.scene.collection.objects.link(obj)

# Select the object
bpy.context.view_layer.objects.active = obj
bpy.data.objects['Facade'].select_set(True)

# Moves object origin to its center:
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

# Move 3D cursor to scene origin:
bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)

# Move shape origin to scene origin: 
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        override = bpy.context.copy()
        override['area'] = area
        override['region'] = area.regions[4]
        bpy.ops.view3d.snap_selected_to_cursor(override, use_offset=False)
        
# Transforming grid properly to 'match' a specific face:
bpy.context.object.rotation_euler[0] = 1.5708 # x-axis rotation (90)
bpy.context.object.rotation_euler[2] = 1.5708 # z-axis rotation (90)

bpy.context.object.location[0] = 1 # translate on x-axis to proper position

###########################################################################

# Deselecting objects from the scene:
for obj in bpy.data.objects:
    obj.select_set(False)

###########################################################################

# SEPARATING SUBGRID:

bpy.ops.object.mode_set(mode = 'OBJECT')

# Deselect everything:
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_all(action = 'DESELECT')

# Reselect specific face:
bpy.ops.object.mode_set(mode = 'OBJECT')

bpy.data.objects['Facade'].data.polygons[0].select = True
bpy.data.objects['Facade'].data.polygons[1].select = True
bpy.data.objects['Facade'].data.polygons[4].select = True
bpy.data.objects['Facade'].data.polygons[5].select = True

bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_mode(type='FACE')

# Separate selected subgrid from 'Facade' creating a new form:
bpy.ops.mesh.separate(type='SELECTED')

###########################################################################

# Deselecting objects from the scene:
for obj in bpy.data.objects:
    obj.select_set(False)
    
###########################################################################

# DISSOLVING INTERNAL EDGES:

bpy.data.objects["Facade.001"].select_set(True)

bpy.ops.object.mode_set(mode = 'OBJECT')
obj = bpy.data.objects['Facade.001']

bpy.ops.object.mode_set(mode = 'EDIT') 
bpy.ops.mesh.select_mode(type="EDGE")

bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Selecting internal edges:
obj.data.edges[5].select = True
obj.data.edges[3].select = True
obj.data.edges[9].select = True
obj.data.edges[2].select = True

bpy.ops.object.mode_set(mode = 'EDIT')

bpy.ops.mesh.dissolve_edges()

bpy.ops.mesh.select_all(action = 'DESELECT')

bpy.data.objects["Facade.001"].select_set(False)

###########################################################################

# JOINING SUBGRID TO MASS:

bpy.ops.object.mode_set(mode = 'OBJECT')

obj = bpy.context.window.scene.objects["Facade.001"]
obj = bpy.context.window.scene.objects["Mass"]

bpy.data.objects["Facade.001"].select_set(True)
bpy.data.objects["Mass"].select_set(True)

bpy.context.view_layer.objects.active = obj    # 'obj' is the active object now

bpy.ops.object.join()

#bpy.ops.object.mode_set(mode = 'OBJECT')
#obj = bpy.context.active_object

#bpy.ops.object.mode_set(mode = 'EDIT') 
#bpy.ops.mesh.select_mode(type="FACE")

#bpy.ops.mesh.select_all(action = 'DESELECT')
#bpy.ops.object.mode_set(mode = 'OBJECT')

#bpy.ops.object.mode_set(mode = 'EDIT')

###########################################################################

# EXTRUDING SUBGRID FACE:

bpy.ops.object.mode_set(mode = 'OBJECT')
obj = bpy.context.active_object

bpy.ops.object.mode_set(mode = 'EDIT') 
bpy.ops.mesh.select_mode(type="FACE")

bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

bpy.data.objects['Mass'].data.polygons[6].select = True

bpy.ops.object.mode_set(mode = 'EDIT')

bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"use_normal_flip":False, "mirror":False}, 
                                   TRANSFORM_OT_translate={"value":(0, 0, 0.862433), 
                                                           "orient_type":'NORMAL', 
                                                           "orient_matrix":((-2.98023e-08, -8.88178e-16, -1), 
                                                                            (-2.98023e-08, 1, 0), 
                                                                            (1, 2.98023e-08, -2.98023e-08)), 
                                                           "orient_matrix_type":'NORMAL', 
                                                           "constraint_axis":(False, False, True), 
                                                           "mirror":False, "use_proportional_edit":False, 
                                                           "proportional_edit_falloff":'SMOOTH', 
                                                           "proportional_size":1, 
                                                           "use_proportional_connected":False, 
                                                           "use_proportional_projected":False, 
                                                           "snap":False, 
                                                           "snap_target":'CLOSEST', 
                                                           "snap_point":(0, 0, 0), 
                                                           "snap_align":False, 
                                                           "snap_normal":(0, 0, 0), 
                                                           "gpencil_strokes":False, 
                                                           "cursor_transform":False, 
                                                           "texture_space":False, 
                                                           "remove_on_cancel":False, 
                                                           "release_confirm":False, 
                                                           "use_accurate":False})

bpy.ops.object.mode_set(mode = 'OBJECT')
obj = bpy.context.active_object

bpy.ops.object.mode_set(mode = 'EDIT') 
bpy.ops.mesh.select_mode(type="EDGE")

bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

obj.data.edges[16].select = True
obj.data.edges[18].select = True

bpy.ops.object.mode_set(mode = 'EDIT')

bpy.ops.mesh.bevel(offset=0.440091, offset_pct=0, segments=10, vertex_only=False)

bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')