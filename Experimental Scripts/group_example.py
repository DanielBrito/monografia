import bpy
import bmesh

label = 'facade'
floors = 6
columns = 7
size = 1

def vert(column, row):
  return (column * size, row * size, 0)

def face(column, row):
  return (column* floors + row,
    		 (column + 1) * floors + row,
         (column + 1) * floors + 1 + row,
          column * floors + 1 + row)

verts = [vert(x, y) for x in range(columns) for y in range(floors)]
faces = [face(x, y) for x in range(columns - 1) for y in range(floors - 1)]

mesh = bpy.data.meshes.new(label)
mesh.from_pydata(verts, [], faces)

obj = bpy.data.objects.new(label, mesh)
bpy.context.scene.collection.objects.link(obj)
bpy.context.view_layer.objects.active = obj
