import bpy
import math

''' ------------------ DATA STRUCTURES: ------------------ '''

class Node(object):
    # Attributes 'label' and 'object' are required for every node:
    def __init__(self, label, object, dimX=0, dimY=0, dimZ=0):
        # Object label
        self.label = label
        # Object itself: 
        self.obj = object
        # Subshapes:
        self.children = []
        # Dimensions:
        self.dimX = dimX
        self.dimY = dimY
        self.dimZ = dimZ
        
    def addChild(self, object):
        self.children.append(object)
        
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
    
    def getEdges(self):
        return self.obj.data.edges
        
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

'''Round shape:'''

def roundShape(object, side, degree, segments, axis=""):
    center = object.center
    
    # DEBUG: Printing center coordinate of the face:
    print("CENTER COORDINATE = ", center)
    
    # Retrieving vertices of the face:    
    verts = object.vertices

    # Selecting vertices of the face:
    for v in verts:
        # DEBUG:
        # print("VERT: ", v)
        bpy.context.active_object.data.vertices[v].select = True
        
    # Storing selected vertexes form object:
    selectedVerts = [v for v in bpy.context.active_object.data.vertices if v.select]
    
    # Deselecting vertices:
    for v in verts:
        bpy.context.active_object.data.vertices[v].select = False

    # DEBUG: Printing coordinates of the selected vertexes:
    # for v in selectedVerts:
    #     print("vertex index = ", v.index)
    #     print("vertex coordinate = ", v.co)
        
    x, y, z = 0, 1, 2
    
    # Round left:
    if side == "left":
        # DEBUG:
        print("ROUND LEFT")
            
        for v in selectedVerts:
            # DEBUG:
            # print(v.co, center)
                        
            # Checking for upper left vertex:
            if v.co[x] < center[x] and v.co[z] > center[z]:
                print("selecting vertex = ", v.index)
                bpy.context.active_object.data.vertices[v.index].select = True
                
            # Checking for bottom left vertex:
            if v.co[x] < center[x] and v.co[z] < center[z]:
                print("selecting vertex = ", v.index)
                bpy.context.active_object.data.vertices[v.index].select = True
        
        # Changing object mode:
        bpy.ops.object.mode_set(mode = 'EDIT')  
        bpy.ops.mesh.select_mode(type="VERT")
        
        # Applying deformation:              
        bpy.ops.mesh.bevel(offset=degree, offset_pct=0, segments=segments, vertex_only=False)
        
        bpy.ops.object.mode_set(mode = 'OBJECT')
         
    # Round right:       
    if side == "right":
        # DEBUG:
        print("ROUND RIGHT")
            
        for v in selectedVerts:
            # DEBUG:
            # print(v.co, center)
                        
            # Checking for upper right vertex:
            if v.co[x] > center[x] and v.co[z] > center[z]:
                print("selecting vertex = ", v.index)
                bpy.context.active_object.data.vertices[v.index].select = True
                
            # Checking for bottom right vertex:
            if v.co[x] > center[x] and v.co[z] < center[z]:
                print("selecting vertex = ", v.index)
                bpy.context.active_object.data.vertices[v.index].select = True

        # Changing object mode:
        bpy.ops.object.mode_set(mode = 'EDIT')  
        bpy.ops.mesh.select_mode(type="VERT")
        
        # Applying deformation:
        bpy.ops.mesh.bevel(offset=degree, offset_pct=0, segments=segments, vertex_only=False)
        
        bpy.ops.object.mode_set(mode = 'OBJECT')
    
    # Round top:
    if side == "top":
        # DEBUG:
        print("ROUND TOP")
            
        for v in selectedVerts:
            # DEBUG:
            # print(v.co, center)
                        
            # Checking for upper right vertex:
            if v.co[x] < center[x] and v.co[z] > center[z]:
                print("selecting vertex = ", v.index)
                bpy.context.active_object.data.vertices[v.index].select = True
                
            # Checking for bottom right vertex:
            if v.co[x] > center[x] and v.co[z] > center[z]:
                print("selecting vertex = ", v.index)
                bpy.context.active_object.data.vertices[v.index].select = True

        # Changing object mode:
        bpy.ops.object.mode_set(mode = 'EDIT')  
        bpy.ops.mesh.select_mode(type="VERT")
        
        # Applying deformation:
        bpy.ops.mesh.bevel(offset=degree, offset_pct=0, segments=segments, vertex_only=False)
        
        bpy.ops.object.mode_set(mode = 'OBJECT')
     
    # Round bottom:   
    if side == "bottom":
        # DEBUG:
        print("ROUND BOTTOM")
            
        for v in selectedVerts:
            # DEBUG:
            # print(v.co, center)
                        
            # Checking for upper right vertex:
            if v.co[x] < center[x] and v.co[z] < center[z]:
                print("selecting vertex = ", v.index)
                bpy.context.active_object.data.vertices[v.index].select = True
                
            # Checking for bottom right vertex:
            if v.co[x] > center[x] and v.co[z] < center[z]:
                print("selecting vertex = ", v.index)
                bpy.context.active_object.data.vertices[v.index].select = True

        # Changing object mode:
        bpy.ops.object.mode_set(mode = 'EDIT')  
        bpy.ops.mesh.select_mode(type="VERT")
        
        # Applying deformation:
        bpy.ops.mesh.bevel(offset=degree, offset_pct=0, segments=segments, vertex_only=False)
        
        bpy.ops.object.mode_set(mode = 'OBJECT')

    # Performing a mix of round left and right, but with edges:
    if side == "front" and axis == "vertical":
        # DEBUG:
        print("ROUND FRONT VERTICAL")
        
        leftEdgeIndex, rightEdgeIndex = 0, 0
        vertexA, vertexB = None, None
        
        # Searching for left edge:
        for v in selectedVerts:
            # DEGUG:
            # print("VERT: ", v.index, v.co)
                        
            # Checking for upper left vertex:
            if v.co[x] < center[x] and v.co[z] > center[z] and round(v.co[y]) == round(center[y]):
                print("selecting upper left vertex = ", v.index)
                vertexA = bpy.context.active_object.data.vertices[v.index]
                
            # Checking for bottom left vertex:
            if v.co[x] < center[x] and v.co[z] < center[z] and round(v.co[y]) == round(center[y]):
                print("selecting bottom left vertex = ", v.index)
                vertexB = bpy.context.active_object.data.vertices[v.index]
                
        bpy.ops.object.mode_set(mode = 'EDIT')
        
        if vertexA == None or vertexB ==None:
            # DEBUG: Checking if the vertex were found:
            print("NONE: ", vertexA, vertexB)
            return
        
        for e in bpy.context.active_object.data.edges:
            # DEGUG: Printing edge keys:
            # print("left edge keys: ", e.vertices[0], e.vertices[1])
            
            # Storing edge index:
            if (e.vertices[0] == vertexA.index and e.vertices[1] == vertexB.index) or (e.vertices[0] == vertexB.index and e.vertices[1] == vertexA.index):
                print("left edge: ", e.index)
                leftEdgeIndex = e.index
                
        # Searching for right edge:
        for v in selectedVerts:
            # DEGUG:
            # print(v.co, center)
                        
            # Checking for upper right vertex:
            if v.co[x] > center[x] and v.co[z] > center[z] and round(v.co[y]) == round(center[y]):
                print("selecting upper right vertex = ", v.index)
                vertexA = bpy.context.active_object.data.vertices[v.index]
                
            # Checking for bottom right vertex:
            if v.co[x] > center[x] and v.co[z] < center[z] and round(v.co[y]) == round(center[y]):
                print("selecting bottom right vertex = ", v.index)
                vertexB = bpy.context.active_object.data.vertices[v.index]
                
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_mode(type="EDGE")
        
        for e in bpy.context.active_object.data.edges:
            # DEGUG: Printing edge keys:
            # print("right edge keys: ", e.vertices[0], e.vertices[1])

            # Storing edge index:
            if (e.vertices[0] == vertexA.index and e.vertices[1] == vertexB.index) or (e.vertices[0] == vertexB.index and e.vertices[1] == vertexA.index):
                print("right edge: ", e.index)
                rightEdgeIndex = e.index
                
        # Selecting edges:
        bpy.ops.object.mode_set(mode = 'OBJECT')

        # Selecting internal edges:
        bpy.context.active_object.data.edges[leftEdgeIndex].select = True
        bpy.context.active_object.data.edges[rightEdgeIndex].select = True
        
        # Applying deformation:
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.bevel(offset=degree, offset_pct=0, segments=segments, vertex_only=False)
        
        bpy.ops.object.mode_set(mode = 'OBJECT')
        
    # Performing a mix of round top and bottom, but with edges:
    if side == "front" and axis == "horizontal":
        # DEBUG:
        print("ROUND FRONT HORIZONTAL")
        
        topEdgeIndex, bottomEdgeIndex = 0, 0
        vertexA, vertexB = None, None
        
        # Searching for top edge:
        for v in selectedVerts:
            # DEGUG:
            # print(v.co, center)
                        
            # Checking for upper left vertex:
            if v.co[x] < center[x] and v.co[z] > center[z] and round(v.co[y]) == round(center[y]):
                print("selecting upper left vertex = ", v.index)
                vertexA = bpy.context.active_object.data.vertices[v.index]
                
            # Checking for upper right vertex:
            if v.co[x] > center[x] and v.co[z] > center[z] and round(v.co[y]) == round(center[y]):
                print("selecting upper right vertex = ", v.index)
                vertexB = bpy.context.active_object.data.vertices[v.index]
                
        bpy.ops.object.mode_set(mode = 'EDIT')
        
        if vertexA == None or vertexB ==None:
            # DEBUG: Checking if the vertex were found:
            print("NONE: ", vertexA, vertexB)
            return
        
        for e in bpy.context.active_object.data.edges:
            # DEGUG: Printing edge keys:
            # print("left edge keys: ", e.vertices[0], e.vertices[1])
            
            # Storing edge index:
            if (e.vertices[0] == vertexA.index and e.vertices[1] == vertexB.index) or (e.vertices[0] == vertexB.index and e.vertices[1] == vertexA.index):
                print("top edge: ", e.index)
                topEdgeIndex = e.index
                
        # Searching for bottom edge:
        for v in selectedVerts:
            # DEGUG:
            # print(v.co, center)
                        
            # Checking for bottom left vertex:
            if v.co[x] < center[x] and v.co[z] < center[z] and round(v.co[y]) == round(center[y]):
                print("selecting bottom left vertex = ", v.index)
                vertexA = bpy.context.active_object.data.vertices[v.index]
                
            # Checking for bottom right vertex:
            if v.co[x] > center[x] and v.co[z] < center[z] and round(v.co[y]) == round(center[y]):
                print("selecting bottom right vertex = ", v.index)
                vertexB = bpy.context.active_object.data.vertices[v.index]
                
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_mode(type="EDGE")
        
        for e in bpy.context.active_object.data.edges:
            # DEGUG: Printing edge keys:
            # print("right edge keys: ", e.vertices[0], e.vertices[1])

            # Storing edge index:
            if (e.vertices[0] == vertexA.index and e.vertices[1] == vertexB.index) or (e.vertices[0] == vertexB.index and e.vertices[1] == vertexA.index):
                print("bottom edge: ", e.index)
                bottomEdgeIndex = e.index
                
        # Selecting edges:
        bpy.ops.object.mode_set(mode = 'OBJECT')

        # Selecting internal edges:
        bpy.context.active_object.data.edges[topEdgeIndex].select = True
        bpy.context.active_object.data.edges[bottomEdgeIndex].select = True
        
        # Applying deformation:
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.bevel(offset=degree, offset_pct=0, segments=segments, vertex_only=False)
        
        bpy.ops.object.mode_set(mode = 'OBJECT')
        
########################################################################

''' ---------------------- RESETING THE SCENE: ---------------------- '''
    
if len(bpy.context.scene.objects) > 0:
    bpy.ops.object.mode_set(mode = "OBJECT")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

########################################################################

''' ------------------ SIMULATING SELEX RULES: ------------------ '''

# Creating and defining shape tree root node:
root = Node("root", None)


'''C1: Initial settings:'''

label = "building"
width = 9
depth = 11
height = 5


'''C2: {<> -> createShape("building", 5, 9, 11)};'''

mass3D = create3DMass(label, width, depth, height)

# Adding building mass node:
root.addChild(Node(label, mass3D, width, depth, height))

# Retrieving root node descendant by label:
building = root.descendant(label) # HARDCODED (GENERALIZE VARIABLE 'building') 

# Configuring object mode:
bpy.ops.object.mode_set(mode = "EDIT")
bpy.ops.mesh.select_all(action = "DESELECT")
bpy.ops.object.mode_set(mode = "OBJECT")

# Creating nodes with object faces:
front = Node(building.label + "_" + "front", building.getPolygon(3), building.getDimX(), 0, building.getDimZ())
left = Node(building.label + "_" + "left", building.getPolygon(0), building.getDimY(), 0, building.getDimZ())
right = Node(building.label + "_" + "right", building.getPolygon(2), building.getDimY(), 0, building.getDimZ())
back = Node(building.label + "_" + "back", building.getPolygon(1), building.getDimX(), 0, building.getDimZ())

# Adding front, back, left and right faces as children of 'building':
building.addChild(front)
building.addChild(left)
building.addChild(right)
building.addChild(back)

# Reseting object mode:
bpy.ops.object.mode_set(mode = "EDIT")
bpy.ops.mesh.select_all(action = "DESELECT")
bpy.ops.object.mode_set(mode = "OBJECT")


# VARIABLES, SELECTION AND RENAMING OF MULTIPLE ELEMENTS STILL HARDCODED:
'''C3: {<descendant()[label=="building"] / 
                     [label=="building_front"]> 
                     -> createGrid(label, rows, columns)};'''

# Retrieving child labeled as 'building' from 'root':
building = root.descendant(label) # HARDCODED (GENERALIZE VARIABLE 'building')

buildingChildLabel = "building_front" # HARDCODED (GENERALIZE VARIABLE 'buildingChildLabel' + GET 'label' FROM RULE)

# Retrieving child labeled as 'building_front' from 'building':
frontFace = building.descendant(buildingChildLabel) # HARDCODED (GENERALIZE 'frontFace')

# Retrieving face dimensions:
faceWidth = frontFace.getDimX() # HARDCODED (FROM 'frontFace')
faceHeight = frontFace.getDimZ() # HARDCODED (FROM 'frontFace')

# DEBUG - Printing dimensions:
print("FACE DIMENSIONS: ", faceWidth, faceHeight)

# Defining number of rows and columns of the grid:
label = "facade"
rows = 3
columns = 5

# Using face dimensions to generate grid:
virtualShape = createGrid(label, int(faceWidth), int(faceHeight), rows, columns)

# Adding virtual shape as child of building_front:
frontFace.addChild(Node(label, virtualShape)) # HARDCODED (CHANGE 'frontFace' FOR GENERALIZED VARIABLE)

# Retriving object from shape tree:
facade = frontFace.descendant(label) # HARDCODED (GENERALIZE 'facade' + CHANGE 'frontFace' FOR GENERALIZED VARIABLE)

# Positioning virtual shape over appropriate face, in this case 'front': HARDCODED (MAKE TRANSFORMATIONS DEPENDING ON SELECTED FACE)

# Always rotate 90 degrees at x-axis:
bpy.context.object.rotation_euler[0] = 1.5708

# Rotating grid at y-axis to fit over the face appropriately:
bpy.context.object.rotation_euler[1] = 1.5708 # HARDCODED

# If it's 'front' or 'back' face, just update location at y-axis appropriately:

## Inverting the sign is needed for 'front' location:
bpy.context.object.location[1] = (-building.getDimY()) / 2 # HARDCODE

## For 'back' location:
# bpy.context.object.location[1] = building.getDimY() / 2 # HARDCODED

# If it's 'left' or 'right' face:

## Perform a rotation by 90 degrees at z-axis:
# bpy.context.object.rotation_euler[2] = 1.5708 # HARDCODED

## Inverting the sign is needed for 'left' location:
# bpy.context.object.location[0] = (-building.getDimX()) / 2 # HARDCODED

## For 'right' location:
# bpy.context.object.location[0] = building.getDimX() / 2 # HARDCODED


# VARIABLES, SELECTION AND RENAMING OF MULTIPLE ELEMENTS STILL HARDCODED:
'''C4: {<descendant()[label=="building"] / 
                     [label=="building_front"] / 
                     [label=="facade"] / 
                     [type=="cell"] 
                     [rowIdx in (2, 3)] 
                     [colIdx in (1, 2)> 
                     -> addVolume("entrance", "building_front", 2.5, ["entrance_front", "entrance_left", "entrance_right"])};'''

# Selection by rows and columns indexes:

## Selection settings:
rowsIndex = [2, 3]
columnsIndex = [1, 2]

# Extrusion setting:
extrusionHeight = 2.5

# Shape tree labels:
facade = "facade" # HARDCODED (GENERALIZE 'facade' + GET FROM RULE)
parent = "bulding_front" # HARDCODED (GET PARENT 'label' FROM RULE)
label = "entrance" # HARDCODED (GET 'label' FROM RULE)

## Finding row and column indexes for a specific cell (using its polygon index):

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
print("SELECTED CELLS: ", selectedCells)

# Changing object mode:
bpy.ops.object.mode_set(mode = 'OBJECT')

## Deselect everything:
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_all(action = 'DESELECT')

bpy.ops.object.mode_set(mode = 'OBJECT')

# Looping through selectedCells in order to select each one:
for cell in selectedCells:    
    # Setting each cell select status to True:
    bpy.ops.object.mode_set(mode = 'OBJECT')
    bpy.data.objects[facade].data.polygons[cell].select = True # HARDCODED (CHANGE FOR GENERALIZED VARIABLE OF 'facade')
    bpy.ops.object.mode_set(mode = 'EDIT')
        
# Changing select mode:
bpy.ops.mesh.select_mode(type='FACE')

# Separate selected subgrid from 'facade' by creating a new form:
bpy.ops.mesh.separate(type='SELECTED')

# Storing reference to region (to be used for extrusion from building):
entrance = bpy.context.selected_objects[0] # HARDCODE (GENERALIZE VARIABLE 'entrance')

# Changing name attribute to label:
entrance.name = label # HARDCODED (USE GENERALIZED VARIABLE 'entrance')

# Adding 'entrance' as child of 'building_front':
frontFace.addChild(Node(label, entrance)) # HARDCODED

# Changing to object mode:
bpy.ops.object.mode_set(mode = "OBJECT")

# Moving object's origin to its center:
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

# Creating unliked copy to be used as virtual shape of 'entrance':
bpy.ops.object.duplicate()


''' HARDCODED (FIX SHAPE TREE - BEGIN) '''
# AFTER EXTRUSION CHANGE PARENT TO parentName.001...
# Renaming virtual shape appropriately:
entranceGrid = bpy.data.objects[label + ".001"] # HARDCODED (GENERALIZE VARIABLE 'entranceGrid')

# Renaming virtual shape:
entranceGrid.name = label + "_grid" # HARDCODED (CHANGE FOR GENERALIZED VARIABLE)

# Retrieving 'entrance' node:
entrance = frontFace.descendant(label) # HARDCODED (GENERALIZE VARIABLE 'entrance' + CHANGE 'frontFrace' FOR GENERALIZED VARIABLE)

# AFTER EXTRUSION CHANGE PARENT TO entrance_front...
# Adding virtual shape as 'entrance' child:
#entrance.addChild(Node(entranceGrid.name, entranceGrid))

# Deselecting object:
bpy.data.objects[entranceGrid.name].select_set(False)
''' HARDCODED (FIX SHAPE TREE - END) '''

# Selecting object to dissolve internal edges:
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
ids = list(range(len(entrance.getEdges())))

# DEBUG: Printing all of the edges indexes:
print("ALL EDGES INDEXES: ", ids)

# Storing just the selected indexes:
selectedEdges = [e.index for e in entrance.getEdges() if e.select]

# DEBUG: Printing border indexes:
print("BORDER EDGES INDEXES: ", selectedEdges)

# Removing border indexes, so the remaining will be internal:
for e in selectedEdges:
    ids.remove(e)
    
# DEBUG: Printing internal indexes:
print("INTERNAL EDGES INDEXES: ", ids)

bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_all(action = 'DESELECT')

bpy.ops.object.mode_set(mode = 'OBJECT')

# Selecting internal edges by index:
for id in ids:
    bpy.data.objects[label].data.edges[id].select = True
    
bpy.ops.object.mode_set(mode = 'EDIT')

# Dissolving internal edges:
bpy.ops.mesh.dissolve_edges()

# Deselecting object:
bpy.data.objects[label].select_set(False)

# DEBUG: building_front number of children:
# print("BUILDING_FRONT CHILDREN: ", len(frontFace.children))

bpy.ops.object.mode_set(mode = 'OBJECT')

# Selecting objects to be joined:
bpy.data.objects["entrance"].select_set(True) # HARDCODED (GET FROM RULE)

bpy.context.view_layer.objects.active = bpy.data.objects["building"] # HARDCODED (GET FROM RULE)
bpy.data.objects["building"].select_set(True) # HARDCODED (GET FROM RULE)

# Joining selected objects ('entrance' will be merged into 'building'):
bpy.ops.object.join()

# Changing object mode:
bpy.ops.object.mode_set(mode = 'EDIT')

# Selecting last object face by its index:
regionIdx = len(building.obj.data.polygons)-1 # HARDCODED

print("REGION INDEX: ", regionIdx)

bpy.ops.mesh.select_all(action = 'DESELECT')

# Reselect specific face:
bpy.ops.object.mode_set(mode = 'OBJECT')

# Selecting faces of the object by it's index:
bpy.data.objects["building"].data.polygons[regionIdx].select = True # HARDCODED

# Changing object mode:
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_mode(type = 'FACE')

# Applying extrusion:

## Invert value sinal (negative) for 'front' and 'left' face extrusaaion:
bpy.ops.mesh.extrude_region_move(
    TRANSFORM_OT_translate={"value":(0, -extrusionHeight, 0)} # HARDCODED (FOR 'front' AND 'left' EXTRUSION)
)

## 'right' and 'back' face extrusion:
# bpy.ops.mesh.extrude_region_move(
#     TRANSFORM_OT_translate={"value":(0, extrusionHeight, 0)} # HARDCODED (FOR 'right' AND 'back' EXTRUSION)
# )

## Retrieving generates faces after extrusion (entrance_front, entrance_left, entrance_right):
# TO-DO

## Moving 'entrance_grid' over 'entrance_front'
# TO-DO

# ORGANIZE SHAPE TREE WITH NEW NODES HERE
# TO-DO

'''C4: {<descendant()[label=="entrance"] / [label=="ef"]> 
       -> roundShape("front", 1.0, 30, "vertical")};'''
       
## Settings: offset = degree of roundness | segments = degree of 'realism'
roundingDegree = 0.3
numberSegments = 30
deformationType = "left" # front | left | right | bottom | top
deformationAxis = "horizontal" # 'frontal' deformation: vertical | horizontal

bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Storing selected face of the object (label = ef):
# TO-DO: SELECT USING PROPER FUNCTION THROUGH SHAPE TREE:
entranceFront = bpy.data.objects["building"].data.polygons[regionIdx+1] # HARDCODED (GENERALIZE VARIABLE 'entranceFront')

# Calling deformation function:

roundShape(entranceFront, deformationType, roundingDegree, numberSegments, deformationAxis)

print("-----------------------------------------------------------------------")