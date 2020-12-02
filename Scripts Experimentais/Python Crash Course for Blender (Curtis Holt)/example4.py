import bpy
from math import radians

# create cube
bpy.ops.mesh.primitive_cube_add()
so  = bpy.context.active_object

# rotate object 45 degrees on the x axis:
so.rotation_euler[0] += radians(45)

# create modifier
modifier_subsurf = so.modifiers.new("My Modifier", 'SUBSURF')

# apply modifier to round the cube:
modifier_subsurf.levels = 3

# smooth the object:
bpy.ops.object.shade_smooth()

# create displacement modifier:
# https://docs.blender.org/api/current/bpy.types.Modifier.html
modifier_displace = so.modifiers.new("My Displacement", 'DISPLACE')

# create the texture:
# https://docs.blender.org/api/current/bpy.types.Texture.html
new_texture = bpy.data.textures.new("My Texture", 'DISTORTED_NOISE')

# change the texture settings:
new_texture.noise_scale = 0.5

# assign the texture to displacement modifier:
modifier_displace.texture = new_texture

# create the material:
new_material = bpy.data.materials.new(name = "My Material")

so.data.materials.append(new_material)

new_material.use_nodes = True
nodes = new_material.node_tree.nodes

material_output = nodes.get("Material Output")
node_emission = nodes.new(type="ShaderNodeEmission")

node_emission.inputs[0].default_value = (0.0, 0.3, 1.0, 1) # cyan color
node_emission.inputs[1].default_value = 500.0 # stength

links = new_material.node_tree.links
new_link = links.new(node_emission.outputs[0], material_output.inputs[0])

# ...change to 'rendered' mode and set world background to black...

# applying bright effect:
bpy.context.scene.eevee.use_gtao = True
bpy.context.scene.eevee.use_bloom = True
bpy.context.scene.eevee.bloom_clamp = 1