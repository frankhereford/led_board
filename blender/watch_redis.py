import json
import bpy

light_data_file = "/Users/frank/Development/led_board/data/lights.json"
# Reading the JSON file
with open(light_data_file, "r") as file:
    lights = json.load(file)


def watch_redis(data):
    # Iterate over the JSON data and create objects in Blender
    for ip in data:
        print(ip)
        for group in data[ip]:
            print(group)
            for light in data[ip][group]:
                print(light)
