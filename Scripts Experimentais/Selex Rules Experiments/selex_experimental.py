########################################################################################################
# $ IMPORTED LIBRARIES
########################################################################################################

import bpy
import math
import os
import re


########################################################################################################
# $ USER CONFIGURATION MODULE
########################################################################################################

# Enter the filename containing the rules and run the script to create the model:
INPUT_FILE_NAME = "rules_1.slx"

# Flag to hide virtual shapes after model generation:
HIDE_VIRTUAL_SHAPES = True

# Flag to remove 'grid' shapes after model generation:
REMOVE_VIRTUAL_SHAPES = True


########################################################################################################
# $ CLASSES MODULE
########################################################################################################

class Node(object):
    # CONSTRUCTOR:
    def __init__(self, label, object, parent):
        # ATTRIBUTES:
        
        # Object label:
        self.label = label
        
        # Mesh reference: 
        self.obj = object
        
        # Parent shape:
        self.parent = parent
        
        # Subshapes:
        self.children = []
        
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
    
    ## Utility functions:
    
    def getPolygon(self, index):
        return self.obj.data.polygons[index]
    
    def getEdges(self):
        return self.obj.data.edges
    
    def getIndex(self):
        return self.obj.index
    
    def printChildren(self):
        for child in self.children:
            print(child.label)


# Inheritance from Node:
class Virtual(Node):
    # CONSTRUCTOR:
    def __init__(self, label, object, parent, rows, columns):
        # Calling parent constructor:
        super().__init__(label, object, parent)
        
        # ATTRIBUTES:
        
        ## Number of rows/columns and type:
        self.rows = rows-1
        self.columns = columns-1
        
    # GETTERS:
        
    def getRows(self):
        return self.rows
    
    def getColumns(self):
        return self.columns
    
    def getType(self):
        return type(self).__name__
        

# Inheritance from Node:
class Construction(Node):
    # CONSTRUCTOR:
    def __init__(self, label, object, parent, dimX=0, dimY=0, dimZ=0):
        # Calling parent constructor:
        super().__init__(label, object, parent)
         
        # ATTRIBUTES:
          
        ## Dimensions:
        self.dimX = dimX
        self.dimY = dimY
        self.dimZ = dimZ
        
    # GETTERS:
        
    def getDimX(self):
        return self.dimX
    
    def getDimY(self):
        return self.dimY
    
    def getDimZ(self):
        return self.dimZ
    
    def getType(self):
        return type(self).__name__
    

########################################################################################################
# $ INITIALIZE SHAPE TREE
########################################################################################################

# Defining shape tree root node as a global variable:
root = Node("root", None, None)


########################################################################################################
# $ UTILITY FUNCTIONS
########################################################################################################

# Used for creating the initial mass model from settings values:
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
    
    # Returning mesh reference:
    return mass


# Used for creating the virtual shape:
def vert(x, y, sizeRows, sizeColumns):
    # Creating single vert:
    return (x * sizeColumns, y * sizeRows, 0)


# Used for creating the virtual shape:
def face(x, y, rows):
    # Creating single face:
    return (x * rows + y,
           (x + 1) * rows + y,
           (x + 1) * rows + 1 + y,
           x * rows + 1 + y)

           
# Used for selecting a node from the shape tree by its label:
def selectNode(root, labels):
    currentNode = root
    child = None
    
    for label in labels:
        child = currentNode.descendant(label)
        currentNode = child
        
    return child


# Used for positioning main virtual shape over proper model side:
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
        
     
# Used for selecting cells from virtual shape in order to apply extrusion:
def selectToBeVolume(grid, rows, columns, rowsIndex, columnsIndex):
    # Setting grid as active object inside the scene:
    bpy.context.view_layer.objects.active = bpy.data.objects[grid.getLabel()]
    
    # Used to store the conversion from row and column indices to face index:
    selectCells = []

    for rowIndex in rowsIndex:
        for columnIndex in columnsIndex:
            cellIndex = (columns * rowIndex) - columns + (columnIndex - 1)
            selectCells.append(cellIndex)

    # DEBUG - Printing selected indices:      
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
    
    
# Used for duplicating a given virtual shape by its label:
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
    
    # Returning copied mesh reference:
    return shapeCopy


# Used for reseting the scene and cleaning the console after each execution:
def resetScene():    
    # Changing Mode:
    ## bpy.ops.object.mode_set(mode = "OBJECT")
    
    # Deleting created objects if they exist:
    if len(bpy.context.scene.objects) > 0:
        
        for hiddenObj in bpy.context.scene.objects:
            hiddenObj.hide_set(False)
        
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete()


# Used for hiding virtual shapes after model generation:
def hideVirtualShapes():
    for obj in bpy.data.objects:
        if "grid" in obj.name:
            obj.hide_set(True)
            

# Used for removing virtual shapes after model generation:
def removeVirtualShapes():
    # Changing object's visibility to 'visible':
    for hiddenObj in bpy.context.scene.objects:
        hiddenObj.hide_set(False)
        
    bpy.ops.object.mode_set(mode = "OBJECT")
    bpy.ops.object.select_all(action='DESELECT')
    
    # Removing objects containing 'grid' in its name:
    for obj in bpy.data.objects:
        if "grid" in obj.name:
            bpy.data.objects[obj.name].select_set(True)
            bpy.ops.object.delete()


# Used for generating a list of indices from 'idxBegin' to 'idxEnd':
def rangeIndex(idxBegin, idxEnd):
    return [i for i in range(idxBegin, idxEnd)]


########################################################################################################
# $ ACTIONS MODULE
########################################################################################################

# Used for creating a virtual shape and update the shape tree:
def createGrid(label, side, rows, columns):
    # Retrieving side dimensions:
    width = side.getDimX()
    height = side.getDimZ()

    # DEBUG - Printing dimensions:
    ## print("FACE DIMENSIONS: ", width, height)
    
    # Changing values for desired number of rows and columns:
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
    side.addChild(Virtual(label, mesh, side, rows, columns))
    
    # Returning the created mesh reference:
    return mesh


# Used for creating the mass model and update shape tree:
def createShape(root, label, width, depth, height):
    # Creating and retrieving mass model:
    mass3D = create3DMass(label, width, depth, height)

    # Adding building mass node to shape tree:
    root.addChild(Construction(label, mass3D, root, width, depth, height))

    # Retrieving root node descendant by label:
    building = root.descendant(label)

    # Configuring mode:
    bpy.ops.object.mode_set(mode = "EDIT")
    bpy.ops.mesh.select_all(action = "DESELECT")
    bpy.ops.object.mode_set(mode = "OBJECT")

    # Creating nodes with object faces:
    front = Construction(building.label + "_" + "front", building.getPolygon(3), building, width, 0, height)
    left = Construction(building.label + "_" + "left", building.getPolygon(0), building, depth, 0, height)
    right = Construction(building.label + "_" + "right", building.getPolygon(2), building, depth, 0, height)
    back = Construction(building.label + "_" + "back", building.getPolygon(1), building, width, 0, height)

    # Adding front, back, left and right faces as children of 'building':
    building.addChild(front)
    building.addChild(left)
    building.addChild(right)
    building.addChild(back)

    # Reseting object mode:
    bpy.ops.object.mode_set(mode = "EDIT")
    bpy.ops.mesh.select_all(action = "DESELECT")
    bpy.ops.object.mode_set(mode = "OBJECT")


# Used for extruding selected region:
def addVolume(label, parent, extrusionSize, sidesLabels, gridLabel, gridRows, gridColumns):
    # Grouping selected cells into a region to be extruded, and storing created subgrid:
    subgrid = groupRegions(label, parent, gridLabel)
    
    # Retrieving shape parent:
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

    # Selecting faces of the object by its index:
    bpy.data.objects[grandparent.getLabel()].data.polygons[regionIndex].select = True

    # Changing selection mode:
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
    parent.addChild(Construction(sidesLabels[0], regionFrontMesh, parent))
    
    ## Retrieving front face node:
    regionFront = parent.descendant(sidesLabels[0])
    
    ## Adding virtual grid as child of front face:
    regionFront.addChild(Virtual(subgrid.name, subgrid, regionFront, gridRows, gridColumns))
    
    # Retrieving frontal polygon index:
    return regionIndex + 1


# Used for grouping selected cells:
def groupRegions(label, parent, gridLabel):
    # Separating selected subgrid by creating a new object:
    bpy.ops.mesh.separate(type='SELECTED')
    
    bpy.data.objects[gridLabel + ".001"].select_set(False)
    
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
    
    # Setting object mode:
    bpy.ops.object.mode_set(mode = 'OBJECT')
    
    # Adding created region as child of parent:
    parent.addChild(Construction(label, region, parent))

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

    # Creating list with all of the object indices:
    ids = list(range(len(region.getEdges())))

    # DEBUG - Printing all of the edges indices:
    ## print("ALL EDGES INDICES: ", ids)

    # Storing just the selected indices:
    selectedEdges = [e.index for e in region.getEdges() if e.select]

    # DEBUG - Printing border indices:
    ## print("BORDER EDGES INDICES: ", selectedEdges)

    # Removing border indices, so the remaining will be internal:
    for e in selectedEdges:
        ids.remove(e)
  
    # DEBUG - Printing internal indices:
    ## print("INTERNAL EDGES INDICES: ", ids)

    # Changing mode:
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


# Used for applying round deformation to a given object:
def roundShape(object, type, direction, roundingDegree, segments, sideReference, axis="", insideDegree=0.05):
    center = object.center
    
    # DEBUG: Printing center coordinate of the face:
    ## print("CENTER COORDINATE = ", center)
    
    # Retrieving vertices of the face:    
    verts = object.vertices

    # Selecting vertices of the face:
    for v in verts:
        bpy.context.active_object.data.vertices[v].select = True
        
    # Storing selected vertexes form object:
    selectedVerts = [v for v in bpy.context.active_object.data.vertices if v.select]
    
    # Deselecting vertices:
    for v in verts:
        bpy.context.active_object.data.vertices[v].select = False

    # DEBUG: Printing coordinates of the selected vertexes:
    ## for v in selectedVerts:
    ##     print("vertex index = ", v.index)
    ##     print("vertex coordinate = ", v.co)
        
    # Changing the axis for an alias:
    x, y, z = 0, 1, 2
    
    if sideReference == "main_front":
        # Round left:
        if type == "left":
            # DEBUG:
            ## print("ROUND LEFT")
                
            for v in selectedVerts:
                # DEBUG:
                # print(v.co, center)
                            
                # Checking for upper left vertex:
                if v.co[x] < center[x] and v.co[z] > center[z]:
                    # DEBUG:
                    ## print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True
                    
                # Checking for bottom left vertex:
                if v.co[x] < center[x] and v.co[z] < center[z]:
                    # DEBUG:
                    ## print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True
            
            # Changing object mode:
            bpy.ops.object.mode_set(mode = 'EDIT')  
            bpy.ops.mesh.select_mode(type="VERT")
            
            # Applying specific deformation:
            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')
             
        # Round right:       
        if type == "right":
            # DEBUG:
            ## print("ROUND RIGHT")
                
            for v in selectedVerts:
                # DEBUG:
                # print(v.co, center)
                            
                # Checking for upper right vertex:
                if v.co[x] > center[x] and v.co[z] > center[z]:
                    # DEBUG:
                    ## print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True
                    
                # Checking for bottom right vertex:
                if v.co[x] > center[x] and v.co[z] < center[z]:
                    # DEBUG:
                    ## print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True

            # Changing object mode:
            bpy.ops.object.mode_set(mode = 'EDIT')  
            bpy.ops.mesh.select_mode(type="VERT")
            
            # Applying specific deformation:
            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')
        
        # Round top:
        if type == "top":
            # DEBUG:
            ## print("ROUND TOP")
                
            for v in selectedVerts:
                # DEBUG:
                # print(v.co, center)
                            
                # Checking for upper right vertex:
                if v.co[x] < center[x] and v.co[z] > center[z]:
                    # DEBUG:
                    ## print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True
                    
                # Checking for bottom right vertex:
                if v.co[x] > center[x] and v.co[z] > center[z]:
                    # DEBUG:
                    ## print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True

            # Changing object mode:
            bpy.ops.object.mode_set(mode = 'EDIT')  
            bpy.ops.mesh.select_mode(type="VERT")
            
            # Applying specific deformation:
            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')
         
        # Round bottom:   
        if type == "bottom":
            # DEBUG:
            ## print("ROUND BOTTOM")
                
            for v in selectedVerts:
                # DEBUG:
                # print(v.co, center)
                            
                # Checking for upper right vertex:
                if v.co[x] < center[x] and v.co[z] < center[z]:
                    # DEBUG:
                    ## print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True
                    
                # Checking for bottom right vertex:
                if v.co[x] > center[x] and v.co[z] < center[z]:
                    # DEBUG:
                    ## print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True

            # Changing object mode:
            bpy.ops.object.mode_set(mode = 'EDIT')  
            bpy.ops.mesh.select_mode(type="VERT")
            
            # Applying specific deformation:
            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')

        # Round front vertically by performing a mix of round left and right, but with edges:
        if type == "front" and axis == "vertical":
            # DEBUG:
            ## print("ROUND FRONT VERTICAL")
            
            leftEdgeIndex, rightEdgeIndex = 0, 0
            vertexA, vertexB = None, None
            
            # Searching for left edge:
            for v in selectedVerts:
                # DEBUG:
                # print("VERT: ", v.index, v.co)
                            
                # Checking for upper left vertex:
                if v.co[x] < center[x] and v.co[z] > center[z] and round(v.co[y]) == round(center[y]):
                    # DEBUG:
                    ## print("selecting upper left vertex = ", v.index)
                    vertexA = bpy.context.active_object.data.vertices[v.index]
                    
                # Checking for bottom left vertex:
                if v.co[x] < center[x] and v.co[z] < center[z] and round(v.co[y]) == round(center[y]):
                    # DEBUG:
                    ## print("selecting bottom left vertex = ", v.index)
                    vertexB = bpy.context.active_object.data.vertices[v.index]
                    
            bpy.ops.object.mode_set(mode = 'EDIT')
            
            # Checking if one of the vertexes was not found:
            if vertexA == None or vertexB ==None:
                # DEBUG:
                ## print("NONE: ", vertexA, vertexB)
                return
            
            for e in bpy.context.active_object.data.edges:
                # DEGUG: Printing edge keys:
                ## print("left edge keys: ", e.vertices[0], e.vertices[1])
                
                # Storing edge index:
                if (e.vertices[0] == vertexA.index and e.vertices[1] == vertexB.index) or (e.vertices[0] == vertexB.index and e.vertices[1] == vertexA.index):
                    # DEBUG:
                    ## print("left edge: ", e.index)
                    leftEdgeIndex = e.index
                    
            # Searching for right edge:
            for v in selectedVerts:
                # DEGUG:
                # print(v.co, center)
                            
                # Checking for upper right vertex:
                if v.co[x] > center[x] and v.co[z] > center[z] and round(v.co[y]) == round(center[y]):
                    # DEBUG:
                    ## print("selecting upper right vertex = ", v.index)
                    vertexA = bpy.context.active_object.data.vertices[v.index]
                    
                # Checking for bottom right vertex:
                if v.co[x] > center[x] and v.co[z] < center[z] and round(v.co[y]) == round(center[y]):
                    # DEBUG:
                    ## print("selecting bottom right vertex = ", v.index)
                    vertexB = bpy.context.active_object.data.vertices[v.index]
                    
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_mode(type="EDGE")
            
            for e in bpy.context.active_object.data.edges:
                # DEGUG: Printing edge keys:
                # print("right edge keys: ", e.vertices[0], e.vertices[1])

                # Storing edge index:
                if (e.vertices[0] == vertexA.index and e.vertices[1] == vertexB.index) or (e.vertices[0] == vertexB.index and e.vertices[1] == vertexA.index):
                    # DEBUG:
                    ## print("right edge: ", e.index)
                    rightEdgeIndex = e.index
                    
            # Selecting edges:
            bpy.ops.object.mode_set(mode = 'OBJECT')

            # Selecting internal edges:
            bpy.context.active_object.data.edges[leftEdgeIndex].select = True
            bpy.context.active_object.data.edges[rightEdgeIndex].select = True
            
            # Applying specific deformation:
            bpy.ops.object.mode_set(mode = 'EDIT')
            
            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')
            
        # Round front horizontally by performing a mix of round left and right, but with edges:
        if type == "front" and axis == "horizontal":
            # DEBUG:
            ## print("ROUND FRONT HORIZONTAL")
            
            topEdgeIndex, bottomEdgeIndex = 0, 0
            vertexA, vertexB = None, None
            
            # Searching for top edge:
            for v in selectedVerts:
                # DEGUG:
                ## print("VERT | CENTER: ", v.co[y], center[y])
                            
                # Checking for upper left vertex:
                if v.co[x] < center[x] and v.co[z] > center[z] and math.floor(v.co[y]) == math.floor(center[y]):
                    # DEBUG:
                    ## print("selecting upper left vertex = ", v.index)
                    vertexA = bpy.context.active_object.data.vertices[v.index]
                    
                # Checking for upper right vertex:
                if v.co[x] > center[x] and v.co[z] > center[z] and math.floor(v.co[y]) == math.floor(center[y]):
                    # DEBUG:
                    ## print("selecting upper right vertex = ", v.index)
                    vertexB = bpy.context.active_object.data.vertices[v.index]
                    
            bpy.ops.object.mode_set(mode = 'EDIT')
            
            # Checking if the vertexes were found:
            if vertexA == None or vertexB == None:
                # DEBUG:
                ## print("NONE: ", vertexA, vertexB)
                return
            
            for e in bpy.context.active_object.data.edges:
                # DEGUG: Printing edge keys:
                ## print("left edge keys: ", e.vertices[0], e.vertices[1])
                
                # Storing edge index:
                if (e.vertices[0] == vertexA.index and e.vertices[1] == vertexB.index) or (e.vertices[0] == vertexB.index and e.vertices[1] == vertexA.index):
                    # DEBUG:
                    ## print("top edge: ", e.index)
                    topEdgeIndex = e.index
                    
            # Searching for bottom edge:
            for v in selectedVerts:
                # DEGUG:
                ## print(v.co, center)
                            
                # Checking for bottom left vertex:
                if v.co[x] < center[x] and v.co[z] < center[z] and math.floor(v.co[y]) == math.floor(center[y]):
                    # DEBUG:
                    ## print("selecting bottom left vertex = ", v.index)
                    vertexA = bpy.context.active_object.data.vertices[v.index]
                    
                # Checking for bottom right vertex:
                if v.co[x] > center[x] and v.co[z] < center[z] and math.floor(v.co[y]) == math.floor(center[y]):
                    # DEBUG:
                    ## print("selecting bottom right vertex = ", v.index)
                    vertexB = bpy.context.active_object.data.vertices[v.index]
                    
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_mode(type="EDGE")
            
            for e in bpy.context.active_object.data.edges:
                # DEGUG: Printing edge keys:
                ## print("right edge keys: ", e.vertices[0], e.vertices[1])

                # Storing edge index:
                if (e.vertices[0] == vertexA.index and e.vertices[1] == vertexB.index) or (e.vertices[0] == vertexB.index and e.vertices[1] == vertexA.index):
                    # DEBUG:
                    ## print("bottom edge: ", e.index)
                    bottomEdgeIndex = e.index
                    
            # Selecting edges:
            bpy.ops.object.mode_set(mode = 'OBJECT')

            # Selecting internal edges:
            bpy.context.active_object.data.edges[topEdgeIndex].select = True
            bpy.context.active_object.data.edges[bottomEdgeIndex].select = True
            
            bpy.ops.object.mode_set(mode = 'EDIT')
            
            # Applying specific deformation:
            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')
            
    if sideReference == "main_back":
        # Round left:
        if type == "left":
            # DEBUG:
            ## print("ROUND LEFT")
                
            for v in selectedVerts:
                # DEBUG:
                ## print(v.co, center)
                            
                # Checking for upper left vertex:
                if v.co[x] > center[x] and v.co[z] > center[z]:
                    # DEBUG:
                    ## print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True
                    
                # Checking for bottom left vertex:
                if v.co[x] > center[x] and v.co[z] < center[z]:
                    # DEBUG:
                    ## print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True
            
            # Changing object mode:
            bpy.ops.object.mode_set(mode = 'EDIT')  
            bpy.ops.mesh.select_mode(type="VERT")
            
            # Applying specific deformation:
            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')
             
        # Round right:       
        if type == "right":
            # DEBUG:
            ## print("ROUND RIGHT")
                
            for v in selectedVerts:
                # DEBUG:
                ## print(v.co, center)
                            
                # Checking for upper right vertex:
                if v.co[x] < center[x] and v.co[z] > center[z]:
                    # DEBUG:
                    ## print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True
                    
                # Checking for bottom right vertex:
                if v.co[x] < center[x] and v.co[z] < center[z]:
                    # DEBUG:
                    ## print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True

            # Changing object mode:
            bpy.ops.object.mode_set(mode = 'EDIT')  
            bpy.ops.mesh.select_mode(type="VERT")
            
            # Applying specific deformation:
            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')
        
        # Round top:
        if type == "top":
            # DEBUG:
            ## print("ROUND TOP")
                
            for v in selectedVerts:
                # DEBUG:
                # print(v.co, center)
                            
                # Checking for upper right vertex:
                if v.co[x] < center[x] and v.co[z] > center[z]:
                    # DEBUG:
                    ## print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True
                    
                # Checking for bottom right vertex:
                if v.co[x] > center[x] and v.co[z] > center[z]:
                    # DEBUG:
                    ## print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True

            # Changing object mode:
            bpy.ops.object.mode_set(mode = 'EDIT')  
            bpy.ops.mesh.select_mode(type="VERT")
            
            # Applying deformation:
            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')
         
        # Round bottom:   
        if type == "bottom":
            # DEBUG:
            ## print("ROUND BOTTOM")
                
            for v in selectedVerts:
                # DEBUG:
                # print(v.co, center)
                            
                # Checking for upper right vertex:
                if v.co[x] < center[x] and v.co[z] < center[z]:
                    # DEBUG:
                    ## print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True
                    
                # Checking for bottom right vertex:
                if v.co[x] > center[x] and v.co[z] < center[z]:
                    # DEBUG:
                    ## print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True

            # Changing object mode:
            bpy.ops.object.mode_set(mode = 'EDIT')  
            bpy.ops.mesh.select_mode(type="VERT")
            
            # Applying deformation:
            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')

        # Performing a mix of round left and right, but with edges:
        if type == "front" and axis == "vertical":
            # DEBUG:
            ## print("ROUND FRONT VERTICAL")
            
            leftEdgeIndex, rightEdgeIndex = 0, 0
            vertexA, vertexB = None, None
            
            # Searching for left edge:
            for v in selectedVerts:
                # DEGUG:
                # print("VERT: ", v.index, v.co)
                            
                # Checking for upper left vertex:
                if v.co[x] < center[x] and v.co[z] > center[z] and round(v.co[y]) == round(center[y]):
                    # DEBUG:
                    ## print("selecting upper left vertex = ", v.index)
                    vertexA = bpy.context.active_object.data.vertices[v.index]
                    
                # Checking for bottom left vertex:
                if v.co[x] < center[x] and v.co[z] < center[z] and round(v.co[y]) == round(center[y]):
                    # DEBUG:
                    ## print("selecting bottom left vertex = ", v.index)
                    vertexB = bpy.context.active_object.data.vertices[v.index]
                    
            bpy.ops.object.mode_set(mode = 'EDIT')
            
            # Checking if the vertex were found:
            if vertexA == None or vertexB ==None:
                # DEBUG:
                ## print("NONE: ", vertexA, vertexB)
                return
            
            for e in bpy.context.active_object.data.edges:
                # DEGUG: Printing edge keys:
                ## print("left edge keys: ", e.vertices[0], e.vertices[1])
                
                # Storing edge index:
                if (e.vertices[0] == vertexA.index and e.vertices[1] == vertexB.index) or (e.vertices[0] == vertexB.index and e.vertices[1] == vertexA.index):
                    # DEBUG:
                    ## print("left edge: ", e.index)
                    leftEdgeIndex = e.index
                    
            # Searching for right edge:
            for v in selectedVerts:
                # DEGUG:
                ## print(v.co, center)
                            
                # Checking for upper right vertex:
                if v.co[x] > center[x] and v.co[z] > center[z] and round(v.co[y]) == round(center[y]):
                    # DEBUG:
                    ## print("selecting upper right vertex = ", v.index)
                    vertexA = bpy.context.active_object.data.vertices[v.index]
                    
                # Checking for bottom right vertex:
                if v.co[x] > center[x] and v.co[z] < center[z] and round(v.co[y]) == round(center[y]):
                    # DEBUG:
                    ## print("selecting bottom right vertex = ", v.index)
                    vertexB = bpy.context.active_object.data.vertices[v.index]
                    
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_mode(type="EDGE")
            
            for e in bpy.context.active_object.data.edges:
                # DEGUG: Printing edge keys:
                ## print("right edge keys: ", e.vertices[0], e.vertices[1])

                # Storing edge index:
                if (e.vertices[0] == vertexA.index and e.vertices[1] == vertexB.index) or (e.vertices[0] == vertexB.index and e.vertices[1] == vertexA.index):
                    # DEBUG:
                    ## print("right edge: ", e.index)
                    rightEdgeIndex = e.index
                    
            # Selecting edges:
            bpy.ops.object.mode_set(mode = 'OBJECT')

            # Selecting internal edges:
            bpy.context.active_object.data.edges[leftEdgeIndex].select = True
            bpy.context.active_object.data.edges[rightEdgeIndex].select = True
            
            # Applying specific deformation:
            bpy.ops.object.mode_set(mode = 'EDIT')
            
            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')
            
        # Round front horizontally by performing a mix of round top and bottom, but with edges:
        if type == "front" and axis == "horizontal":
            # DEBUG:
            ## print("ROUND FRONT HORIZONTAL")
            
            topEdgeIndex, bottomEdgeIndex = 0, 0
            vertexA, vertexB = None, None
            
            # Searching for top edge:
            for v in selectedVerts:
                # DEGUG:
                ## print(v.co, center)
                            
                # Checking for upper left vertex:
                if v.co[x] < center[x] and v.co[z] > center[z] and math.floor(v.co[y]) == math.floor(center[y]):
                    # DEBUG:
                    ## print("selecting upper left vertex = ", v.index)
                    vertexA = bpy.context.active_object.data.vertices[v.index]
                    
                # Checking for upper right vertex:
                if v.co[x] > center[x] and v.co[z] > center[z] and math.floor(v.co[y]) == math.floor(center[y]):
                    # DEBUG:
                    ## print("selecting upper right vertex = ", v.index)
                    vertexB = bpy.context.active_object.data.vertices[v.index]
                    
            bpy.ops.object.mode_set(mode = 'EDIT')
            
            # Checking if the vertex were found:
            if vertexA == None or vertexB ==None:
                # DEBUG:
                ## print("NONE: ", vertexA, vertexB)
                return
            
            for e in bpy.context.active_object.data.edges:
                # DEGUG: Printing edge keys:
                ## print("left edge keys: ", e.vertices[0], e.vertices[1])
                
                # Storing edge index:
                if (e.vertices[0] == vertexA.index and e.vertices[1] == vertexB.index) or (e.vertices[0] == vertexB.index and e.vertices[1] == vertexA.index):
                    # DEBUG:
                    ## print("top edge: ", e.index)
                    topEdgeIndex = e.index
                    
            # Searching for bottom edge:
            for v in selectedVerts:
                # DEGUG:
                ## print(v.co, center)
                            
                # Checking for bottom left vertex:
                if v.co[x] < center[x] and v.co[z] < center[z] and math.floor(v.co[y]) == math.floor(center[y]):
                    # DEBUG:
                    ## print("selecting bottom left vertex = ", v.index)
                    vertexA = bpy.context.active_object.data.vertices[v.index]
                    
                # Checking for bottom right vertex:
                if v.co[x] > center[x] and v.co[z] < center[z] and math.floor(v.co[y]) == math.floor(center[y]):
                    # DEBUG:
                    ## print("selecting bottom right vertex = ", v.index)
                    vertexB = bpy.context.active_object.data.vertices[v.index]
                    
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_mode(type="EDGE")
            
            for e in bpy.context.active_object.data.edges:
                # DEGUG: Printing edge keys:
                ## print("right edge keys: ", e.vertices[0], e.vertices[1])

                # Storing edge index:
                if (e.vertices[0] == vertexA.index and e.vertices[1] == vertexB.index) or (e.vertices[0] == vertexB.index and e.vertices[1] == vertexA.index):
                    # DEBUG:
                    ## print("bottom edge: ", e.index)
                    bottomEdgeIndex = e.index
                    
            # Selecting edges:
            bpy.ops.object.mode_set(mode = 'OBJECT')

            # Selecting internal edges:
            bpy.context.active_object.data.edges[topEdgeIndex].select = True
            bpy.context.active_object.data.edges[bottomEdgeIndex].select = True
            
            # Applying specific deformation:
            bpy.ops.object.mode_set(mode = 'EDIT')

            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')
            

    if sideReference == "main_left":
        # Round left:
        if type == "left":
            # DEBUG:
            ## print("ROUND LEFT")
                
            for v in selectedVerts:
                # DEBUG:
                ## print(v.co, center)
                            
                # Checking for upper left vertex:
                if v.co[y] > center[y] and v.co[z] > center[z]:
                    # DEBUG:
                    ## print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True
                    
                # Checking for bottom left vertex:
                if v.co[y] > center[y] and v.co[z] < center[z]:
                    # DEBUG:
                    ## print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True
            
            # Changing object mode:
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_mode(type="VERT")
            
            # Applying specific deformation:
            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')
             
        # Round right:       
        if type == "right":
            # DEBUG:
            ## print("ROUND RIGHT")
                
            for v in selectedVerts:
                # DEBUG:
                ## print(v.co, center)
                            
                # Checking for upper right vertex:
                if v.co[y] < center[y] and v.co[z] > center[z]:
                    # DEBUG:
                    ## print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True
                    
                # Checking for bottom right vertex:
                if v.co[y] < center[y] and v.co[z] < center[z]:
                    # DEBUG:
                    ## print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True

            # Changing object mode:
            bpy.ops.object.mode_set(mode = 'EDIT')  
            bpy.ops.mesh.select_mode(type="VERT")
            
            # Applying specific deformation:
            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')
        
        # Round top:
        if type == "top":
            # DEBUG:
            ## print("ROUND TOP")
                
            for v in selectedVerts:
                # DEBUG:
                ## print(v.co, center)
                            
                # Checking for upper left vertex:
                if v.co[y] > center[y] and v.co[z] > center[z]:
                    # DEBUG:
                    # print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True
                    
                # Checking for upper right vertex:
                if v.co[y] < center[y] and v.co[z] > center[z]:
                    # DEBUG:
                    ## print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True

            # Changing object mode:
            bpy.ops.object.mode_set(mode = 'EDIT')  
            bpy.ops.mesh.select_mode(type="VERT")
            
            # Applying specific deformation:
            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')
         
        # Round bottom:   
        if type == "bottom":
            # DEBUG:
            ## print("ROUND BOTTOM")
                
            for v in selectedVerts:
                # DEBUG:
                ## print(v.co, center)
                            
                # Checking for bottom left vertex:
                if v.co[y] > center[y] and v.co[z] < center[z]:
                    # DEBUG:
                    ## print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True
                    
                # Checking for bottom right vertex:
                if v.co[y] < center[y] and v.co[z] < center[z]:
                    # DEBUG:
                    ## print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True

            # Changing object mode:
            bpy.ops.object.mode_set(mode = 'EDIT')  
            bpy.ops.mesh.select_mode(type="VERT")
            
            # Applying deformation:
            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')

        # Round front vertical by performing a mix of round left and right, but with edges:
        if type == "front" and axis == "vertical":
            # DEBUG:
            ## print("ROUND FRONT VERTICAL")
            
            leftEdgeIndex, rightEdgeIndex = 0, 0
            vertexA, vertexB = None, None
            
            # Searching for left edge:
            for v in selectedVerts:
                # DEGUG:
                ## print("VERT: ", v.index, v.co)
                            
                # Checking for upper left vertex:
                if v.co[y] > center[y] and v.co[z] > center[z] and round(v.co[x]) == round(center[x]):
                    # DEBUG:
                    ## print("selecting upper left vertex = ", v.index)
                    vertexA = bpy.context.active_object.data.vertices[v.index]
                    
                # Checking for bottom left vertex:
                if v.co[y] > center[y] and v.co[z] < center[z] and round(v.co[x]) == round(center[x]):
                    # DEBUG:
                    ## print("selecting bottom left vertex = ", v.index)
                    vertexB = bpy.context.active_object.data.vertices[v.index]
                    
            bpy.ops.object.mode_set(mode = 'EDIT')
            
            # Checking if the vertex were found:
            if vertexA == None or vertexB ==None:
                # DEBUG:
                ## print("NONE: ", vertexA, vertexB)
                return
            
            for e in bpy.context.active_object.data.edges:
                # DEGUG: Printing edge keys:
                ## print("left edge keys: ", e.vertices[0], e.vertices[1])
                
                # Storing edge index:
                if (e.vertices[0] == vertexA.index and e.vertices[1] == vertexB.index) or (e.vertices[0] == vertexB.index and e.vertices[1] == vertexA.index):
                    # DEBUG:
                    ## print("left edge: ", e.index)
                    leftEdgeIndex = e.index
                    
            # Searching for right edge:
            for v in selectedVerts:
                # DEGUG:
                ## print(v.co, center)
                            
                # Checking for upper right vertex:
                if v.co[y] < center[y] and v.co[z] > center[z] and round(v.co[x]) == round(center[x]):
                    # DEBUG:
                    ## print("selecting upper right vertex = ", v.index)
                    vertexA = bpy.context.active_object.data.vertices[v.index]
                    
                # Checking for bottom right vertex:
                if v.co[y] < center[y] and v.co[z] < center[z] and round(v.co[x]) == round(center[x]):
                    # DEBUG:
                    ## print("selecting bottom right vertex = ", v.index)
                    vertexB = bpy.context.active_object.data.vertices[v.index]
                    
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_mode(type="EDGE")
            
            for e in bpy.context.active_object.data.edges:
                # DEGUG: Printing edge keys:
                # print("right edge keys: ", e.vertices[0], e.vertices[1])

                # Storing edge index:
                if (e.vertices[0] == vertexA.index and e.vertices[1] == vertexB.index) or (e.vertices[0] == vertexB.index and e.vertices[1] == vertexA.index):
                    # DEBUG:
                    ## print("right edge: ", e.index)
                    rightEdgeIndex = e.index
                    
            # Selecting edges:
            bpy.ops.object.mode_set(mode = 'OBJECT')

            # Selecting internal edges:
            bpy.context.active_object.data.edges[leftEdgeIndex].select = True
            bpy.context.active_object.data.edges[rightEdgeIndex].select = True
            
            bpy.ops.object.mode_set(mode = 'EDIT')

            # Applying specific deformation:
            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')
            
        # Round front horizontally by performing a mix of round top and bottom, but with edges:
        if type == "front" and axis == "horizontal":
            # DEBUG:
            ## print("ROUND FRONT HORIZONTAL")
            
            topEdgeIndex, bottomEdgeIndex = 0, 0
            vertexA, vertexB = None, None
            
            # Searching for top edge:
            for v in selectedVerts:
                # DEGUG:
                ## print(v.co, center)
                            
                # Checking for upper left vertex:
                if v.co[y] > center[y] and v.co[z] > center[z] and math.floor(v.co[x]) == math.floor(center[x]):
                    # DEBUG:
                    ## print("selecting upper left vertex = ", v.index)
                    vertexA = bpy.context.active_object.data.vertices[v.index]
                    
                # Checking for upper right vertex:
                if v.co[y] < center[y] and v.co[z] > center[z] and math.floor(v.co[x]) == math.floor(center[x]):
                    # DEBUG:
                    ## print("selecting upper right vertex = ", v.index)
                    vertexB = bpy.context.active_object.data.vertices[v.index]
                    
            bpy.ops.object.mode_set(mode = 'EDIT')
            
            # Checking if the vertex were found:
            if vertexA == None or vertexB ==None:
                # DEBUG:
                ## print("NONE: ", vertexA, vertexB)
                return
            
            for e in bpy.context.active_object.data.edges:
                # DEGUG: Printing edge keys:
                ## print("left edge keys: ", e.vertices[0], e.vertices[1])
                
                # Storing edge index:
                if (e.vertices[0] == vertexA.index and e.vertices[1] == vertexB.index) or (e.vertices[0] == vertexB.index and e.vertices[1] == vertexA.index):
                    # DEBUG:
                    ## print("top edge: ", e.index)
                    topEdgeIndex = e.index
                    
            # Searching for bottom edge:
            for v in selectedVerts:
                # DEGUG:
                ## print(v.co, center)
                            
                # Checking for bottom left vertex:
                if v.co[y] > center[y] and v.co[z] < center[z] and math.floor(v.co[x]) == math.floor(center[x]):
                    # DEBUG:
                    ## print("selecting bottom left vertex = ", v.index)
                    vertexA = bpy.context.active_object.data.vertices[v.index]
                    
                # Checking for bottom right vertex:
                if v.co[y] < center[y] and v.co[z] < center[z] and math.floor(v.co[x]) == math.floor(center[x]):
                    # DEBUG:
                    ## print("selecting bottom right vertex = ", v.index)
                    vertexB = bpy.context.active_object.data.vertices[v.index]
                    
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_mode(type="EDGE")
            
            for e in bpy.context.active_object.data.edges:
                # DEGUG: Printing edge keys:
                ## print("right edge keys: ", e.vertices[0], e.vertices[1])

                # Storing edge index:
                if (e.vertices[0] == vertexA.index and e.vertices[1] == vertexB.index) or (e.vertices[0] == vertexB.index and e.vertices[1] == vertexA.index):
                    # DEBUG:
                    ## print("bottom edge: ", e.index)
                    bottomEdgeIndex = e.index
                    
            # Selecting edges:
            bpy.ops.object.mode_set(mode = 'OBJECT')

            # Selecting internal edges:
            bpy.context.active_object.data.edges[topEdgeIndex].select = True
            bpy.context.active_object.data.edges[bottomEdgeIndex].select = True
            
            bpy.ops.object.mode_set(mode = 'EDIT')

            # Applying specific deformation:
            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')
            
            
    if sideReference == "main_right":
        # Round left:
        if type == "left":
            # DEBUG:
            ## print("ROUND LEFT")
                
            for v in selectedVerts:
                # DEBUG:
                ## print(v.co, center)
                            
                # Checking for upper left vertex:
                if v.co[y] < center[y] and v.co[z] > center[z]:
                    # DEBUG:
                    ## print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True
                    
                # Checking for bottom left vertex:
                if v.co[y] < center[y] and v.co[z] < center[z]:
                    # DEBUG:
                    ## print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True
            
            # Changing object mode:
            bpy.ops.object.mode_set(mode = 'EDIT')  
            bpy.ops.mesh.select_mode(type="VERT")
            
            # Applying specific deformation:
            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')
             
        # Round right:       
        if type == "right":
            # DEBUG:
            ## print("ROUND RIGHT")
                
            for v in selectedVerts:
                # DEBUG:
                ## print(v.co, center)
                            
                # Checking for upper right vertex:
                if v.co[y] > center[y] and v.co[z] > center[z]:
                    # DEBUG:
                    ## print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True
                    
                # Checking for bottom right vertex:
                if v.co[y] > center[y] and v.co[z] < center[z]:
                    # DEBUG:
                    ## print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True

            # Changing object mode:
            bpy.ops.object.mode_set(mode = 'EDIT')  
            bpy.ops.mesh.select_mode(type="VERT")
            
            # Applying specific deformation:
            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')
        
        # Round top:
        if type == "top":
            # DEBUG:
            ## print("ROUND TOP")
                
            for v in selectedVerts:
                # DEBUG:
                ## print(v.co, center)
                            
                # Checking for upper left vertex:
                if v.co[y] < center[y] and v.co[z] > center[z]:
                    # DEBUG:
                    ## print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True
                    
                # Checking for upper right vertex:
                if v.co[y] > center[y] and v.co[z] > center[z]:
                    # DEBUG:
                    ## print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True

            # Changing object mode:
            bpy.ops.object.mode_set(mode = 'EDIT')  
            bpy.ops.mesh.select_mode(type="VERT")
            
            # Applying specific deformation:
            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')
         
        # Round bottom:   
        if type == "bottom":
            # DEBUG:
            ## print("ROUND BOTTOM")
                
            for v in selectedVerts:
                # DEBUG:
                ## print(v.co, center)
                            
                # Checking for bottom left vertex:
                if v.co[y] < center[y] and v.co[z] < center[z]:
                    # DEBUG:
                    ## print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True
                    
                # Checking for bottom right vertex:
                if v.co[y] > center[y] and v.co[z] < center[z]:
                    # DEBUG:
                    ## print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True

            # Changing object mode:
            bpy.ops.object.mode_set(mode = 'EDIT')  
            bpy.ops.mesh.select_mode(type="VERT")
            
            # Applying specific deformation:
            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')

        # Performing a mix of round left and right, but with edges:
        if type == "front" and axis == "vertical":
            # DEBUG:
            ## print("ROUND FRONT VERTICAL")
            
            leftEdgeIndex, rightEdgeIndex = 0, 0
            vertexA, vertexB = None, None
            
            # Searching for left edge:
            for v in selectedVerts:
                # DEGUG:
                ## print("VERT: ", v.index, v.co)
                            
                # Checking for upper left vertex:
                if v.co[y] < center[y] and v.co[z] > center[z] and round(v.co[x]) == round(center[x]):
                    # DEBUG:
                    ## print("selecting upper left vertex = ", v.index)
                    vertexA = bpy.context.active_object.data.vertices[v.index]
                    
                # Checking for bottom left vertex:
                if v.co[y] < center[y] and v.co[z] < center[z] and round(v.co[x]) == round(center[x]):
                    # DEBUG:
                    ## print("selecting bottom left vertex = ", v.index)
                    vertexB = bpy.context.active_object.data.vertices[v.index]
                    
            bpy.ops.object.mode_set(mode = 'EDIT')
            
            # Checking if the vertex were found:
            if vertexA == None or vertexB ==None:
                # DEBUG:
                ## print("NONE: ", vertexA, vertexB)
                return
            
            for e in bpy.context.active_object.data.edges:
                # DEGUG: Printing edge keys:
                ## print("left edge keys: ", e.vertices[0], e.vertices[1])
                
                # Storing edge index:
                if (e.vertices[0] == vertexA.index and e.vertices[1] == vertexB.index) or (e.vertices[0] == vertexB.index and e.vertices[1] == vertexA.index):
                    # DEBUG:
                    ## print("left edge: ", e.index)
                    leftEdgeIndex = e.index
                    
            # Searching for right edge:
            for v in selectedVerts:
                # DEGUG:
                ## print(v.co, center)
                            
                # Checking for upper right vertex:
                if v.co[y] > center[y] and v.co[z] > center[z] and round(v.co[x]) == round(center[x]):
                    # DEBUG:
                    ## print("selecting upper right vertex = ", v.index)
                    vertexA = bpy.context.active_object.data.vertices[v.index]
                    
                # Checking for bottom right vertex:
                if v.co[y] > center[y] and v.co[z] < center[z] and round(v.co[x]) == round(center[x]):
                    # DEBUG:
                    ## print("selecting bottom right vertex = ", v.index)
                    vertexB = bpy.context.active_object.data.vertices[v.index]
                    
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_mode(type="EDGE")
            
            for e in bpy.context.active_object.data.edges:
                # DEGUG: Printing edge keys:
                ## print("right edge keys: ", e.vertices[0], e.vertices[1])

                # Storing edge index:
                if (e.vertices[0] == vertexA.index and e.vertices[1] == vertexB.index) or (e.vertices[0] == vertexB.index and e.vertices[1] == vertexA.index):
                    # DEBUG:
                    ## print("right edge: ", e.index)
                    rightEdgeIndex = e.index
                    
            # Selecting edges:
            bpy.ops.object.mode_set(mode = 'OBJECT')

            # Selecting internal edges:
            bpy.context.active_object.data.edges[leftEdgeIndex].select = True
            bpy.context.active_object.data.edges[rightEdgeIndex].select = True
            
            bpy.ops.object.mode_set(mode = 'EDIT')
            
            # Applying specific deformation:
            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')
            
        # Performing a mix of round top and bottom, but with edges:
        if type == "front" and axis == "horizontal":
            # DEBUG:
            ## print("ROUND FRONT HORIZONTAL")
            
            topEdgeIndex, bottomEdgeIndex = 0, 0
            vertexA, vertexB = None, None
            
            # Searching for top edge:
            for v in selectedVerts:
                # DEGUG:
                ## print(v.co, center)
                            
                # Checking for upper left vertex:
                if v.co[y] < center[y] and v.co[z] > center[z] and math.floor(v.co[x]) == math.floor(center[x]):
                    # DEBUG:
                    ## print("selecting upper left vertex = ", v.index)
                    vertexA = bpy.context.active_object.data.vertices[v.index]
                    
                # Checking for upper right vertex:
                if v.co[y] > center[y] and v.co[z] > center[z] and math.floor(v.co[x]) == math.floor(center[x]):
                    # DEBUG:
                    ## print("selecting upper right vertex = ", v.index)
                    vertexB = bpy.context.active_object.data.vertices[v.index]
                    
            bpy.ops.object.mode_set(mode = 'EDIT')
            
            # Checking if the vertex were found:
            if vertexA == None or vertexB ==None:
                # DEBUG:
                ## print("NONE: ", vertexA, vertexB)
                return
            
            for e in bpy.context.active_object.data.edges:
                # DEGUG: Printing edge keys:
                ## print("left edge keys: ", e.vertices[0], e.vertices[1])
                
                # Storing edge index:
                if (e.vertices[0] == vertexA.index and e.vertices[1] == vertexB.index) or (e.vertices[0] == vertexB.index and e.vertices[1] == vertexA.index):
                    # DEBUG:
                    ## print("top edge: ", e.index)
                    topEdgeIndex = e.index
                    
            # Searching for bottom edge:
            for v in selectedVerts:
                # DEGUG:
                ## print(v.co, center)
                            
                # Checking for bottom left vertex:
                if v.co[y] < center[y] and v.co[z] < center[z] and math.floor(v.co[x]) == math.floor(center[x]):
                    # DEBUG:
                    ## print("selecting bottom left vertex = ", v.index)
                    vertexA = bpy.context.active_object.data.vertices[v.index]
                    
                # Checking for bottom right vertex:
                if v.co[y] > center[y] and v.co[z] < center[z] and math.floor(v.co[x]) == math.floor(center[x]):
                    # DEBUG:
                    ## print("selecting bottom right vertex = ", v.index)
                    vertexB = bpy.context.active_object.data.vertices[v.index]
                    
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_mode(type="EDGE")
            
            for e in bpy.context.active_object.data.edges:
                # DEGUG: Printing edge keys:
                ## print("right edge keys: ", e.vertices[0], e.vertices[1])

                # Storing edge index:
                if (e.vertices[0] == vertexA.index and e.vertices[1] == vertexB.index) or (e.vertices[0] == vertexB.index and e.vertices[1] == vertexA.index):
                    # DEBUG:
                    ## print("bottom edge: ", e.index)
                    bottomEdgeIndex = e.index
                    
            # Selecting edges:
            bpy.ops.object.mode_set(mode = 'OBJECT')

            # Selecting internal edges:
            bpy.context.active_object.data.edges[topEdgeIndex].select = True
            bpy.context.active_object.data.edges[bottomEdgeIndex].select = True
            
            # Applying deformation:
            bpy.ops.object.mode_set(mode = 'EDIT')

            # Applying specific deformation:
            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')

        
########################################################################################################
# $ INPUT STREAM MODULE
########################################################################################################

# Used for loading mass model settings:
def loadSettings(data):
    # Splitting assignments into tokens:
    settings = data.split(";")
    
    tokens = []
    
    # Retrieving each parameter:
    for setting in settings:
        tokens.append(setting.split("="))
    
    # Storing values after removing empty spaces:
    label = tokens[0][1].strip().replace('"', "")
    width = tokens[1][1].strip()
    depth = tokens[2][1].strip()
    height = tokens[3][1].strip()
    
    # DEGUG - Printing model settings:
    print("# settings: ", label, float(width), float(depth), float(height))
    
    createShape(root, label, float(width), float(depth), float(height))


# Used for creating mass model:
def loadCreateShape(root, label, width, depth, height):
    # DEBUG - Printing createShape parameters:
    print("# createShape(): ", root, label, width, depth, height)


# Used for creating and positioning virtual shape:
def loadCreateGrid(data):
    # Splitting selection expressions and action into tokens:
    selection, action = data.split("->")
    
    # Retrieving labels from 'selection':
    selectionLabels = selection.split('"')[1::2]
    
    # Retrieving each parameter separately:
    label, rows, columns = action[action.find("(")+1:action.find(")")].split(", ")
    
    label = label.replace('"', "")
    
    # DEBUG - Printing createGrid parameters:
    print("# createGrid(): ", selectionLabels, label, int(rows), int(columns))
    
    ## Passing labels to function responsible for selecting the object from shape tree:
    side = selectNode(root, selectionLabels)
    
    virtualShape = createGrid(label, side, int(rows), int(columns))
    
    placeMainVirtualShape(side, virtualShape)


# Used for extruding region from the mass model:
def loadAddVolume(data):
    # Splitting selection expressions and action into tokens:
    selection, action = data.split("->")
    
    # Retrieving labels from 'selection':
    selectionLabels = selection.split('"')[1::2]
    
    # Removing element 'cell':
    selectionLabels.pop()
    
    # Sepatating list of rows and columns:
    rowsIndices, columnsIndices = re.findall('\(([^)]+)', selection)
    
    # Converting rows to list of integers:
    if "indexRange" in rowsIndices:
        # Extracting range numbers from the string:
        r = list(map(int, re.findall(r'\d+', rowsIndices)))
        
        # DEBUG:
        ## print("ROWS = indexRange(): ", r)
        
        # Generating list with the given range:
        rows = rangeIndex(r[0], r[-1]+1)
    else:
        # Extracting indices from the string:        
        rows = [int(i) for i in rowsIndices.split(', ')]
        
    # Converting columns to list of integers:
    if "indexRange" in columnsIndices:
        # Extracting range numbers from the string:
        c = list(map(int, re.findall(r'\d+', columnsIndices)))
        
        # DEBUG:
        ## print("COLS = indexRange(): ", c)

        # Generating list with the given range:
        columns = rangeIndex(c[0], c[-1]+1)
    else:
        # Extracting indices from the string:
        columns = [int(i) for i in columnsIndices.split(', ')]
    
    # Retrieving content inside parenthesis:
    actionContent = re.findall('\(([^)]+)', action)[0]
    
    # Retrieving elements separately:
    label, parentLabel, extrusionSize, frontLabel, leftLabel, rightLabel = actionContent.split(", ")
    
    label = label.replace('"', "")
    parentLabel = parentLabel.replace('"', "")
    
    sideLabels = []
    
    sideLabels.append(frontLabel.replace('"', "").replace("[", ""))
    sideLabels.append(leftLabel.replace('"', ""))
    sideLabels.append(rightLabel.replace('"', "").replace("]", ""))
    
    # DEBUG - Printing addVolume parameters:
    print("# addVolume(): ", selectionLabels, rows, columns, label, parentLabel, float(extrusionSize), sideLabels)
    
    # Passing labels to function responsible for selecting the object from shape tree:
    grid = selectNode(root, selectionLabels)
    
    # Creating grid copy to be used as selection tool:
    gridCopy = duplicateShape(grid.getLabel())
    
    gridCopyNode = Virtual(gridCopy.name, gridCopy, grid.getParent(), grid.getRows()+1, grid.getColumns()+1)
    
    # Selecting cells from the grid:
    selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rows, columns)

    # Retrieving object reference:
    parent = gridCopyNode.getParent()
    
    # Extra parameter for selecting objects properly:
    gridLabel = gridCopyNode.getLabel()
    
    # Adding volume to the mass model and retrieving face index to apply deformation:
    regionIndex = addVolume(label, parent, float(extrusionSize), sideLabels, gridLabel, len(rows), len(columns))
    
    return regionIndex


# Used for applying deformation to the mass model:
def loadRoundShape(data, regionIndex):
    # Splitting selection expressions and action into tokens:
    selection, action = data.split("->")
    
    # Retrieving labels from 'selection':
    selectionLabels = selection.split('"')[1::2]
    
    # Retrieving content inside parenthesis:
    actionContent = re.findall('\(([^)]+)', action)[0]
    
    actionParameters = actionContent.split(", ")
    
    # Checking for rounding type:
    if len(actionParameters) == 5:
        # DEBUG - Printing rouding type:
        print("Single side outside rounding")  
        
        type = actionParameters[0].replace('"', "")
        direction = actionParameters[1].replace('"', "")
        roundingDegree = float(actionParameters[2])
        segments = int(actionParameters[3])
        sideReference = actionParameters[4].replace('"', "")
        
        # DEBUG - Printing roundShape parameters:
        print("# roundShape(): ", type, direction, roundingDegree, segments, sideReference)
        
        # Changing select mode:
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_mode(type = 'FACE')
        bpy.ops.mesh.select_all(action = 'DESELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')

        # Retrieving model mass region to apply the deformation:
        region = bpy.data.objects[selectionLabels[0]].data.polygons[regionIndex]

        # Applying deformation:
        roundShape(region, type, direction, roundingDegree, segments, sideReference)       
        
    elif len(actionParameters) == 6:
        
        direction = actionParameters[1].replace('"', "")
        
        if direction == "outside":
            # DEBUG - Printing rouding type:
            print("Frontal outside rounding")
            
            type = actionParameters[0].replace('"', "")
            roundingDegree = float(actionParameters[2])
            segments = int(actionParameters[3])
            sideReference = actionParameters[4].replace('"', "")
            axis = actionParameters[5].replace('"', "")
            
            # DEBUG - Printing roundShape parameters:
            print("# roundShape(): ", type, direction, roundingDegree, segments, sideReference, axis)
            
            # Changing select mode:
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_mode(type = 'FACE')
            bpy.ops.mesh.select_all(action = 'DESELECT')
            bpy.ops.object.mode_set(mode = 'OBJECT')

            # Retrieving model mass region to apply the deformation:
            region = bpy.data.objects[selectionLabels[0]].data.polygons[regionIndex]

            # Applying deformation:
            roundShape(region, type, direction, roundingDegree, segments, sideReference, axis)
        
        elif direction == "inside":
            # DEBUG - Printing rouding type:
            print("Single side inside rounding")
            
            type = actionParameters[0].replace('"', "")
            roundingDegree = float(actionParameters[2])
            segments = int(actionParameters[3])
            sideReference = actionParameters[4].replace('"', "")
            insideDegree = float(actionParameters[5])
            
            # DEBUG - Printing roundShape parameters:
            print("# roundShape(): ", type, direction, roundingDegree, segments, sideReference, insideDegree)
            
            # Changing select mode:
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_mode(type = 'FACE')
            bpy.ops.mesh.select_all(action = 'DESELECT')
            bpy.ops.object.mode_set(mode = 'OBJECT')

            # Retrieving model mass region to apply the deformation:
            region = bpy.data.objects[selectionLabels[0]].data.polygons[regionIndex]

            # Applying deformation:
            roundShape(region, type, direction, roundingDegree, segments, sideReference, insideDegree)
            
    elif len(actionParameters) == 7:
        # DEBUG - Printing rouding type:
        print("Frontal inside rounding")
        
        type = actionParameters[0].replace('"', "")
        direction = actionParameters[1].replace('"', "")
        roundingDegree = float(actionParameters[2])
        segments = int(actionParameters[3])
        sideReference = actionParameters[4].replace('"', "")
        axis = actionParameters[5].replace('"', "")
        insideDegree = float(actionParameters[6])
        
        # DEBUG - Printing roundShape parameters:
        print("# roundShape(): ", type, direction, roundingDegree, segments, sideReference, axis, insideDegree)
        
        # Changing select mode:
        bpy.ops.object.mode_set(mode = 'EDIT')
        bpy.ops.mesh.select_mode(type = 'FACE')
        bpy.ops.mesh.select_all(action = 'DESELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')

        # Retrieving model mass region to apply the deformation:
        region = bpy.data.objects[selectionLabels[0]].data.polygons[regionIndex]

        # Applying deformation:
        roundShape(region, type, direction, roundingDegree, segments, sideReference, axis, insideDegree)
        

# Used to compute instructions by calling its propor function:
def computeInstructions(rules):
    # Auxiliary variable to help selecting shape for applying deformation after extrusion:
    regionIndex = 0
        
    for index, rule in enumerate(rules):
        if index == 0:
            loadSettings(rule)
            
        if "createShape" in rule:
            print("# createShape: Ran right after loadSettings()")
        
        if "createGrid" in rule:
            loadCreateGrid(rule)
        
        if "addVolume" in rule:
            regionIndex = loadAddVolume(rule)
            
        if "roundShape" in rule:
            loadRoundShape(rule, regionIndex)
            
        print()


########################################################################################################
# $ FILE MODULE
########################################################################################################

# Used for reading the file containing the rules:
def readFile():

    # Retrieving Blender project location:
    filepath = bpy.data.filepath
    directory = os.path.dirname(filepath)

    # Reading rules from file present at the same location as the project:
    readfile = open(os.path.join(directory, INPUT_FILE_NAME), "r")

    # Storing each line inside a list:
    arr = readfile.readlines()

    readfile.close()

    # List to store just the rules:
    filteredRules = []

    # Removing comments and blank lines:
    for line in arr:
        filteredRules = [line.strip() for line in arr if line.strip() and "#" not in line]
          
    computeInstructions(filteredRules)
 
       
########################################################################################################
# $ EXECUTION MODULE
########################################################################################################

# Used for initialization:
def main():
    
    # DEBUG - Cleaning debugging logs before execution:
    os.system("clear")
    
    # Removing objects of the scene:
    resetScene()
    
    # Read file containing SELEX rules:
    readFile()
    
    # Checking if user decided to hide the virtual shapes:
    if HIDE_VIRTUAL_SHAPES:
        hideVirtualShapes()

    # Checking if user decided to remove the virtual shapes:
    if REMOVE_VIRTUAL_SHAPES:
        removeVirtualShapes()

if __name__ == "__main__":
    main()