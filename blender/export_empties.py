import bpy
import json

data = {}

for collection in bpy.context.scene.collection.children:
    data[collection.name] = {}
    for sub_collection in collection.children:
        data[collection.name][sub_collection.name] = []
        for obj in sub_collection.objects:
            # Split the object name over the colon
            print(obj.name)
            split_name = obj.name.split('-')

            # Convert the value after the colon to an integer and store it in a variable
            if len(split_name) > 1:
                number = int(split_name[1])
            else:
                number = None  # or some default value if no colon is found

            # Dividing x and y coordinates by 10
            coords = obj.location
            data[collection.name][sub_collection.name].append({
                "index": number,  # add the integer value to the data structure
                "coordinate": {"x": coords.x / 10, "y": coords.y / 10, "z": coords.z}
            })

#print(data)

# Specifying the file path
file_path = '/Users/frank/Development/led_board/data/installation.json'

# Writing the data object as JSON to the specified file
with open(file_path, 'w') as json_file:
    json.dump(data, json_file, indent=4)
