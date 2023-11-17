import json

# File path
file_path = 'house_layout.json'

# Load JSON data into a dictionary
with open(file_path, 'r') as file:
    house_layout = json.load(file)

#print(house_layout)

# File path
file_path = 'lights_by_group.json'

# Load JSON data into a dictionary
with open(file_path, 'r') as file:
    lights_by_group = json.load(file)

#print(lights_by_group)

lights = {}

for collection in lights_by_group['collections']:
    ip = collection['name']
    lights[ip] = {}
    for group in collection["children"]:
        group_name = group['name']
        lights[ip][group_name] = []
        for light in group['objects']:
            if light.strip():
                parts = light.split()
                number_part = parts[1]
                index = int(number_part.split('.')[0])
                #print(ip, group_name, index)
                #print(house_layout[ip][index - 1])
                lights[ip][group_name].append({
                    'index': index,
                    'coordinate': house_layout[ip][index - 1]
                })

#print(lights)

pretty_json = json.dumps(lights, indent=4)
print(pretty_json)