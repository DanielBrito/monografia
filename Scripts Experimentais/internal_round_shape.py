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
    
    # Retrieving frontal polygon index:
    return regionIndex + 1


''' Function to group selected cells: '''

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
    

''' Applying deformation to a given object: '''

def roundShape(object, type, direction, roundingDegree, segments, sideReference, axis="", insideDegree=0):
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
    
    if sideReference == "main_front":
        # Round left:
        if type == "left":
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
            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')
             
        # Round right:       
        if type == "right":
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
            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')
        
        # Round top:
        if type == "top":
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
            # Applying deformation:
            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')
         
        # Round bottom:   
        if type == "bottom":
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
            # Applying deformation:
            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')

        # Performing a mix of round left and right, but with edges:
        if type == "front" and axis == "vertical":
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
            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')
            
        # Performing a mix of round top and bottom, but with edges:
        if type == "front" and axis == "horizontal":
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

            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')
            
    if sideReference == "main_back":
        # Round left:
        if type == "left":
            # DEBUG:
            print("ROUND LEFT")
                
            for v in selectedVerts:
                # DEBUG:
                # print(v.co, center)
                            
                # Checking for upper left vertex:
                if v.co[x] > center[x] and v.co[z] > center[z]:
                    print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True
                    
                # Checking for bottom left vertex:
                if v.co[x] > center[x] and v.co[z] < center[z]:
                    print("selecting vertex = ", v.index)
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
             
        # Round right:       
        if type == "right":
            # DEBUG:
            print("ROUND RIGHT")
                
            for v in selectedVerts:
                # DEBUG:
                # print(v.co, center)
                            
                # Checking for upper right vertex:
                if v.co[x] < center[x] and v.co[z] > center[z]:
                    print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True
                    
                # Checking for bottom right vertex:
                if v.co[x] < center[x] and v.co[z] < center[z]:
                    print("selecting vertex = ", v.index)
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
        
        # Round top:
        if type == "top":
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
            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')
         
        # Round bottom:   
        if type == "bottom":
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
            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')

        # Performing a mix of round left and right, but with edges:
        if type == "front" and axis == "vertical":
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
            
            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')
            
        # Performing a mix of round top and bottom, but with edges:
        if type == "front" and axis == "horizontal":
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

            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')
            

    if sideReference == "main_left":
        # Round left:
        if type == "left":
            # DEBUG:
            print("ROUND LEFT")
                
            for v in selectedVerts:
                # DEBUG:
                # print(v.co, center)
                            
                # Checking for upper left vertex:
                if v.co[y] > center[y] and v.co[z] > center[z]:
                    print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True
                    
                # Checking for bottom left vertex:
                if v.co[y] > center[y] and v.co[z] < center[z]:
                    print("selecting vertex = ", v.index)
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
             
        # Round right:       
        if type == "right":
            # DEBUG:
            print("ROUND RIGHT")
                
            for v in selectedVerts:
                # DEBUG:
                # print(v.co, center)
                            
                # Checking for upper right vertex:
                if v.co[y] < center[y] and v.co[z] > center[z]:
                    print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True
                    
                # Checking for bottom right vertex:
                if v.co[y] < center[y] and v.co[z] < center[z]:
                    print("selecting vertex = ", v.index)
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
        
        # Round top:
        if type == "top":
            # DEBUG:
            print("ROUND TOP")
                
            for v in selectedVerts:
                # DEBUG:
                # print(v.co, center)
                            
                # Checking for upper left vertex:
                if v.co[y] > center[y] and v.co[z] > center[z]:
                    print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True
                    
                # Checking for upper right vertex:
                if v.co[y] < center[y] and v.co[z] > center[z]:
                    print("selecting vertex = ", v.index)
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
            print("ROUND BOTTOM")
                
            for v in selectedVerts:
                # DEBUG:
                # print(v.co, center)
                            
                # Checking for bottom left vertex:
                if v.co[y] > center[y] and v.co[z] < center[z]:
                    print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True
                    
                # Checking for bottom right vertex:
                if v.co[y] < center[y] and v.co[z] < center[z]:
                    print("selecting vertex = ", v.index)
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
            print("ROUND FRONT VERTICAL")
            
            leftEdgeIndex, rightEdgeIndex = 0, 0
            vertexA, vertexB = None, None
            
            # Searching for left edge:
            for v in selectedVerts:
                # DEGUG:
                # print("VERT: ", v.index, v.co)
                            
                # Checking for upper left vertex:
                if v.co[y] > center[y] and v.co[z] > center[z] and round(v.co[x]) == round(center[x]):
                    print("selecting upper left vertex = ", v.index)
                    vertexA = bpy.context.active_object.data.vertices[v.index]
                    
                # Checking for bottom left vertex:
                if v.co[y] > center[y] and v.co[z] < center[z] and round(v.co[x]) == round(center[x]):
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
                if v.co[y] < center[y] and v.co[z] > center[z] and round(v.co[x]) == round(center[x]):
                    print("selecting upper right vertex = ", v.index)
                    vertexA = bpy.context.active_object.data.vertices[v.index]
                    
                # Checking for bottom right vertex:
                if v.co[y] < center[y] and v.co[z] < center[z] and round(v.co[x]) == round(center[x]):
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

            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')
            
        # Performing a mix of round top and bottom, but with edges:
        if type == "front" and axis == "horizontal":
            # DEBUG:
            print("ROUND FRONT HORIZONTAL")
            
            topEdgeIndex, bottomEdgeIndex = 0, 0
            vertexA, vertexB = None, None
            
            # Searching for top edge:
            for v in selectedVerts:
                # DEGUG:
                # print(v.co, center)
                            
                # Checking for upper left vertex:
                if v.co[y] > center[y] and v.co[z] > center[z] and round(v.co[x]) == round(center[x]):
                    print("selecting upper left vertex = ", v.index)
                    vertexA = bpy.context.active_object.data.vertices[v.index]
                    
                # Checking for upper right vertex:
                if v.co[y] < center[y] and v.co[z] > center[z] and round(v.co[x]) == round(center[x]):
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
                if v.co[y] > center[y] and v.co[z] < center[z] and round(v.co[x]) == round(center[x]):
                    print("selecting bottom left vertex = ", v.index)
                    vertexA = bpy.context.active_object.data.vertices[v.index]
                    
                # Checking for bottom right vertex:
                if v.co[y] < center[y] and v.co[z] < center[z] and round(v.co[x]) == round(center[x]):
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

            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')
            
            
    if sideReference == "main_right":
        # Round left:
        if type == "left":
            # DEBUG:
            print("ROUND LEFT")
                
            for v in selectedVerts:
                # DEBUG:
                # print(v.co, center)
                            
                # Checking for upper left vertex:
                if v.co[y] < center[y] and v.co[z] > center[z]:
                    print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True
                    
                # Checking for bottom left vertex:
                if v.co[y] < center[y] and v.co[z] < center[z]:
                    print("selecting vertex = ", v.index)
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
             
        # Round right:       
        if type == "right":
            # DEBUG:
            print("ROUND RIGHT")
                
            for v in selectedVerts:
                # DEBUG:
                # print(v.co, center)
                            
                # Checking for upper right vertex:
                if v.co[y] > center[y] and v.co[z] > center[z]:
                    print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True
                    
                # Checking for bottom right vertex:
                if v.co[y] > center[y] and v.co[z] < center[z]:
                    print("selecting vertex = ", v.index)
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
        
        # Round top:
        if type == "top":
            # DEBUG:
            print("ROUND TOP")
                
            for v in selectedVerts:
                # DEBUG:
                # print(v.co, center)
                            
                # Checking for upper left vertex:
                if v.co[y] < center[y] and v.co[z] > center[z]:
                    print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True
                    
                # Checking for upper right vertex:
                if v.co[y] > center[y] and v.co[z] > center[z]:
                    print("selecting vertex = ", v.index)
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
            print("ROUND BOTTOM")
                
            for v in selectedVerts:
                # DEBUG:
                # print(v.co, center)
                            
                # Checking for bottom left vertex:
                if v.co[y] < center[y] and v.co[z] < center[z]:
                    print("selecting vertex = ", v.index)
                    bpy.context.active_object.data.vertices[v.index].select = True
                    
                # Checking for bottom right vertex:
                if v.co[y] > center[y] and v.co[z] < center[z]:
                    print("selecting vertex = ", v.index)
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
            print("ROUND FRONT VERTICAL")
            
            leftEdgeIndex, rightEdgeIndex = 0, 0
            vertexA, vertexB = None, None
            
            # Searching for left edge:
            for v in selectedVerts:
                # DEGUG:
                # print("VERT: ", v.index, v.co)
                            
                # Checking for upper left vertex:
                if v.co[y] < center[y] and v.co[z] > center[z] and round(v.co[x]) == round(center[x]):
                    print("selecting upper left vertex = ", v.index)
                    vertexA = bpy.context.active_object.data.vertices[v.index]
                    
                # Checking for bottom left vertex:
                if v.co[y] < center[y] and v.co[z] < center[z] and round(v.co[x]) == round(center[x]):
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
                if v.co[y] > center[y] and v.co[z] > center[z] and round(v.co[x]) == round(center[x]):
                    print("selecting upper right vertex = ", v.index)
                    vertexA = bpy.context.active_object.data.vertices[v.index]
                    
                # Checking for bottom right vertex:
                if v.co[y] > center[y] and v.co[z] < center[z] and round(v.co[x]) == round(center[x]):
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

            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')
            
        # Performing a mix of round top and bottom, but with edges:
        if type == "front" and axis == "horizontal":
            # DEBUG:
            print("ROUND FRONT HORIZONTAL")
            
            topEdgeIndex, bottomEdgeIndex = 0, 0
            vertexA, vertexB = None, None
            
            # Searching for top edge:
            for v in selectedVerts:
                # DEGUG:
                # print(v.co, center)
                            
                # Checking for upper left vertex:
                if v.co[y] < center[y] and v.co[z] > center[z] and round(v.co[x]) == round(center[x]):
                    print("selecting upper left vertex = ", v.index)
                    vertexA = bpy.context.active_object.data.vertices[v.index]
                    
                # Checking for upper right vertex:
                if v.co[y] > center[y] and v.co[z] > center[z] and round(v.co[x]) == round(center[x]):
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
                if v.co[y] < center[y] and v.co[z] < center[z] and round(v.co[x]) == round(center[x]):
                    print("selecting bottom left vertex = ", v.index)
                    vertexA = bpy.context.active_object.data.vertices[v.index]
                    
                # Checking for bottom right vertex:
                if v.co[y] > center[y] and v.co[z] < center[z] and round(v.co[x]) == round(center[x]):
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

            # Applying deformation:
            if direction == "outside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False)
            elif direction == "inside":
                bpy.ops.mesh.bevel(offset=roundingDegree, offset_pct=0, segments=segments, vertex_only=False, profile=insideDegree)
            
            bpy.ops.object.mode_set(mode = 'OBJECT')
        
          
########################################################################

''' ---------------------- RESETING THE SCENE: ---------------------- '''
    
if len(bpy.context.scene.objects) > 0:
    bpy.ops.object.mode_set(mode = "OBJECT")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    
    # Cleaning debugging logs:
    os.system("clear")

########################################################################

''' ------------------- SIMULATING SELEX RULES: ---------------------- '''

# Defining shape tree root node:
root = Node("root", None, None, None)

# Simulating list traversal and rules execution:

# Default rule for defining mass model characteristics:
''' #C1 '''

# TESTING -> Simulating data for initial settings:
label = "building"
width = 9
depth = 11
height = 10


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
# VIRTUAL SHAPES
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
label = "main_grid_front"
rows = 3
columns = 6

virtualShape = createGrid(label, side, rows, columns)

placeMainVirtualShape(side, virtualShape)

# -------------------------------------------------------------------------------

# TESTING 2 -> Simulating data for generated list of labels:
labels_back = ["building", "building_back"]

## Passing labels to function responsible for selecting the object from shape tree:
side = selectNode(root, labels_back)

# TESTING -> Simulating data for label and number of rows/columns:
label = "main_grid_back"
rows = 3
columns = 6

virtualShape = createGrid(label, side, rows, columns)

placeMainVirtualShape(side, virtualShape)

# -------------------------------------------------------------------------------

# TESTING 3 -> Simulating data for generated list of labels:
labels_left = ["building", "building_left"]

## Passing labels to function responsible for selecting the object from shape tree:
side = selectNode(root, labels_left)

# TESTING -> Simulating data for label and number of rows/columns:
label = "main_grid_left"
rows = 3
columns = 6

virtualShape = createGrid(label, side, rows, columns)

placeMainVirtualShape(side, virtualShape)

# -------------------------------------------------------------------------------

# TESTING 4 -> Simulating data for generated list of labels:
labels_right = ["building", "building_right"]

## Passing labels to function responsible for selecting the object from shape tree:
side = selectNode(root, labels_right)

# TESTING -> Simulating data for label and number of rows/columns:
label = "main_grid_right"
rows = 3
columns = 6

virtualShape = createGrid(label, side, rows, columns)

placeMainVirtualShape(side, virtualShape)


# -------------------------------------------------------------------------------
# ROUND FRONT
# -------------------------------------------------------------------------------

# TESTING 1 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_front", "main_grid_front"]
rowsIndex = [1, 2, 3]
columnsIndex = [1]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "entrance_1"
parent = gridCopyNode.getParent()
extrusionSize = 3
sidesLabels = [label + "_front", label + "_left", label + "_right"]
sideReference = "main_front"

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model and retrieving face index to apply deformation:
regionIndex = addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)

       
# TESTING -> Simulating data for labels, degree, segments, type and axis:
labels = ["building", "building_front", "entrance_1", "entrance_1_front"]
roundingDegree = 0.16 # (width / num_columns) / num_columns
numberSegments = 30
deformationType = "left" # front | left | right | bottom | top
deformationAxis = "vertical" # frontal deformation: vertical | horizontal
direction = "inside"
insideDegree = roundingDegree/2

# Changing select mode:
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_mode(type = 'FACE')
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Retrieving model mass region to apply the deformation:
region = bpy.data.objects[labels[0]].data.polygons[regionIndex]

# Applying deformation:
roundShape(region, deformationType, direction, roundingDegree, numberSegments, sideReference, deformationAxis, insideDegree)

# -------------------------------------------------------------------------------

# TESTING 2 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_front", "main_grid_front"]
rowsIndex = [1]
columnsIndex = [2]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "entrance_2_1"
parent = gridCopyNode.getParent()
extrusionSize = 1
sidesLabels = [label + "_front", label + "_left", label + "_right"]
sideReference = "main_front"

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model and retrieving face index to apply deformation:
regionIndex = addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)

       
# TESTING -> Simulating data for labels, degree, segments, type and axis:
labels = ["building", "building_front", "entrance_2_1", "entrance_2_1_front"]
roundingDegree = 0.2
numberSegments = 30
deformationType = "bottom" # front | left | right | bottom | top
deformationAxis = "horizontal" # frontal deformation: vertical | horizontal
direction = "inside"
insideDegree = 0.1

# Changing select mode:
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_mode(type = 'FACE')
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Retrieving model mass region to apply the deformation:
region = bpy.data.objects[labels[0]].data.polygons[regionIndex]

# Applying deformation:
roundShape(region, deformationType, direction, roundingDegree, numberSegments, sideReference, deformationAxis, roundingDegree)

# -------------------------------------------------------------------------------

# TESTING 2.1 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_front", "main_grid_front"]
rowsIndex = [2]
columnsIndex = [2]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "entrance_2_2"
parent = gridCopyNode.getParent()
extrusionSize = 1
sidesLabels = [label + "_front", label + "_left", label + "_right"]
sideReference = "main_front"

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model and retrieving face index to apply deformation:
regionIndex = addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)

       
# TESTING -> Simulating data for labels, degree, segments, type and axis:
labels = ["building", "building_front", "entrance_2_2", "entrance_2_2_front"]
roundingDegree = 0.3
numberSegments = 30
deformationType = "front" # front | left | right | bottom | top
deformationAxis = "horizontal" # frontal deformation: vertical | horizontal
direction = "inside"
insideDegree = 0.1

# Changing select mode:
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_mode(type = 'FACE')
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Retrieving model mass region to apply the deformation:
region = bpy.data.objects[labels[0]].data.polygons[regionIndex]

# Applying deformation:
roundShape(region, deformationType, direction, roundingDegree, numberSegments, sideReference, deformationAxis, insideDegree)

# -------------------------------------------------------------------------------

# TESTING 2.2 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_front", "main_grid_front"]
rowsIndex = [3]
columnsIndex = [2]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "entrance_2_3"
parent = gridCopyNode.getParent()
extrusionSize = 1
sidesLabels = [label + "_front", label + "_left", label + "_right"]
sideReference = "main_front"

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model and retrieving face index to apply deformation:
regionIndex = addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)

       
# TESTING -> Simulating data for labels, degree, segments, type and axis:
labels = ["building", "building_front", "entrance_2_3", "entrance_2_3_front"]
roundingDegree = 0.2
numberSegments = 30
deformationType = "top" # front | left | right | bottom | top
deformationAxis = "horizontal" # frontal deformation: vertical | horizontal
direction = "inside"
insideDegree = 0.1

# Changing select mode:
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_mode(type = 'FACE')
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Retrieving model mass region to apply the deformation:
region = bpy.data.objects[labels[0]].data.polygons[regionIndex]

# Applying deformation:
roundShape(region, deformationType, direction, roundingDegree, numberSegments, sideReference, deformationAxis, insideDegree)

# -------------------------------------------------------------------------------

# TESTING 3 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_front", "main_grid_front"]
rowsIndex = [1, 2, 3]
columnsIndex = [3]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "entrance_3"
parent = gridCopyNode.getParent()
extrusionSize = 2
sidesLabels = [label + "_front", label + "_left", label + "_right"]
sideReference = "main_front"

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model and retrieving face index to apply deformation:
regionIndex = addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)

       
# TESTING -> Simulating data for labels, degree, segments, type and axis:
labels = ["building", "building_front", "entrance_3", "entrance_3_front"]
roundingDegree = 0.16 # (width / num_columns) / num_columns
numberSegments = 30
deformationType = "left" # front | left | right | bottom | top
deformationAxis = "vertical" # frontal deformation: vertical | horizontal
direction = "outside"

# Changing select mode:
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_mode(type = 'FACE')
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Retrieving model mass region to apply the deformation:
region = bpy.data.objects[labels[0]].data.polygons[regionIndex]

# Applying deformation:
roundShape(region, deformationType, direction, roundingDegree, numberSegments, sideReference, deformationAxis)


# TESTING 4 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_front", "main_grid_front"]
rowsIndex = [3]
columnsIndex = [4, 5, 6]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "entrance_4"
parent = gridCopyNode.getParent()
extrusionSize = 5
sidesLabels = [label + "_front", label + "_left", label + "_right"]
sideReference = "main_front"

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model and retrieving face index to apply deformation:
regionIndex = addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)


# TESTING -> Simulating data for labels, degree, segments, type and axis:
labels = ["building", "building_front", "entrance_4", "entrance_4_"]
roundingDegree = 0.4
numberSegments = 30
deformationType = "front" # front | left | right | bottom | top
deformationAxis = "vertical" # frontal deformation: vertical | horizontal
direction = "inside"
insideDegree = 0.1

# Changing select mode:
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_mode(type = 'FACE')
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Retrieving model mass region to apply the deformation:
region = bpy.data.objects[labels[0]].data.polygons[regionIndex]

# Applying deformation:
roundShape(region, deformationType, direction, roundingDegree, numberSegments, sideReference, deformationAxis, insideDegree)

# -------------------------------------------------------------------------------

# TESTING 5 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_front", "main_grid_front"]
rowsIndex = [1, 2]
columnsIndex = [4, 5, 6]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "entrance_top"
parent = gridCopyNode.getParent()
extrusionSize = 2
sidesLabels = [label + "_front", label + "_left", label + "_right"]
sideReference = "main_front"

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model and retrieving face index to apply deformation:
regionIndex = addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)

       
# TESTING -> Simulating data for labels, degree, segments, type and axis:
labels = ["building", "building_front", "entrance_top", "entrance_top_front"]
roundingDegree = 0.48
numberSegments = 30
deformationType = "right" # front | left | right | bottom | top
deformationAxis = "vertical" # frontal deformation: vertical | horizontal
direction = "inside"
insideDegree = 0.1

# Changing select mode:
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_mode(type = 'FACE')
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Retrieving model mass region to apply the deformation:
region = bpy.data.objects[labels[0]].data.polygons[regionIndex]

# Applying deformation:
roundShape(region, deformationType, direction, roundingDegree, numberSegments, sideReference, deformationAxis, insideDegree)


# -------------------------------------------------------------------------------
# ROUND BACK
# -------------------------------------------------------------------------------

# TESTING 1 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_back", "main_grid_back"]
rowsIndex = [1, 2, 3]
columnsIndex = [1]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "backyard_1"
parent = gridCopyNode.getParent()
extrusionSize = 3
sidesLabels = [label + "_front", label + "_left", label + "_right"]
sideReference = "main_back"

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model and retrieving face index to apply deformation:
regionIndex = addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)

       
# TESTING -> Simulating data for labels, degree, segments, type and axis:
labels = ["building", "building_back", "backyard_1", "backyard_1_front"]
roundingDegree = 0.16 # (width / num_columns) / num_columns
numberSegments = 30
deformationType = "left" # front | left | right | bottom | top
deformationAxis = "vertical" # frontal deformation: vertical | horizontal
direction = "inside"
insideDegree = roundingDegree/2

# Changing select mode:
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_mode(type = 'FACE')
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Retrieving model mass region to apply the deformation:
region = bpy.data.objects[labels[0]].data.polygons[regionIndex]

# Applying deformation:
roundShape(region, deformationType, direction, roundingDegree, numberSegments, sideReference, deformationAxis, insideDegree)

# -------------------------------------------------------------------------------

# TESTING 2 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_back", "main_grid_back"]
rowsIndex = [1]
columnsIndex = [2]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "backyard_2_1"
parent = gridCopyNode.getParent()
extrusionSize = 1
sidesLabels = [label + "_front", label + "_left", label + "_right"]
sideReference = "main_back"

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model and retrieving face index to apply deformation:
regionIndex = addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)

       
# TESTING -> Simulating data for labels, degree, segments, type and axis:
labels = ["building", "building_back", "backyard_2_1", "backyard_2_1_front"]
roundingDegree = 0.2
numberSegments = 30
deformationType = "bottom" # front | left | right | bottom | top
deformationAxis = "horizontal" # frontal deformation: vertical | horizontal
direction = "inside"
insideDegree = 0.1

# Changing select mode:
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_mode(type = 'FACE')
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Retrieving model mass region to apply the deformation:
region = bpy.data.objects[labels[0]].data.polygons[regionIndex]

# Applying deformation:
roundShape(region, deformationType, direction, roundingDegree, numberSegments, sideReference, deformationAxis, roundingDegree)

# -------------------------------------------------------------------------------

# TESTING 2.1 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_back", "main_grid_back"]
rowsIndex = [2]
columnsIndex = [2]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "backyard_2_2"
parent = gridCopyNode.getParent()
extrusionSize = 1
sidesLabels = [label + "_front", label + "_left", label + "_right"]
sideReference = "main_back"

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model and retrieving face index to apply deformation:
regionIndex = addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)

       
# TESTING -> Simulating data for labels, degree, segments, type and axis:
labels = ["building", "building_back", "backyard_2_2", "backyard_2_2_front"]
roundingDegree = 0.3
numberSegments = 30
deformationType = "front" # front | left | right | bottom | top
deformationAxis = "horizontal" # frontal deformation: vertical | horizontal
direction = "inside"
insideDegree = 0.1

# Changing select mode:
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_mode(type = 'FACE')
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Retrieving model mass region to apply the deformation:
region = bpy.data.objects[labels[0]].data.polygons[regionIndex]

# Applying deformation:
roundShape(region, deformationType, direction, roundingDegree, numberSegments, sideReference, deformationAxis, insideDegree)

# -------------------------------------------------------------------------------

# TESTING 2.2 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_back", "main_grid_back"]
rowsIndex = [3]
columnsIndex = [2]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "backyard_2_3"
parent = gridCopyNode.getParent()
extrusionSize = 1
sidesLabels = [label + "_front", label + "_left", label + "_right"]
sideReference = "main_back"

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model and retrieving face index to apply deformation:
regionIndex = addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)

       
# TESTING -> Simulating data for labels, degree, segments, type and axis:
labels = ["building", "building_back", "backyard_2_3", "backyard_2_3_front"]
roundingDegree = 0.2
numberSegments = 30
deformationType = "top" # front | left | right | bottom | top
deformationAxis = "horizontal" # frontal deformation: vertical | horizontal
direction = "inside"
insideDegree = 0.1

# Changing select mode:
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_mode(type = 'FACE')
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Retrieving model mass region to apply the deformation:
region = bpy.data.objects[labels[0]].data.polygons[regionIndex]

# Applying deformation:
roundShape(region, deformationType, direction, roundingDegree, numberSegments, sideReference, deformationAxis, insideDegree)

# -------------------------------------------------------------------------------

# TESTING 3 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_back", "main_grid_back"]
rowsIndex = [1, 2, 3]
columnsIndex = [3]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "backyard_3"
parent = gridCopyNode.getParent()
extrusionSize = 2
sidesLabels = [label + "_front", label + "_left", label + "_right"]
sideReference = "main_back"

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model and retrieving face index to apply deformation:
regionIndex = addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)

       
# TESTING -> Simulating data for labels, degree, segments, type and axis:
labels = ["building", "building_back", "backyard_3", "backyard_3_front"]
roundingDegree = 0.16 # (width / num_columns) / num_columns
numberSegments = 30
deformationType = "left" # front | left | right | bottom | top
deformationAxis = "vertical" # frontal deformation: vertical | horizontal
direction = "outside"

# Changing select mode:
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_mode(type = 'FACE')
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Retrieving model mass region to apply the deformation:
region = bpy.data.objects[labels[0]].data.polygons[regionIndex]

# Applying deformation:
roundShape(region, deformationType, direction, roundingDegree, numberSegments, sideReference, deformationAxis)


# TESTING 4 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_back", "main_grid_back"]
rowsIndex = [3]
columnsIndex = [4, 5, 6]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "backyard_4"
parent = gridCopyNode.getParent()
extrusionSize = 5
sidesLabels = [label + "_front", label + "_left", label + "_right"]
sideReference = "main_back"

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model and retrieving face index to apply deformation:
regionIndex = addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)


# TESTING -> Simulating data for labels, degree, segments, type and axis:
labels = ["building", "building_back", "backyard_4", "backyard_4_"]
roundingDegree = 0.4
numberSegments = 30
deformationType = "front" # front | left | right | bottom | top
deformationAxis = "vertical" # frontal deformation: vertical | horizontal
direction = "inside"
insideDegree = 0.1

# Changing select mode:
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_mode(type = 'FACE')
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Retrieving model mass region to apply the deformation:
region = bpy.data.objects[labels[0]].data.polygons[regionIndex]

# Applying deformation:
roundShape(region, deformationType, direction, roundingDegree, numberSegments, sideReference, deformationAxis, insideDegree)

# -------------------------------------------------------------------------------

# TESTING 5 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_back", "main_grid_back"]
rowsIndex = [1, 2]
columnsIndex = [4, 5, 6]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "backyard_top"
parent = gridCopyNode.getParent()
extrusionSize = 2
sidesLabels = [label + "_front", label + "_left", label + "_right"]
sideReference = "main_back"

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model and retrieving face index to apply deformation:
regionIndex = addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)

       
# TESTING -> Simulating data for labels, degree, segments, type and axis:
labels = ["building", "building_back", "backyard_top", "backyard_top_front"]
roundingDegree = 0.48
numberSegments = 30
deformationType = "right" # front | left | right | bottom | top
deformationAxis = "vertical" # frontal deformation: vertical | horizontal
direction = "inside"
insideDegree = 0.1

# Changing select mode:
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_mode(type = 'FACE')
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Retrieving model mass region to apply the deformation:
region = bpy.data.objects[labels[0]].data.polygons[regionIndex]

# Applying deformation:
roundShape(region, deformationType, direction, roundingDegree, numberSegments, sideReference, deformationAxis, insideDegree)


# -------------------------------------------------------------------------------
# ROUND LEFT
# -------------------------------------------------------------------------------

# TESTING 1 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_left", "main_grid_left"]
rowsIndex = [1, 2, 3]
columnsIndex = [1]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "reception_1"
parent = gridCopyNode.getParent()
extrusionSize = 3
sidesLabels = [label + "_front", label + "_left", label + "_right"]
sideReference = "main_left"

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model and retrieving face index to apply deformation:
regionIndex = addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)

       
# TESTING -> Simulating data for labels, degree, segments, type and axis:
labels = ["building", "building_left", "reception_1", "reception_1_front"]
roundingDegree = 0.16 # (width / num_columns) / num_columns
numberSegments = 30
deformationType = "left" # front | left | right | bottom | top
deformationAxis = "vertical" # frontal deformation: vertical | horizontal
direction = "inside"
insideDegree = roundingDegree/2

# Changing select mode:
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_mode(type = 'FACE')
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Retrieving model mass region to apply the deformation:
region = bpy.data.objects[labels[0]].data.polygons[regionIndex]

# Applying deformation:
roundShape(region, deformationType, direction, roundingDegree, numberSegments, sideReference, deformationAxis, insideDegree)

# -------------------------------------------------------------------------------

# TESTING 2 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_left", "main_grid_left"]
rowsIndex = [1]
columnsIndex = [2]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "reception_2_1"
parent = gridCopyNode.getParent()
extrusionSize = 1
sidesLabels = [label + "_front", label + "_left", label + "_right"]
sideReference = "main_back"

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model and retrieving face index to apply deformation:
regionIndex = addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)

       
# TESTING -> Simulating data for labels, degree, segments, type and axis:
labels = ["building", "building_left", "reception_2_1", "reception_2_1_front"]
roundingDegree = 0.2
numberSegments = 30
deformationType = "bottom" # front | left | right | bottom | top
deformationAxis = "horizontal" # frontal deformation: vertical | horizontal
direction = "inside"
insideDegree = 0.1

# Changing select mode:
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_mode(type = 'FACE')
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Retrieving model mass region to apply the deformation:
region = bpy.data.objects[labels[0]].data.polygons[regionIndex]

# Applying deformation:
roundShape(region, deformationType, direction, roundingDegree, numberSegments, sideReference, deformationAxis, roundingDegree)

# -------------------------------------------------------------------------------

# TESTING 2.1 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_left", "main_grid_left"]
rowsIndex = [2]
columnsIndex = [2]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "reception_2_2"
parent = gridCopyNode.getParent()
extrusionSize = 1
sidesLabels = [label + "_front", label + "_left", label + "_right"]
sideReference = "main_left"

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model and retrieving face index to apply deformation:
regionIndex = addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)

       
# TESTING -> Simulating data for labels, degree, segments, type and axis:
labels = ["building", "building_left", "reception_2_2", "reception_2_2_front"]
roundingDegree = 0.3
numberSegments = 30
deformationType = "front" # front | left | right | bottom | top
deformationAxis = "horizontal" # frontal deformation: vertical | horizontal
direction = "inside"
insideDegree = 0.1

# Changing select mode:
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_mode(type = 'FACE')
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Retrieving model mass region to apply the deformation:
region = bpy.data.objects[labels[0]].data.polygons[regionIndex]

# Applying deformation:
roundShape(region, deformationType, direction, roundingDegree, numberSegments, sideReference, deformationAxis, insideDegree)

# -------------------------------------------------------------------------------

# TESTING 2.2 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_left", "main_grid_left"]
rowsIndex = [3]
columnsIndex = [2]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "reception_2_3"
parent = gridCopyNode.getParent()
extrusionSize = 1
sidesLabels = [label + "_front", label + "_left", label + "_right"]
sideReference = "main_left"

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model and retrieving face index to apply deformation:
regionIndex = addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)

       
# TESTING -> Simulating data for labels, degree, segments, type and axis:
labels = ["building", "building_left", "reception_2_3", "reception_2_3_front"]
roundingDegree = 0.2
numberSegments = 30
deformationType = "top" # front | left | right | bottom | top
deformationAxis = "horizontal" # frontal deformation: vertical | horizontal
direction = "inside"
insideDegree = 0.1

# Changing select mode:
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_mode(type = 'FACE')
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Retrieving model mass region to apply the deformation:
region = bpy.data.objects[labels[0]].data.polygons[regionIndex]

# Applying deformation:
roundShape(region, deformationType, direction, roundingDegree, numberSegments, sideReference, deformationAxis, insideDegree)

# -------------------------------------------------------------------------------

# TESTING 3 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_left", "main_grid_left"]
rowsIndex = [1, 2, 3]
columnsIndex = [3]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "reception_3"
parent = gridCopyNode.getParent()
extrusionSize = 2
sidesLabels = [label + "_front", label + "_left", label + "_right"]
sideReference = "main_left"

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model and retrieving face index to apply deformation:
regionIndex = addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)

       
# TESTING -> Simulating data for labels, degree, segments, type and axis:
labels = ["building", "building_left", "reception_3", "reception_3_front"]
roundingDegree = 0.16 # (width / num_columns) / num_columns
numberSegments = 30
deformationType = "left" # front | left | right | bottom | top
deformationAxis = "vertical" # frontal deformation: vertical | horizontal
direction = "outside"

# Changing select mode:
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_mode(type = 'FACE')
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Retrieving model mass region to apply the deformation:
region = bpy.data.objects[labels[0]].data.polygons[regionIndex]

# Applying deformation:
roundShape(region, deformationType, direction, roundingDegree, numberSegments, sideReference, deformationAxis)


# TESTING 4 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_left", "main_grid_left"]
rowsIndex = [3]
columnsIndex = [4, 5, 6]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "reception_4"
parent = gridCopyNode.getParent()
extrusionSize = 5
sidesLabels = [label + "_front", label + "_left", label + "_right"]
sideReference = "main_left"

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model and retrieving face index to apply deformation:
regionIndex = addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)


# TESTING -> Simulating data for labels, degree, segments, type and axis:
labels = ["building", "building_left", "reception_4", "reception_4_"]
roundingDegree = 0.4
numberSegments = 30
deformationType = "front" # front | left | right | bottom | top
deformationAxis = "vertical" # frontal deformation: vertical | horizontal
direction = "inside"
insideDegree = 0.1

# Changing select mode:
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_mode(type = 'FACE')
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Retrieving model mass region to apply the deformation:
region = bpy.data.objects[labels[0]].data.polygons[regionIndex]

# Applying deformation:
roundShape(region, deformationType, direction, roundingDegree, numberSegments, sideReference, deformationAxis, insideDegree)

# -------------------------------------------------------------------------------

# TESTING 5 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_left", "main_grid_left"]
rowsIndex = [1, 2]
columnsIndex = [4, 5, 6]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "reception_top"
parent = gridCopyNode.getParent()
extrusionSize = 2
sidesLabels = [label + "_front", label + "_left", label + "_right"]
sideReference = "main_left"

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model and retrieving face index to apply deformation:
regionIndex = addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)

       
# TESTING -> Simulating data for labels, degree, segments, type and axis:
labels = ["building", "building_left", "reception_top", "reception_top_front"]
roundingDegree = 0.48
numberSegments = 30
deformationType = "right" # front | left | right | bottom | top
deformationAxis = "vertical" # frontal deformation: vertical | horizontal
direction = "inside"
insideDegree = 0.1

# Changing select mode:
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_mode(type = 'FACE')
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Retrieving model mass region to apply the deformation:
region = bpy.data.objects[labels[0]].data.polygons[regionIndex]

# Applying deformation:
roundShape(region, deformationType, direction, roundingDegree, numberSegments, sideReference, deformationAxis, insideDegree)


# -------------------------------------------------------------------------------
# ROUND RIGHT
# -------------------------------------------------------------------------------

# TESTING 1 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_right", "main_grid_right"]
rowsIndex = [1, 2, 3]
columnsIndex = [1]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "garden_1"
parent = gridCopyNode.getParent()
extrusionSize = 3
sidesLabels = [label + "_front", label + "_left", label + "_right"]
sideReference = "main_right"

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model and retrieving face index to apply deformation:
regionIndex = addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)

       
# TESTING -> Simulating data for labels, degree, segments, type and axis:
labels = ["building", "building_right", "garden_1", "garden_1_front"]
roundingDegree = 0.16 # (width / num_columns) / num_columns
numberSegments = 30
deformationType = "left" # front | left | right | bottom | top
deformationAxis = "vertical" # frontal deformation: vertical | horizontal
direction = "inside"
insideDegree = roundingDegree/2

# Changing select mode:
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_mode(type = 'FACE')
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Retrieving model mass region to apply the deformation:
region = bpy.data.objects[labels[0]].data.polygons[regionIndex]

# Applying deformation:
roundShape(region, deformationType, direction, roundingDegree, numberSegments, sideReference, deformationAxis, insideDegree)

# -------------------------------------------------------------------------------

# TESTING 2 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_right", "main_grid_right"]
rowsIndex = [1]
columnsIndex = [2]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "garden_2_1"
parent = gridCopyNode.getParent()
extrusionSize = 1
sidesLabels = [label + "_front", label + "_left", label + "_right"]
sideReference = "main_right"

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model and retrieving face index to apply deformation:
regionIndex = addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)

       
# TESTING -> Simulating data for labels, degree, segments, type and axis:
labels = ["building", "building_right", "garden_2_1", "garden_2_1_front"]
roundingDegree = 0.2
numberSegments = 30
deformationType = "bottom" # front | left | right | bottom | top
deformationAxis = "horizontal" # frontal deformation: vertical | horizontal
direction = "inside"
insideDegree = 0.1

# Changing select mode:
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_mode(type = 'FACE')
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Retrieving model mass region to apply the deformation:
region = bpy.data.objects[labels[0]].data.polygons[regionIndex]

# Applying deformation:
roundShape(region, deformationType, direction, roundingDegree, numberSegments, sideReference, deformationAxis, roundingDegree)

# -------------------------------------------------------------------------------

# TESTING 2.1 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_right", "main_grid_right"]
rowsIndex = [2]
columnsIndex = [2]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "garden_2_2"
parent = gridCopyNode.getParent()
extrusionSize = 1
sidesLabels = [label + "_front", label + "_left", label + "_right"]
sideReference = "main_right"

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model and retrieving face index to apply deformation:
regionIndex = addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)

       
# TESTING -> Simulating data for labels, degree, segments, type and axis:
labels = ["building", "building_right", "garden_2_2", "garden_2_2_front"]
roundingDegree = 0.3
numberSegments = 30
deformationType = "front" # front | left | right | bottom | top
deformationAxis = "horizontal" # frontal deformation: vertical | horizontal
direction = "inside"
insideDegree = 0.1

# Changing select mode:
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_mode(type = 'FACE')
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Retrieving model mass region to apply the deformation:
region = bpy.data.objects[labels[0]].data.polygons[regionIndex]

# Applying deformation:
roundShape(region, deformationType, direction, roundingDegree, numberSegments, sideReference, deformationAxis, insideDegree)

# -------------------------------------------------------------------------------

# TESTING 2.2 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_right", "main_grid_right"]
rowsIndex = [3]
columnsIndex = [2]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "garden_2_3"
parent = gridCopyNode.getParent()
extrusionSize = 1
sidesLabels = [label + "_front", label + "_left", label + "_right"]
sideReference = "main_right"

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model and retrieving face index to apply deformation:
regionIndex = addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)

       
# TESTING -> Simulating data for labels, degree, segments, type and axis:
labels = ["building", "building_right", "garden_2_3", "garden_2_3_front"]
roundingDegree = 0.2
numberSegments = 30
deformationType = "top" # front | left | right | bottom | top
deformationAxis = "horizontal" # frontal deformation: vertical | horizontal
direction = "inside"
insideDegree = 0.1

# Changing select mode:
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_mode(type = 'FACE')
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Retrieving model mass region to apply the deformation:
region = bpy.data.objects[labels[0]].data.polygons[regionIndex]

# Applying deformation:
roundShape(region, deformationType, direction, roundingDegree, numberSegments, sideReference, deformationAxis, insideDegree)

# -------------------------------------------------------------------------------

# TESTING 3 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_right", "main_grid_right"]
rowsIndex = [1, 2, 3]
columnsIndex = [3]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "garden_3"
parent = gridCopyNode.getParent()
extrusionSize = 2
sidesLabels = [label + "_front", label + "_left", label + "_right"]
sideReference = "main_right"

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model and retrieving face index to apply deformation:
regionIndex = addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)

       
# TESTING -> Simulating data for labels, degree, segments, type and axis:
labels = ["building", "building_right", "garden_3", "garden_3_front"]
roundingDegree = 0.16 # (width / num_columns) / num_columns
numberSegments = 30
deformationType = "left" # front | left | right | bottom | top
deformationAxis = "vertical" # frontal deformation: vertical | horizontal
direction = "outside"

# Changing select mode:
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_mode(type = 'FACE')
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Retrieving model mass region to apply the deformation:
region = bpy.data.objects[labels[0]].data.polygons[regionIndex]

# Applying deformation:
roundShape(region, deformationType, direction, roundingDegree, numberSegments, sideReference, deformationAxis)


# TESTING 4 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_right", "main_grid_right"]
rowsIndex = [3]
columnsIndex = [4, 5, 6]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "garden_4"
parent = gridCopyNode.getParent()
extrusionSize = 5
sidesLabels = [label + "_front", label + "_left", label + "_right"]
sideReference = "main_right"

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model and retrieving face index to apply deformation:
regionIndex = addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)


# TESTING -> Simulating data for labels, degree, segments, type and axis:
labels = ["building", "building_right", "garden_4", "garden_4_"]
roundingDegree = 0.4
numberSegments = 30
deformationType = "front" # front | left | right | bottom | top
deformationAxis = "vertical" # frontal deformation: vertical | horizontal
direction = "inside"
insideDegree = 0.1

# Changing select mode:
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_mode(type = 'FACE')
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Retrieving model mass region to apply the deformation:
region = bpy.data.objects[labels[0]].data.polygons[regionIndex]

# Applying deformation:
roundShape(region, deformationType, direction, roundingDegree, numberSegments, sideReference, deformationAxis, insideDegree)

# -------------------------------------------------------------------------------

# TESTING 5 -> Simulating data for labels and rows/columns indexes:
labels = ["building", "building_right", "main_grid_right"]
rowsIndex = [1, 2]
columnsIndex = [4, 5, 6]

## Passing labels to function responsible for selecting the object from shape tree:
grid = selectNode(root, labels)

gridCopy = duplicateShape(grid.getLabel())

gridCopyNode = Node(gridCopy.name, gridCopy, grid.getParent(), "virtual", grid.getDimX(), grid.getDimY(), grid.getDimZ(), grid.getRows()+1, grid.getColumns()+1)

# DEBUG - Printing grid label and number of rows and columns
## print("GRID - ROWS x COLUMNS: ", grid.getLabel(), grid.getRows(), grid.getColumns())

## Selecting cells from the grid:
selectToBeVolume(gridCopyNode, gridCopyNode.getRows(), gridCopyNode.getColumns(), rowsIndex, columnsIndex)

# TESTING -> Simulating data for label, parent, extrusion size and volume side's labels:
label = "garden_top"
parent = gridCopyNode.getParent()
extrusionSize = 2
sidesLabels = [label + "_front", label + "_left", label + "_right"]
sideReference = "main_right"

# Extra parameter for selecting objects properly:
gridLabel = gridCopyNode.getLabel()

## Adding volume to the mass model and retrieving face index to apply deformation:
regionIndex = addVolume(label, parent, extrusionSize, sidesLabels, gridLabel)

       
# TESTING -> Simulating data for labels, degree, segments, type and axis:
labels = ["building", "building_right", "garden_top", "garden_top_front"]
roundingDegree = 0.48
numberSegments = 30
deformationType = "right" # front | left | right | bottom | top
deformationAxis = "vertical" # frontal deformation: vertical | horizontal
direction = "inside"
insideDegree = 0.1

# Changing select mode:
bpy.ops.object.mode_set(mode = 'EDIT')
bpy.ops.mesh.select_mode(type = 'FACE')
bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Retrieving model mass region to apply the deformation:
region = bpy.data.objects[labels[0]].data.polygons[regionIndex]

# Applying deformation:
roundShape(region, deformationType, direction, roundingDegree, numberSegments, sideReference, deformationAxis, insideDegree)

''' </ END FOR LOOP > '''