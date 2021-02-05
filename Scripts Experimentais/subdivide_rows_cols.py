import bpy

facade = 'Facade'
floors = 6 # Real number of floors = 5
columns = 7 # Real number of columns = 6
size = 1 # Size of the grid

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
