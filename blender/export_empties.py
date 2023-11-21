import bpy
import json

data = {}

for collection in bpy.context.scene.collection.children:
    data[collection.name] = {}
    for sub_collection in collection.children:
        data[collection.name][sub_collection.name] = []
        for obj in sub_collection.objects:
            # Dividing x and y coordinates by 10
            coords = obj.location
            data[collection.name][sub_collection.name].append({
                "coordinates": {"x": coords.x / 10, "y": coords.y / 10, "z": coords.z}
            })

print(data)

# Specifying the file path
file_path = '/Users/frank/Development/led_board/data/installation.json'

# Writing the data object as JSON to the specified file
with open(file_path, 'w') as json_file:
    json.dump(data, json_file, indent=4)
