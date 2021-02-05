import bpy
import bmesh

# Assuming there is a transformed plane (configurations below) properly positioned on the face of the (default) cube:

# Rotate X = 90
# Rotate Z = 90
# Scale X = 0.5
# Scale Y = 0.5
# Location Y = -0.5
# Location Z = -0.5

# Selectiong objects to be joined:
bpy.data.objects["Cube"].select_set(True)
bpy.data.objects["Plane"].select_set(True)

# Joining objects:
bpy.ops.object.join()

bpy.ops.object.mode_set(mode = 'OBJECT')
obj = bpy.context.active_object

bpy.ops.object.mode_set(mode = 'EDIT') 
bpy.ops.mesh.select_mode(type="FACE")

bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Selecting face to be extruded:
bpy.data.objects['Cube'].data.polygons[6].select = True

bpy.ops.object.mode_set(mode = 'EDIT')

# Extruding region (copied from 'Info'):
bpy.ops.mesh.extrude_region_move(MESH_OT_extrude_region={"use_normal_flip":False, "mirror":False}, 
	                               TRANSFORM_OT_translate={"value":(0, 0, 0.862433), 
	                                                       "orient_type":'NORMAL', 
	                                                       "orient_matrix":((-2.98023e-08, -8.88178e-16, -1), 
	                                                       	                (-2.98023e-08, 1, 0), 
	                                                       	                (1, 2.98023e-08, -2.98023e-08)), 
	                                                       "orient_matrix_type":'NORMAL', 
	                                                       "constraint_axis":(False, False, True), 
	                                                       "mirror":False, "use_proportional_edit":False, 
	                                                       "proportional_edit_falloff":'SMOOTH', 
	                                                       "proportional_size":1, 
	                                                       "use_proportional_connected":False, 
	                                                       "use_proportional_projected":False, 
	                                                       "snap":False, 
	                                                       "snap_target":'CLOSEST', 
	                                                       "snap_point":(0, 0, 0), 
	                                                       "snap_align":False, 
	                                                       "snap_normal":(0, 0, 0), 
	                                                       "gpencil_strokes":False, 
	                                                       "cursor_transform":False, 
	                                                       "texture_space":False, 
	                                                       "remove_on_cancel":False, 
	                                                       "release_confirm":False, 
	                                                       "use_accurate":False})

bpy.ops.object.mode_set(mode = 'OBJECT')
obj = bpy.context.active_object

bpy.ops.object.mode_set(mode = 'EDIT') 
bpy.ops.mesh.select_mode(type="EDGE")

bpy.ops.mesh.select_all(action = 'DESELECT')
bpy.ops.object.mode_set(mode = 'OBJECT')

# Selecting lateral (left and right) egdes to round object:
obj.data.edges[16].select = True
obj.data.edges[18].select = True

bpy.ops.object.mode_set(mode = 'EDIT')

# Applying bevel transformation (copied from 'Info') on selected edges:
bpy.ops.mesh.bevel(offset=0.440091, offset_pct=0, segments=10, vertex_only=False)