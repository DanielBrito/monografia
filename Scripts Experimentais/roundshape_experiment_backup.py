import bpy
import bmesh

''' FUNCTION: '''
def roundShape(object, side, degree, segments, axis=""):
    center = object.center
    
    # DEBUG: Printing center coordinate of the face:
    # print("center coordinate = ", center)
    
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
            # print(v.co, center)
                        
            # Checking for upper left vertex:
            if v.co[x] < center[x] and v.co[z] > center[z] and v.co[y] == center[y]:
                print("selecting upper left vertex = ", v.index)
                vertexA = bpy.context.active_object.data.vertices[v.index]
                
            # Checking for bottom left vertex:
            if v.co[x] < center[x] and v.co[z] < center[z] and v.co[y] == center[y]:
                print("selecting bottom left vertex = ", v.index)
                vertexB = bpy.context.active_object.data.vertices[v.index]
                
        bpy.ops.object.mode_set(mode = 'EDIT')
        
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
            if v.co[x] > center[x] and v.co[z] > center[z] and v.co[y] == center[y]:
                print("selecting upper right vertex = ", v.index)
                vertexA = bpy.context.active_object.data.vertices[v.index]
                
            # Checking for bottom right vertex:
            if v.co[x] > center[x] and v.co[z] < center[z] and v.co[y] == center[y]:
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
            if v.co[x] < center[x] and v.co[z] > center[z] and v.co[y] == center[y]:
                print("selecting upper left vertex = ", v.index)
                vertexA = bpy.context.active_object.data.vertices[v.index]
                
            # Checking for upper right vertex:
            if v.co[x] > center[x] and v.co[z] > center[z] and v.co[y] == center[y]:
                print("selecting upper right vertex = ", v.index)
                vertexB = bpy.context.active_object.data.vertices[v.index]
                
        bpy.ops.object.mode_set(mode = 'EDIT')
        
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
            if v.co[x] < center[x] and v.co[z] < center[z] and v.co[y] == center[y]:
                print("selecting bottom left vertex = ", v.index)
                vertexA = bpy.context.active_object.data.vertices[v.index]
                
            # Checking for bottom right vertex:
            if v.co[x] > center[x] and v.co[z] < center[z] and v.co[y] == center[y]:
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
 
   
''' RESETING THE SCENE: '''
    
if len(bpy.context.scene.objects) > 0:
    bpy.ops.object.mode_set(mode = "OBJECT")
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    
bpy.ops.mesh.primitive_cube_add()
    

''' MAIN: '''

# Switching from Edit mode to Object mode so the selection gets updated:
bpy.ops.object.mode_set(mode = 'OBJECT')
bpy.ops.object.mode_set(mode = 'EDIT') 

bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Storing selected face of the object:
selectedFace = bpy.context.active_object.data.polygons[3]

# Calling deformation function:

#roundShape(selectedFace, "left", 1.0, 30)
#roundShape(selectedFace, "right", 1.0, 30)
#roundShape(selectedFace, "top", 1.0, 30)
#roundShape(selectedFace, "bottom", 1.0, 30)
roundShape(selectedFace, "front", 1.0, 30, "vertical")
#roundShape(selectedFace, "front", 1.0, 30, "horizontal")

print("-----------------------------------------------------------------------")