import json
import bpy

light_data_file = "/Users/frank/Development/led_board/data/lights.json"
# Reading the JSON file
with open(light_data_file, 'r') as file:
    lights = json.load(file)

def empty_scene():
    # Delete all objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Delete all materials
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)

    # Delete all collections except the master collection
    for collection in bpy.data.collections:
        bpy.data.collections.remove(collection)

    # Delete all cameras
    for camera in bpy.data.cameras:
        bpy.data.cameras.remove(camera)

    # Delete all lights
    for light in bpy.data.lights:
        bpy.data.lights.remove(light)

    print("Cleared the Blender scene.")

def create_icosphere(name, coordinates, size, subdivisions, collection):
    # Multiply x and y coordinates by 10
    scaled_location = (coordinates['x'] * 10, coordinates['y'] * 10, coordinates['z'])
    
    bpy.ops.mesh.primitive_ico_sphere_add(radius=size, subdivisions=subdivisions, location=scaled_location)
    obj = bpy.context.active_object
    obj.name = name

    collection.objects.link(obj)  # Link the icosphere to the specified collection
    bpy.context.collection.objects.unlink(obj)
    return obj

def assign_emission_material(obj, color=(1, 1, 1), strength=5.0):
    # Create a new material
    mat = bpy.data.materials.new(name="EmissionMaterial")

    # Enable 'Use nodes':
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    # Clear all nodes to start clean
    nodes.clear()

    # Create an Emission node
    emission_node = nodes.new(type='ShaderNodeEmission')
    emission_node.location = (0, 0)
    emission_node.inputs['Color'].default_value = (*color, 1)
    emission_node.inputs['Strength'].default_value = strength

    # Create an Output node
    output_node = nodes.new('ShaderNodeOutputMaterial')
    output_node.location = (200, 0)

    # Link Emission to Output
    links = mat.node_tree.links
    links.new(emission_node.outputs['Emission'], output_node.inputs['Surface'])

    # Assign it to the object
    if obj.data.materials:
        # Replace material
        obj.data.materials[0] = mat
    else:
        # Add material
        obj.data.materials.append(mat)


def load_data(data, max_lights_per_group=5000):
    # Iterate over the JSON data and create objects in Blender
    for ip in data:
        if ip not in bpy.data.collections:
            ip_collection = bpy.data.collections.new(ip)
            bpy.context.scene.collection.children.link(ip_collection)
        for group in data[ip]:
            print(group)
            group_collection = bpy.data.collections.new(group)
            ip_collection.children.link(group_collection)
            lights_added = 0
            for light in data[ip][group]:
                if lights_added >= max_lights_per_group:
                    break
                sphere = create_icosphere(f"{ip}-{group}-{light['index']}", light['coordinate'], 0.05, 1, group_collection)
                assign_emission_material(sphere, color=(0, 1, 0), strength=10)
                lights_added += 1


empty_scene()
load_data(lights)