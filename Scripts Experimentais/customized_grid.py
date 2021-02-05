import bpy

# Settings:
facade = 'Facade'

mass_height = 1
mass_width = 2

# real number floors = value - 1 -> In this case: floors = 2
floors = 3

# real number of columns = value -1 -> In this case: columns = 4
columns = 4

# Calculating size of the cells:
size_floors = mass_height / ((floors-1) / 2)
size_columns = mass_width / ((columns-1) / 2)

# Utility functions:
def vert(column, row):
    # Create a single vert:
    return (column * size_columns, row * size_floors, 0)

def face(column, row):
    # Create a single face:
    return (column * floors + row,
           (column + 1) * floors + row,
           (column + 1) * floors + 1 + row,
           column * floors + 1 + row)

# Looping to create the grid:
verts = [vert(x, y) for x in range(columns) for y in range(floors)]
faces = [face(x, y) for x in range(columns - 1) for y in range(floors - 1)]

# Create Mesh Datablock:
mesh = bpy.data.meshes.new(facade)
mesh.from_pydata(verts, [], faces)

# Create Object and link to scene:
obj = bpy.data.objects.new(facade, mesh)
bpy.context.scene.collection.objects.link(obj)

# Select the object:
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

'''
# Improve index positioning, but invert number of columns with number of floors for M x N grids:

Generated    Rotated
 [1] [3]     [0] [1]
 [0] [2]     [2] [3]

# bpy.context.object.rotation_euler[1] = 1.5708 # y-axis rotation (90)
'''
# Translate on x-axis to proper position:
bpy.context.object.location[0] = 1