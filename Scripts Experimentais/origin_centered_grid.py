import bpy

# Settings:
facade = 'Facade'
floors = 4 # Real number of floors = 3
columns = 4 # Real number of columns = 3
size = 1 # Size of each cell (size x size)

# Utility functions:
def vert(column, row):
    # Create a single vert:
    return (column * size, row * size, 0)


def face(column, row):
    # Create a single face:
    return (column* floors + row,
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