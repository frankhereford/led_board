import bpy
import json

# remove all collections
for collection in list(bpy.data.collections):
    bpy.data.collections.remove(collection)


# Clear all objects in the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Load the JSON data
file_path = '/Users/frank/Desktop/house_layout.json'
with open(file_path, 'r') as file:
    data = json.load(file)

# Function to create a UV sphere
def create_uv_sphere(location, name):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=location)
    sphere = bpy.context.object
    sphere.name = name
    return sphere

# Function to create an omnidirectional light
def create_omni_light(location, name):
    bpy.ops.object.light_add(type='POINT', location=location)
    light = bpy.context.object
    light.name = name
    return light


# Process each IP address
for ip, points in data.items():
    # Create a new collection for each IP
    collection = bpy.data.collections.new(name=ip)
    bpy.context.scene.collection.children.link(collection)

    for i, point in enumerate(points, start=1):
        #if i > 100:
            #continue  # Skip the rest of the points after the 10th one

        # Scale coordinates
        location = (point['x'] * 10, point['y'] * 10, point['z'])
        # Create a UV sphere
        sphere = create_omni_light(location, f'light {i:03d}')
        # Link the sphere to the collection
        collection.objects.link(sphere)
        # Unlink from the main collection if needed
        bpy.context.scene.collection.objects.unlink(sphere)