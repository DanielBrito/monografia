import bpy

def create_custom_mesh(objname, px, py, pz):
 
    # Define arrays for holding data    
    myvertex = []
    myfaces = []

    # Create all Vertices:
    mypoint = [(-1.0, -1.0, 0.0)] # vertex 0
    myvertex.extend(mypoint)

    mypoint = [(1.0, -1.0, 0.0)] # vertex 1
    myvertex.extend(mypoint)

    mypoint = [(-1.0, 1.0, 0.0)] # vertex 2
    myvertex.extend(mypoint)

    mypoint = [(1.0, 1.0, 0.0)] # vertex 3
    myvertex.extend(mypoint)

    # Create all Faces:
    myface = [(0, 1, 3, 2)]
    myfaces.extend(myface)
    
    mymesh = bpy.data.meshes.new(objname)

    myobject = bpy.data.objects.new(objname, mymesh)

    bpy.context.scene.collection.objects.link(myobject)
    
    # Generate mesh data:
    mymesh.from_pydata(myvertex, [], myfaces)

    # Calculate the edges:
    mymesh.update(calc_edges=True)

    # Set Location:
    myobject.location.x = px
    myobject.location.y = py
    myobject.location.z = pz

    return myobject

cursor_location = bpy.context.scene.cursor.location

create_custom_mesh("Plane", cursor_location[0], cursor_location[1], 0)
