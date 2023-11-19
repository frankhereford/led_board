import xled

import json


lights = {}
light_data = {}

for ip in ['10.10.10.154', '10.10.10.155']:
    control = xled.ControlInterface(ip)
    #print(control)
    response = control.get_led_layout()
    #print(response.data)

    lights[ip] = response.data['coordinates']

    if ip == '10.10.10.154':
        group_name = 'Left Window'
    elif ip == '10.10.10.155':
        group_name = 'Right Window'

    light_data[ip] = {
        group_name : []
    }
    index = 0
    for index, light in enumerate(response.data['coordinates']):
        light_data[ip][group_name].append({
            'index': index,
            'coordinate': light,
        })

#print(json.dumps(light_data, indent=4))

with open('test_windows_data.json', 'w') as file:
    json.dump(light_data, file, indent=4)
