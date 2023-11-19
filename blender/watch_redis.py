import json
import bpy
import redis
import time

redis_client = redis.StrictRedis(host='10.10.10.1', port=6379, db=0)

light_data_file = "/Users/frank/Development/led_board/data/lights.json"
# Reading the JSON file
with open(light_data_file, "r") as file:
    lights = json.load(file)

def get_material(object_name):
    # Get the object by its name
    obj = bpy.data.objects.get(object_name)

    if obj and obj.data.materials:
        # Return the first material of the object
        return obj.data.materials[0]
    else:
        return None

def set_material_color(material, rgb_values):
    if material and material.use_nodes:
        # Assuming a principled BSDF shader with an Emission node
        for node in material.node_tree.nodes:
            if node.type == 'EMISSION':
                # Blender expects color values in the range [0, 1]
                color = [rgb_values['r']/255.0, rgb_values['g']/255.0, rgb_values['b']/255.0, 1]
                node.inputs['Color'].default_value = color
                break

def watch_redis(data):
    redis_client = redis.Redis(host='10.10.10.1', port=6379, db=0)  # Adjust to your Redis setup

    for ip in data:
        for group in data[ip]:
            for light in data[ip][group]:
                object_name = f"{ip}-{group}-{light['index']}"
                redis_key = f"{ip}:{light['index']}"
                rgb_value = redis_client.get(redis_key)

                if rgb_value:
                    rgb_value = rgb_value.decode('utf-8')
                    rgb_dict = json.loads(rgb_value)  # Parse the RGB JSON string

                    #print(f"Current RGB value for {redis_key}: {rgb_dict}")
                    material = get_material(object_name)

                    if material:
                        set_material_color(material, rgb_dict)

while False:
    watch_redis(lights)
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
    time.sleep(5)  # Adjust the sleep time as needed

watch_redis(lights)
print("done")