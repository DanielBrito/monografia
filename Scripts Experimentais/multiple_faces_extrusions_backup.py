import os
import bpy
import math

''' ------------------ DATA STRUCTURE: ------------------ '''

class Node(object):
    # CONSTRUCTOR:
    
    # Attributes 'label', 'object', 'type' and 'parent' are required for every node:
    def __init__(self, label, object, parent, type, dimX=0, dimY=0, dimZ=0, rows=0, columns=0):
        # ATTRIBUTES:
        
        # Object label:
        self.label = label
        
        # Object reference: 
        self.obj = object
        
        # Parent shape:
        self.parent = parent
        
        # Virtual or construction shape:
        self.type = type
        
        # Subshapes:
        self.children = []
        
        # Dimensions for construction shapes:
        self.dimX = dimX
        self.dimY = dimY
        self.dimZ = dimZ
        
        # Number of rows and columns for virtual shapes:
        self.rows = rows-1
        self.columns = columns-1
        
    # METHODS:
        
    ## Shape tree:
    
    def addChild(self, object):
        self.children.append(object)
        
    def descendant(self, label):
        for child in self.children:
            if child.label == label:
                return child
    
    ## Getters:
    
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
    
    def getIndex(self):
        return self.obj.index
    
    def getDimX(self):
        return self.dimX
    
    def getDimY(self):
        return self.dimY
    
    def getDimZ(self):
        return self.dimZ
    
    def getRows(self):
        return self.rows
    
    def getColumns(self):
        return self.columns
    
    ## Utilitary functions:
    
    def printChildren(self):
        for child in self.children:
            print(child.label)
        
        
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
    # Creating a single vert:
    return (x * sizeColumns, y * sizeRows, 0)

def face(x, y, rows):
    # Creating a single face:
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

    # Creating mesh datablock:
    mesh = bpy.data.meshes.new(label)
    mesh.from_pydata(verts, [], faces)

    # Creating object and link to scene:
    grid = bpy.data.objects.new(label, mesh)
    bpy.context.scene.collection.objects.link(grid)

    # Selecting the object:
    bpy.context.view_layer.objects.active = grid
    bpy.data.objects[label].select_set(True)

    # Moving object origin to its center:
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

    # Moving 3D cursor to scene origin:
    bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)

    # Moving shape origin to scene origin: 
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            override = bpy.context.copy()
            override['area'] = area
            override['region'] = area.regions[4]
            bpy.ops.view3d.snap_selected_to_cursor(override, use_offset=False)
    
    bpy.data.objects[label].select_set(False)
    
    # Adding virtual shape as child of side:
    side.addChild(Node(label, mesh, side, "virtual", width, 0, height, rows, columns))
    
    return mesh


''' Creating mass model and updating shape tree: '''

def createShape(root, label, width, depth, height):
    # Creating and retrieving mass model:
    mass3D = create3DMass(label, width, depth, height)

    # Adding building mass node to shape tree:
    root.addChild(Node(label, mass3D, root, "construction", width, depth, height))

    # Retrieving root node descendant by label:
    building = root.descendant(label)

    # Configuring object mode:
    bpy.ops.object.mode_set(mode = "EDIT")
    bpy.ops.mesh.select_all(action = "DESELECT")
    bpy.ops.object.mode_set(mode = "OBJECT")

    # Creating nodes with object faces:
    front = Node(building.label + "_" + "front", building.getPolygon(3), building, "construction", width, 0, height)
    left = Node(building.label + "_" + "left", building.getPolygon(0), building, "construction", depth, 0, height)
    right = Node(building.label + "_" + "right", building.getPolygon(2), building, "construction", depth, 0, height)
    back = Node(building.label + "_" + "back", building.getPolygon(1), building, "construction", width, 0, height)

    # Adding front, back, left and right faces as children of 'building':
    building.addChild(front)
    building.addChild(left)
    building.addChild(right)
    building.addChild(back)

    # Reseting object mode:
    bpy.ops.object.mode_set(mode = "EDIT")
    bpy.ops.mesh.select_all(action = "DESELECT")
    bpy.ops.object.mode_set(mode = "OBJECT")
   

''' Selecting node by its label from shape tree: '''

def selectNode(root, labels):
    currentNode = root
    child = None
    
    for label in labels:
        child = currentNode.descendant(label)
        currentNode = child
        
    return child


''' Positioning main virtual shape over proper model side: '''

def placeMainVirtualShape(side, virtualShape):
    # Always rotate 90 degrees at y-axis:
    bpy.context.object.rotation_euler[1] = 1.5708
    
    if "front" in side.getLabel():
        # Rotating properly at z-axis (90 deg):
        bpy.context.object.rotation_euler[0] = 1.5708
        
        # Positioning virtual shape over the proper side at y-axis:
        bpy.context.object.location[1] = -side.getParent().getDimY() / 2
        
    elif "back" in side.getLabel():    
        # Rotating properly at z-axis (-90 deg):
        bpy.context.object.rotation_euler[0] = -1.5708
        
        # Positioning virtual shape over the proper side at y-axis:
        bpy.context.object.location[1] = side.getParent().getDimY() / 2
        
    elif "left" in side.getLabel():
        # Rotating properly at z-axis (180 deg):
        bpy.context.object.rotation_euler[2] = 3.14159
        
        # Positioning virtual shape over the proper side at y-axis:
        bpy.context.object.location[0] = -side.getParent().getDimX() / 2
    
    elif "right" in side.getLabel():        
        # Positioning virtual shape over the proper side at y-axis:
        bpy.context.object.location[0] = side.getParent().getDimX() / 2
        
        
''' Selecting cells from virtual shape to apply extrusion: '''

def selectToBeVolume(grid, rows, columns, rowsIndex, columnsIndex):
    # Setting grid as active object inside the scene:
    bpy.context.view_layer.objects.active = bpy.data.objects[grid.getLabel()]
    
    # Used to store the conversion from row and column indexes to face index:
    selectCells = []

    for rowIndex in rowsIndex:
        for columnIndex in columnsIndex:
            cellIndex = (columns * rowIndex) - columns + (columnIndex - 1)
            selectCells.append(cellIndex)

    # DEBUG - Printing selected indexes:      
    ## print("GRID CELLS: ", selectCells)

    # Changing object mode:
    bpy.ops.object.mode_set(mode = 'OBJECT')

    ## Deselecting everything:
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action = 'DESELECT')

    bpy.ops.object.mode_set(mode = 'OBJECT')

    # Looping through 'selectedCells' in order to select each one:
    for cell in selectCells:    
        # Setting each cell select status to True:
        bpy.ops.object.mode_set(mode = 'OBJECT')  
        bpy.data.objects[grid.getLabel()].data.polygons[cell].select = True
        bpy.ops.object.mode_set(mode = 'EDIT')
            
    # Changing select mode:
    bpy.ops.mesh.select_mode(type='FACE')
    

''' Extruding selected region: '''

def addVolume(label, parent, extrusionSize, sidesLabels, gridLabel):
    # Grouping selected cells into a region to be extruded, and storing created subgrid:
    subgrid = groupRegions(label, parent, gridLabel)
    
    grandparent = parent.getParent()
    
    # Changing object mode:
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.mode_set(mode = 'EDIT')

    # Selecting last polygon by its index:
    regionIndex = len(grandparent.obj.data.polygons)-1

    # DEBUG - Printing last polygon index:
    ## print("REGION INDEX: ", regionIndex)

    # Updating selection:
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.ops.object.mode_set(mode = 'OBJECT')

    # Selecting faces of the object by it's index:
    bpy.data.objects[grandparent.getLabel()].data.polygons[regionIndex].select = True

    # Updating selection mode:
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_mode(type = 'FACE')
    
    # Performing extrusion:
    
    if "front" in parent.getLabel():
        ## Inverting the sinal for 'front' extrusions (y-axis):
        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, -extrusionSize, 0)})
        
    elif "left" in parent.getLabel():
        ## Inverting the sinal for 'left' extrusions (x-axis):
        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(-extrusionSize, 0, 0)})
        
    elif "right" in parent.getLabel():
        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(extrusionSize, 0, 0)})
        
    elif "back" in parent.getLabel():
        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(0, extrusionSize, 0)})

    ## Changing object mode:
    bpy.ops.mesh.select_all(action = 'DESELECT')
    bpy.ops.object.mode_set(mode = 'OBJECT')
    
    # Updating shape tree:
    
    ## Retrieving extruded front face:
    regionFrontMesh = bpy.data.objects[grandparent.getLabel()].data.polygons[regionIndex+1]
    
    ## Adding front face as child of parent:
    parent.addChild(Node(sidesLabels[0], regionFrontMesh, parent, "construction"))
    
    ## Retrieving front face node:
    regionFront = parent.descendant(sidesLabels[0])
    
    ## Adding virtual grid as child of front face:
    regionFront.addChild(Node(subgrid.name, subgrid, regionFront, "virtual"))
    
    # Updating 'subgrid' position:
    ## TO-DO


''' Function to group selected cells: '''

def groupRegions(label, parent, gridLabel):
    # Separating selected subgrid by creating a new object:
    bpy.ops.mesh.separate(type='SELECTED')
    
    bpy.data.objects[gridLabel + ".001"].select_set(False)
    
    print("LABEL: ", label)
    print("PARENT: ", parent.getLabel())
    print("GRID LABEL: ", gridLabel)
    
    grandparent = parent.getParent()
    
    # Deleting obsolete object (main_front_grid_copy):  
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    
    bpy.context.view_layer.objects.active = bpy.data.objects[gridLabel]
    bpy.data.objects[gridLabel].select_set(True)
    
    bpy.ops.object.delete()
    
    # Storing reference to region (to be used for extrusion from building):
    region = bpy.data.objects[gridLabel + ".001"]
    
    # Changing name attribute to label:
    region.name = label

    # Setting region as active object inside the scene:
    bpy.data.objects[label].select_set(True)
    bpy.context.view_layer.objects.active = bpy.data.objects[label]
    
    # Setting object mode to fix poll error:
    bpy.ops.object.mode_set(mode = 'OBJECT')
    
    # Adding created region as child of parent:
    parent.addChild(Node(label, region, parent, "construction"))

    # Moving object's origin to its center:
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

    # Creating unliked copy to be used as virtual shape of 'region':
    bpy.ops.object.duplicate()
    
    # Renaming virtual shape appropriately:
    regionGrid = bpy.data.objects[label + ".001"]

    # Renaming virtual shape:
    regionGrid.name = label + "_front_grid"

    # Retrieving 'region' node:
    region = parent.descendant(label) 

    # Deselecting object:
    bpy.data.objects[region.getLabel()].select_set(False)
    bpy.data.objects[regionGrid.name].select_set(False)
    
    # Selecting object as active to dissolve internal edges:
    bpy.context.view_layer.objects.active = bpy.data.objects[label]
    bpy.data.objects[label].select_set(True)

    # Changing object mode:
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.mode_set(mode = 'EDIT')

    # Selecting all the faces:
    bpy.ops.mesh.select_all(action = 'SELECT')

    # Changing object mode:
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.ops.object.mode_set(mode = 'EDIT')

    # Selecting boundary edges:
    bpy.ops.mesh.region_to_loop()

    bpy.ops.object.mode_set(mode = 'OBJECT')

    # Creating list with all of the object indexes:
    ids = list(range(len(region.getEdges())))

    # DEBUG - Printing all of the edges indexes:
    ## print("ALL EDGES INDEXES: ", ids)

    # Storing just the selected indexes:
    selectedEdges = [e.index for e in region.getEdges() if e.select]

    # DEBUG - Printing border indexes:
    ## print("BORDER EDGES INDEXES: ", selectedEdges)

    # Removing border indexes, so the remaining will be internal:
    for e in selectedEdges:
        ids.remove(e)
  
    # DEBUG - Printing internal indexes:
    ## print("INTERNAL EDGES INDEXES: ", ids)

    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.select_all(action = 'DESELECT')

    bpy.ops.object.mode_set(mode = 'OBJECT')
    
    # Selecting internal edges by index:
    for id in ids:
        bpy.data.objects[label].data.edges[id].select = True
        
    bpy.ops.object.mode_set(mode = 'EDIT')

    # Dissolving internal edges:
    bpy.ops.mesh.dissolve_edges()
    
    # Switching to object mode:
    bpy.ops.object.mode_set(mode = 'OBJECT')
    
    # Selecting region as source for the join operation:
    bpy.data.objects[label].select_set(True)
    
    # Selecting first object of the scene as target for the join operation:
    bpy.context.view_layer.objects.active = bpy.data.objects[grandparent.getLabel()]
    bpy.data.objects[grandparent.getLabel()].select_set(True)

    # Joining selected objects ('region' will be merged into 'grandparent'):
    bpy.ops.object.join()
    
    deselectIndex = bpy.data.objects[grandparent.getLabel()].pass_index
    
    # Deselecting objects to avoid bugs:
    bpy.data.objects[grandparent.getLabel()].select_set(False)
    bpy.data.objects[deselectIndex].select_set(False)
    
    # Returning grid to be added as '_grid' child of 'region_front':
    return regionGrid
    

''' Utilitary function to copy a given shape from its label: '''

def duplicateShape(originalShapeLabel):
    # Setting region as active object inside the scene:
    bpy.context.view_layer.objects.active = bpy.data.objects[originalShapeLabel]
    bpy.data.objects[originalShapeLabel].select_set(True)
    
    # Changing to object mode:
    bpy.ops.object.mode_set(mode = "OBJECT")

    # Moving object's origin to its center:
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

    # Creating unliked copy to be used as virtual shape of 'region':
    bpy.ops.object.duplicate()
    
    # Renaming virtual shape appropriately:
    shapeCopy = bpy.data.objects[originalShapeLabel + ".001"]

    # Renaming virtual shape:
    shapeCopy.name = originalShapeLabel + "_copy"
    
    return shapeCopy
    
    
########################################################################

''' ---------------------- RESETING THE SCENE: ---------------------- '''
    
if len(bpy.context.scene.objects) > 0:
    bpy.ops.object.mode_set(mode = "OBJECT")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    
    # Cleaning debugging logs:
    os.system("clear")

########################################################################

''' --------- SIMULATING SELEX RULES (multiple_faces_extrusions.slx): --------- '''

# Defining shape tree root node:
root = Node("root", None, None, None)

# Simulating list traversal and rules execution:

# Default rule for defining mass model characteristics:
''' #C1 '''

# TESTING -> Simulating data for initial settings:
label = "building"
width = 9
depth = 11
height = 5


# Default rule for creating mass model:
''' #C2 '''

createShape(root, label, width, depth, height)


# Executing transformation and deformation rules:

''' < BEGIN FOR LOOP > '''

''' for index range(2, len(rules)): '''

''' #C3, #C4, #C5, ... '''

# Splitting rule into 'selection' (<labels>) and 'action' (after ->):
## selexAction = rules[index].split(' -> ')

# Retrieving selection rules from 'selexAction':
## selection = selexAction[0]

# Retrieving actions from 'selexAction':
## action = selexActions[1]

# -------------------------------------------------------------------------------

# Checking if actions has 'addVolume' OR 'createGrid' / 'roundShape':
## if "addVolume" in action OR if "createdGrid" or "roundShape" in actions

# 1) If the action is related to 'createGrid' or 'roundShape' perform split:

# 1.1) If the rule contains 'createGrid':

## Retrieving labels from 'selection':
### labels = selection.split('"')[1::2];

# TESTING 1 -> Simulating data for generated list of labels:
labels_front = ["building", "building_front"]

## Passing labels to function responsible for selecting the object from shape tree:
side = selectNode(root, labels_front)

# TESTING -> Simulating data for label and number of rows/columns:
label = "main_front_grid"
rows = 3
columns = 6

virtualShape = createGrid(label, side, rows, columns)

placeMainVirtualShape(side, virtualShape)

# -------------------------------------------------------------------------------

# TESTING 2 -> Simulating data for generated list of labels:
labels_left = ["building", "building_left"]

## Passing labels to function responsible for selecting the object from shape tree:
side = selectNode(root, labels_left)

# TESTING -> Simulating data for label and number of rows/columns:
label = "main_left_grid"
rows = 2
columns = 5

virtualShape = createGrid(label, side, rows, columns)

placeMainVirtualShape(side, virtualShape)

# -------------------------------------------------------------------------------

# TESTING 3 -> Simulating data for generated list of labels:
labels_right = ["building", "building_right"]

## Passing labels to function responsible for selecting the object from shape tree:
side = selectNode(root, labels_right)

# TESTING -> Simulating data for label and number of rows/columns:
label = "main_right_grid"
rows = 3
columns = 3

virtualShape = createGrid(label, side, rows, columns)

placeMainVirtualShape(side, virtualShape)

# -------------------------------------------------------------------------------

# TESTING 4 -> Simulating data for generated list of labels:
labels_back = ["building", "building_back"]

## Passing labels to function responsible for selecting the object from shape tree:
side = selectNode(root, labels_back)

# TESTING -> Simulating data for label and number of rows/columns:
label = "main_back_grid"
rows = 5
columns = 4

virtualShape = createGrid(label, side, rows, columns)

placeMainVirtualShape(side, virtualShape)

# -------------------------------------------------------------------------------

# 2) If the action is related to 'addVolume' perform split and also store rows/columns:

## Retrieving labels from 'selection' example:
### labels = selection.split('"')[1::2];


# -------------------------------------------------------------------------------
# FRONT
# -------------------------------------------------------------------------------

# TESTING 1 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_front", "main_front_grid"]
rowsIndex = [3]
columnsIndex = [1, 2]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "entrance_sm"
parent = gridCopyNode.getParent()
extrusionSize = 1
sidesLabels = [label + "_front", label + "_left", label + "_right"]

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model:
addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)

# -------------------------------------------------------------------------------

# TESTING 2 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_front", "main_front_grid"]
rowsIndex = [2, 3]
columnsIndex = [3, 4]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "entrance_md"
parent = gridCopyNode.getParent()
extrusionSize = 2
sidesLabels = [label + "_front", label + "_left", label + "_right"]

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model:
addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)

# -------------------------------------------------------------------------------

# TESTING 3 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_front", "main_front_grid"]
rowsIndex = [1, 2, 3]
columnsIndex = [5, 6]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "entrance_lg"
parent = gridCopyNode.getParent()
extrusionSize = 3
sidesLabels = [label + "_front", label + "_left", label + "_right"]

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model:
addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)


# -------------------------------------------------------------------------------
# BACK
# -------------------------------------------------------------------------------

# TESTING 1 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_back", "main_back_grid"]
rowsIndex = [1, 2, 3, 4, 5]
columnsIndex = [1, 2]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "garden_lg"
parent = gridCopyNode.getParent()
extrusionSize = 2
sidesLabels = [label + "_front", label + "_left", label + "_right"]

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model:
addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)

# -------------------------------------------------------------------------------

# TESTING 2 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_back", "main_back_grid"]
rowsIndex = [4, 5]
columnsIndex = [3, 4]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "garden_sm"
parent = gridCopyNode.getParent()
extrusionSize = 2
sidesLabels = [label + "_front", label + "_left", label + "_right"]

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model:
addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)


# -------------------------------------------------------------------------------
# LEFT
# -------------------------------------------------------------------------------

# TESTING 1 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_left", "main_left_grid"]
rowsIndex = [2]
columnsIndex = [1, 2]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "reception_employees"
parent = gridCopyNode.getParent()
extrusionSize = 3
sidesLabels = [label + "_front", label + "_left", label + "_right"]

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model:
addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)

# -------------------------------------------------------------------------------

# TESTING 2 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_left", "main_left_grid"]
rowsIndex = [2]
columnsIndex = [4, 5]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "reception_visitors"
parent = gridCopyNode.getParent()
extrusionSize = 2
sidesLabels = [label + "_front", label + "_left", label + "_right"]

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model:
addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)


# -------------------------------------------------------------------------------
# RIGHT
# -------------------------------------------------------------------------------

# TESTING 1 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_right", "main_right_grid"]
rowsIndex = [2, 3]
columnsIndex = [1, 2, 3]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "garden"
parent = gridCopyNode.getParent()
extrusionSize = 2
sidesLabels = [label + "_front", label + "_left", label + "_right"]

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model:
addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)
  
''' </ END FOR LOOP > '''