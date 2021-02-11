import bpy
import math

''' ------------------ DATA STRUCTURES: ------------------ '''

class Node(object):
    # Label and Object are required for every node:
    def __init__(self, label, obj, dimX=0, dimY=0, dimZ=0):
        # Object label
        self.label = label
        # Object itself: 
        self.obj = obj
        # Subshapes:
        self.children = []
        # Dimensions:
        self.dimX = dimX
        self.dimY = dimY
        self.dimZ = dimZ
        
    def addChild(self, obj):
        self.children.append(obj)
        
    def descendant(self, label):
        for child in self.children:
            if child.label == label:
                return child
    
    def getDimX(self):
        return self.dimX
    
    def getDimY(self):
        return self.dimY
    
    def getDimZ(self):
        return self.dimZ
    
    def getPolygon(self, index):
        return self.obj.data.polygons[index]
    
        
########################################################################

''' ------------------ FUNCTIONS: ------------------ '''

'''Creates initial 3D Mass (root node):'''

def create3DMass(label, width, depth, height):
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
    sizeRows = (width/2) / ((columns-1) / 2)
    sizeColumns = (height/2) / ((rows-1) / 2)

    # Looping to create the grid:
    verts = [vert(x, y, sizeRows, sizeColumns) for x in range(rows) for y in range(columns)]
    faces = [face(x, y, columns) for x in range(rows - 1) for y in range(columns - 1)]

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
    return mesh


########################################################################

''' ------------------ SIMULATING SELEX RULES: ------------------ '''

'''C1: Initial settings:'''

label = "building"
width = 9
depth = 11
height = 5


'''C2: {<> -> createShape("building", height, width, depth)};'''

mass3D = create3DMass(label, width, depth, height)

# Defining shape tree root node:
root = Node("root", None)

# Adding building mass node:
root.addChild(Node(label, mass3D, width, depth, height))

# Retrieving root node descendant by label:
building = root.descendant("building")

# Configuring object mode:
bpy.ops.object.mode_set(mode = "EDIT")
bpy.ops.mesh.select_all(action = "DESELECT")
bpy.ops.object.mode_set(mode = "OBJECT")

# Creating nodes with object faces:
front = Node(building.label + "_" + "front", building.getPolygon(3), building.getDimX(), 0, building.getDimZ())
left = Node(building.label + "_" + "left", building.getPolygon(0), building.getDimY(), 0, building.getDimZ())
right = Node(building.label + "_" + "right", building.getPolygon(2), building.getDimY(), 0, building.getDimZ())
back = Node(building.label + "_" + "back", building.getPolygon(1), building.getDimX(), 0, building.getDimZ())

# Adding front, back, left and right faces as children:
building.addChild(front)
building.addChild(left)
building.addChild(right)
building.addChild(back)

# Reseting object mode:
bpy.ops.object.mode_set(mode = "EDIT")
bpy.ops.mesh.select_all(action = "DESELECT")
bpy.ops.object.mode_set(mode = "OBJECT")


'''C3: {<[label=="building_front"]> 
       -> createGrid("facade", 4, 4)};'''
    
frontFace = building.descendant("building_front")

# Retrieving face dimensions:
faceWidth = frontFace.getDimX()
faceHeight = frontFace.getDimZ()

# DEBUG - Printing dimensions:
print(faceWidth, faceHeight)

# Defining number of rows and columns of the grid:
rows = 3
columns = 5

label = "facade"

# Using face dimensions to generate grid:
virtualShape = createGrid(label, int(faceWidth), int(faceHeight), rows, columns)

# Adding virtual shape as child of building_front:
frontFace.addChild(Node(label, virtualShape))

# Retriving object from shape tree:
facade = frontFace.descendant(label)

# Positioning virtual shape over appropriate face:

# Always rotate 90 degrees at x-axis:
bpy.context.object.rotation_euler[0] = 1.5708
bpy.context.object.rotation_euler[1] = 1.5708

# If it's 'front' or 'back' face, just update location at y-axis appropriately:

## Inverting the sign is needed for 'front' location:
bpy.context.object.location[1] = (-building.getDimY()) / 2

## For 'back' location:
# bpy.context.object.location[1] = building.getDimY() / 2

# If it's 'left' or 'right' face:

## Perform a rotation by 90 degrees at z-axis:
# bpy.context.object.rotation_euler[2] = 1.5708

## Inverting the sign is needed for 'left' location:
# bpy.context.object.location[0] = (-building.getDimX()) / 2

## For 'right' location:
# bpy.context.object.location[0] = building.getDimX() / 2

'''C4: {<descendant()[label=="building"] / 
                     [label=="building_front"] / 
                     [label=="facade"] / 
                     [type=="cell"] 
                     [rowIdx in (3, 4)] 
                     [colIdx in (1, 2)> 
                     -> pull()};'''

# Experimental selection by face index:

## Changing object mode:
# bpy.ops.object.mode_set(mode = 'OBJECT')

## Deselect everything:
# bpy.ops.object.mode_set(mode = 'EDIT')
# bpy.ops.mesh.select_all(action = 'DESELECT')

# bpy.ops.object.mode_set(mode = 'OBJECT')

## Selecting faces of the object by it's index:
# bpy.data.objects['facade'].data.polygons[10].select = True
# bpy.data.objects['facade'].data.polygons[11].select = True
# bpy.data.objects['facade'].data.polygons[15].select = True
# bpy.data.objects['facade'].data.polygons[16].select = True

# bpy.ops.object.mode_set(mode = 'EDIT')

# Selection by rows and columns indexes:

## Selection settings:
rowsIndex = [2, 3]
columnsIndex = [1, 2]
label = "facade"

## Finding row and column grid indexes for a specific cell (its polygon index):

# idxRow = (cellIndex / columns) + 1
# idxColumn = (cellIndex / rows) + 1

## Finding cells corresponding to 'rowsIndex' and 'columnsIndex':

# (columns * rowIndex) - columns + (columnIndex - 1)

# Used to store the conversion from row and column indexes to face index:
selectedCells = []

for rowIndex in rowsIndex:
    for columnIndex in columnsIndex:
        cellIndex = (columns * rowIndex) - columns + (columnIndex - 1)
        selectedCells.append(cellIndex)

# DEBUG: Printing selected indexes:      
print(selectedCells)

# Changing object mode:
bpy.ops.object.mode_set(mode = 'OBJECT')

## Deselect everything:
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_all(action = 'DESELECT')

bpy.ops.object.mode_set(mode = 'OBJECT')

# Looping through selectedCells in order to select each one:
for cell in selectedCells:
    # DEBUG: Printing selected cells:
    print("Selecting: ", cell)
    
    # Setting each cell status to selected:
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.data.objects[label].data.polygons[cell].select = True
    bpy.ops.object.mode_set(mode = 'EDIT')
        
