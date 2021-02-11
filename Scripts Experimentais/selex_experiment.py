import bpy
import math

''' ------------------ DATA STRUCTURES: ------------------ '''

class Node(object):
    def __init__(self, label, obj, x=0, y=0, z=0):
        # Object label
        self.label = label
        # Object itself: 
        self.obj = obj
        # Possible children:
        self.children = []
        # Dimensions:
        self.x = x
        self.y = y
        self.z = z
        
    def addChild(self, obj):
        self.children.append(obj)
        
    def descendant(self, label):
        for child in self.children:
            if child.label == label:
                return child
    
    def getWidth(self):
        return self.obj.dimensions[0]
    
    def getDepth(self):
        return self.obj.dimensions[1]
    
    def getHeight(self):
        return self.obj.dimensions[2]
        
########################################################################

''' ------------------ FUNCTIONS: ------------------ '''

'''Creates initial 3D Mass (root node):'''

def create3DMass(label, height, depth, width):
    # Creating primitive object:
    bpy.ops.mesh.primitive_cube_add()
    
    # Selecting created object:
    bpy.data.objects["Cube"].select_set(True)
    
    # Storing reference to object:
    mass = bpy.context.selected_objects[0]
    
    # Changing name attribute to label:
    mass.name = label
    
    # Setting object dimensions:
    bpy.ops.transform.resize(value=(width/2, depth/2, height/2))
    
    bpy.data.objects[label].select_set(False)
    
    return mass


'''Utility functions for grid generation:'''

def vert(x, y, sizeRows, sizeColumns):
    # Create a single vert:
    return (x * sizeColumns, y * sizeRows, 0)

def face(x, y, rows):
    # Create a single face:
    return (x * rows + y,
           (x + 1) * rows + y,
           (x + 1) * rows + 1 + y,
           x * rows + 1 + y)


'''Creates virtual shape:'''

def createGrid(label, width, height, rows, columns):
    # Changing for desired number of rows and columns:
    rows += 1
    columns += 1
    
    # Calculating size of the cells:
    sizeRows = (height/2) / ((rows-1) / 2)
    sizeColumns = (width/2) / ((columns-1) / 2)

    # Looping to create the grid:
    verts = [vert(x, y, sizeRows, sizeColumns) for x in range(columns) for y in range(rows)]
    faces = [face(x, y, rows) for x in range(columns - 1) for y in range(rows - 1)]

    # Create Mesh Datablock:
    mesh = bpy.data.meshes.new(label)
    mesh.from_pydata(verts, [], faces)

    # Create Object and link to scene:
    obj = bpy.data.objects.new(label, mesh)
    bpy.context.scene.collection.objects.link(obj)

    # Select the object:
    bpy.context.view_layer.objects.active = obj
    bpy.data.objects[label].select_set(True)

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
    
    bpy.data.objects[label].select_set(False)


########################################################################

''' ------------------ SIMULATING SELEX RULES: ------------------ '''

'''C1: Initial settings:'''

label = "building"
height = 5
width = 9
depth = 11


'''C2: {<> -> createShape("building", height, width, depth)};'''

mass3D = create3DMass(label, height, depth, width)

# Defining shape tree root node:
root = Node("root", None)

# Adding building mass node:
root.addChild(Node(label, mass3D))

# Retrieving root node descendant by label:
building = root.descendant("building")

# Configuring object mode:
bpy.ops.object.mode_set(mode = "EDIT")
bpy.ops.mesh.select_all(action = "DESELECT")
bpy.ops.object.mode_set(mode = "OBJECT")

# Creating nodes with object faces:
front = Node(building.label + "_" + "front", building.obj.data.polygons[3])
left = Node(building.label + "_" + "left", building.obj.data.polygons[0])
right = Node(building.label + "_" + "right", building.obj.data.polygons[2])
back = Node(building.label + "_" + "back", building.obj.data.polygons[1])

# Adding front, back, left and right faces as children:
building.addChild(front)
building.addChild(left)
building.addChild(right)
building.addChild(back)

# Reseting object mode:
bpy.ops.object.mode_set(mode = "EDIT")
bpy.ops.mesh.select_all(action = "DESELECT")
bpy.ops.object.mode_set(mode = "OBJECT")


'''C3: {<[label=="building_front"]> -> createGrid("facade", 4, 4)};'''

# Retrieving object dimensions:
# BUILDING-FRONT!!!! SELECT DIMENSIONS (EDGE LENGTH) OF A SPECIFIC FACE...
faceWidth = building.getWidth()
faceHeight = building.getHeight()

# Printing dimensions:
print(faceWidth, faceHeight)

# Defining number of rows and columns of the grid:
rows = 4
columns = 4

label = "facade"

# Using dimensions to generate grid:
createGrid(label, int(faceWidth), int(faceHeight), rows, columns)