import xled
import json
ips = ['10.10.10.152', '10.10.10.78', '10.10.10.151']  # List of IPs

house = {}

for ip in ips:
    control = xled.ControlInterface(ip)
    layout = control.get_led_layout()

    house[ip] = layout.data['coordinates']

print(house)

with open('house_layout.json', 'w') as file:
    json.dump(house, file, indent=2)

