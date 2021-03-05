import bpy
import math

''' ------------------ DATA STRUCTURE: ------------------ '''

class Node(object):
    # CONSTRUCTOR:
    
    # Attributes 'label', 'object' and parent are required for every node:
    def __init__(self, label, object, parent, dimX=0, dimY=0, dimZ=0):
        # ATTRIBUTES:
        
        # Object label:
        self.label = label
        
        # Object itself: 
        self.obj = object
        
        # Parent shape:
        self.parent = parent
        
        # Subshapes:
        self.children = []
        
        # Dimensions:
        self.dimX = dimX
        self.dimY = dimY
        self.dimZ = dimZ
        
    # METHODS:
        
    def addChild(self, object):
        self.children.append(object)
        
    def descendant(self, label):
        for child in self.children:
            if child.label == label:
                return child
    
    def getLabel(self):
        return self.label
    
    def getChildren(self):
        return self.children
    
    def getParent(self):
        return self.parent
    
    def getPolygon(self, index):
        return self.obj.data.polygons[index]
    
    def getEdges(self):
        return self.obj.data.edges
    
    def getCenter(self):
        return self.center
    
    # Necessary?
    def getDimX(self):
        return self.dimX
    
    # Necessary?
    def getDimY(self):
        return self.dimY
    
    # Necessary?
    def getDimZ(self):
        return self.dimZ
        
########################################################################

''' ------------------ FUNCTIONS: ------------------ '''

''' Creating initial 3D mass: '''

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


''' Utility functions for grid generation: '''

def vert(x, y, sizeRows, sizeColumns):
    # Create a single vert:
    return (x * sizeColumns, y * sizeRows, 0)

def face(x, y, rows):
    # Create a single face:
    return (x * rows + y,
           (x + 1) * rows + y,
           (x + 1) * rows + 1 + y,
           x * rows + 1 + y)


''' Creating virtual shape and updating shape tree: '''

def createGrid(label, side, rows, columns):
    # Retrieving side dimensions:
    width = side.getDimX()
    height = side.getDimZ()

    # DEBUG - Printing dimensions:
    ## print("FACE DIMENSIONS: ", width, height)
    
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
    grid = bpy.data.objects.new(label, mesh)
    bpy.context.scene.collection.objects.link(grid)

    # Select the object:
    bpy.context.view_layer.objects.active = grid
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
    
    # Adding virtual shape as child of side:
    side.addChild(Node(label, mesh, side, width, 0, height))
    
    return mesh


''' Creating mass model and updating shape tree: '''

def createShape(root, label, width, depth, height):
    # Creating and retrieving mass model:
    mass3D = create3DMass(label, width, depth, height)

    # Adding building mass node to shape tree:
    root.addChild(Node(label, mass3D, root, width, depth, height))

    # Retrieving root node descendant by label:
    building = root.descendant(label)

    # Configuring object mode:
    bpy.ops.object.mode_set(mode = "EDIT")
    bpy.ops.mesh.select_all(action = "DESELECT")
    bpy.ops.object.mode_set(mode = "OBJECT")

    # Creating nodes with object faces:
    front = Node(building.label + "_" + "front", building.getPolygon(3), building, width, 0, height)
    left = Node(building.label + "_" + "left", building.getPolygon(0), building, depth, 0, height)
    right = Node(building.label + "_" + "right", building.getPolygon(2), building, depth, 0, height)
    back = Node(building.label + "_" + "back", building.getPolygon(1), building, width, 0, height)

    # Adding front, back, left and right faces as children of 'building':
    building.addChild(front)
    building.addChild(left)
    building.addChild(right)
    building.addChild(back)

    # Reseting object mode:
    bpy.ops.object.mode_set(mode = "EDIT")
    bpy.ops.mesh.select_all(action = "DESELECT")
    bpy.ops.object.mode_set(mode = "OBJECT")
   

''' Selecting object side in order to add virtual shape: '''
def selectToBeGrid(root, labels):
    currentNode = root
    child = None
    
    for label in labels:
        child = currentNode.descendant(label)
        currentNode = child
        
    return child


''' Selecting virtual shape cells in order to apply extrusion: '''
def selectToBeVolume(root, labels, rows, columns):
    return None


''' Positioning virtual shape over proper model side: '''
def placeVirtualShape():
    return None
        
########################################################################

''' ---------------------- RESETING THE SCENE: ---------------------- '''
    
if len(bpy.context.scene.objects) > 0:
    bpy.ops.object.mode_set(mode = "OBJECT")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

########################################################################

''' -------------- SIMULATING SELEX RULES (experiment.slx): -------------- '''

# Defining shape tree root node:
root = Node("root", None, None)

# TESTING -> Simulating generated list after reading the file:

rules = []

# rule[0]:
rules.append("label = 'building'; width = 9; depth = 11; height = 5;")

# rule[1]:
rules.append("{<> -> createShape('building', 5, 9, 11)};")

# rule[2]:
rules.append("{< descendant() [label=='building'] / [label=='building_front'] > -> createGrid(label, rows, columns)};")

# rule[3]:
rules.append("{< descendant() [label=='building'] / [label=='building_front'] / [label=='facade'] / [type=='cell'] [rowIdx in (2, 3)] [colIdx in (1, 2) > -> addVolume('entrance', 'building_front', 2.5, ['entrance_front', 'entrance_left', 'entrance_right'])};")

# rule[4]:
rules.append("{< descendant() <descendant() [label=='building'] / [label=='building_front'] / [label=='entrance'] / [label=='entrance_front'] > -> roundShape('front', 1.0, 30, 'vertical')};")


# Simulating list traversal and rules execution:

# Default rule for defining mass model characteristics:
''' #C1 -> rules[0] '''

# TESTING -> Simulating data for initial settings:
label = "building"
width = 9
depth = 11
height = 5


# Default rule for creating mass model:
''' #C2 -> rules[1] '''

createShape(root, label, width, depth, height)


# Executing transformation and deformation rules:

''' < BEGIN FOR LOOP > '''

''' for index range(2, len(rules)): '''

''' #C3 -> rules[2] '''

# Splitting rule into 'selection' (<labels>) and 'action' (after ->):
## selexAction = rules[index].split(' -> ')

# Retrieving selection rules from 'selexAction':
## selection = selexAction[0]

# Retrieving actions from 'selexAction':
## action = selexActions[1]

# Checking if actions has 'addVolume' OR 'createGrid' / 'roundShape':
## if "addVolume" in action OR if "createdGrid" or "roundShape" in actions

# a) If the action is related to 'createGrid' or 'roundShape' perform split:

## Retrieving labels from 'selection':
### labels = selection.split('"')[1::2];

# TESTING -> Simulating data for generated list of labels:
labels = ["building", "building_front"]

## Passing labels to function responsible for selecting the object from shape tree:
side = selectToBeGrid(root, labels)

# TESTING -> Simulating data for label and number of rows/columns:
label = "facade"
rows = 3
columns = 4

virtualShape = createGrid(label, side, rows, columns)

placeVirtualShape(side, virtualShape)

# b) If the action is related to 'addVolume' perform split and also store rows/columns:

## Retrieving labels from 'selection':
### labels = selection.split('"')[1::2];

## Retrieving rows and columns indexes:
### TO-DO

# Example: selectToBeVolume(root, labels, rows, columns)
                 
''' </ END FOR LOOP > '''