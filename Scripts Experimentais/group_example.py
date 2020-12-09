import bpy

# Object configuration:
facade = 'Facade'
floors = 6
columns = 7
size = 1

# Create a single vertex
def vert(column, row):
  return (column * size, row * size, 0)

# Create a single face
def face(column, row):
  return (column* floors + row,
    		 (column + 1) * floors + row,
         (column + 1) * floors + 1 + row,
          column * floors + 1 + row)

# Create grid:
verts = [vert(x, y) for x in range(columns) for y in range(floors)]
faces = [face(x, y) for x in range(columns - 1) for y in range(floors - 1)]

# Create mesh:
mesh = bpy.data.meshes.new(facade)
mesh.from_pydata(verts, [], faces)

# Link object to the scene:
obj = bpy.data.objects.new(facade, mesh)
bpy.context.scene.collection.objects.link(obj)

# Select object:
bpy.context.view_layer.objects.active = obj
