import xled
import csv

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

control = xled.ControlInterface('10.10.10.151')
#print(control)
response = control.get_led_layout()
#print(response.data)

# Extracting x, y, z coordinates
x = [point['x'] for point in response.data['coordinates']]
y = [point['y'] for point in response.data['coordinates']]
z = [point['z'] for point in response.data['coordinates']]

# Creating the 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(x, y, z)

# Labels and title
ax.set_xlabel('X Axis')
ax.set_ylabel('Y Axis')
ax.set_zlabel('Z Axis')
ax.set_title('3D Scatter Plot of Coordinates')


plt.savefig('3d_scatter.png')

with open('led_coordinates.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['x', 'y', 'z'])
    for point in response.data['coordinates']:
        writer.writerow([point['x'], point['y'], point['z']])