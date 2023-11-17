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
        #if collection.name != "Collection":
        bpy.data.collections.remove(collection)

    # Delete all cameras
    for camera in bpy.data.cameras:
        bpy.data.cameras.remove(camera)

    # Delete all lights
    for light in bpy.data.lights:
        bpy.data.lights.remove(light)

    print("Cleared the Blender scene.")

def create_icosphere(name, coordinates, size, subdivisions):
    bpy.ops.mesh.primitive_ico_sphere_add(radius=size, subdivisions=subdivisions, location=(coordinates['x'], coordinates['y'], coordinates['z']))
    obj = bpy.context.active_object
    obj.name = name



def load_data(data):
    # Iterate over the JSON data and create objects in Blender
    print(data)

    for ip in data:
        if ip not in bpy.data.collections:
            ip_collection = bpy.data.collections.new(ip)
            bpy.context.scene.collection.children.link(ip_collection)
        for group in data[ip]:
            print(group)
            group_collection = bpy.data.collections.new(group)
            ip_collection.children.link(group_collection)
            for light in data[ip][group]:
                create_icosphere(f"{light['index']}", light['coordinate'], 0.1, 10)
                pass
                #print(light)
                #create_object(f"{ip}_{group}_{light['index']}", light['coordinate'])

    return
    for ip, collections in data.items():
        for collection_name, objects in collections.items():
            # Create a new collection if it doesn't exist
            if collection_name not in bpy.data.collections:
                new_collection = bpy.data.collections.new(collection_name)
                bpy.context.scene.collection.children.link(new_collection)

            # Select the collection
            collection = bpy.data.collections[collection_name]

            # Create objects in the collection
            for obj in objects:
                pass
                #create_object(f"{collection_name}_{obj['index']}", obj['coordinate'])
                # Link the object to the collection
                #collection.objects.link(bpy.context.active_object)

empty_scene()
load_data(lights)