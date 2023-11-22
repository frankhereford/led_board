import redis
import matplotlib.pyplot as plt
import json
import time

r = redis.Redis(host='10.10.10.1', port=6379, db=0)

def parse_data(data):
    points = []
    data_dict = json.loads(data)  # Assuming data is a JSON string

    for _, nested_data in data_dict.items():
        for _, points_list in nested_data.items():
            for point in points_list:
                x = point['coordinate']['x']
                y = point['coordinate']['y']
                color = (0, 0, 0)
                if 'color' in point:
                    color = (
                        point['color']['r'] / 255,
                        point['color']['g'] / 255,
                        point['color']['b'] / 255,
                    )
                points.append((x, y, color))
    return points


# Set up the interactive mode for real-time updates
plt.ion()
figure, ax = plt.subplots()

iteration = 0

while True:
    print(f"Render Loop {iteration}")
    iteration = iteration + 1

    # Retrieve data from Redis
    data = r.get('installation_layout')

    # Check if data is not None
    if data:
        # Extract coordinates and colors
        points = parse_data(data)

        # Clear the plot
        ax.clear()

        # Plot the new data
        for x, y, color in points:
            ax.scatter(x, y, c=[color], marker='o')  # 'o' for circle markers

        # Update the plot
        plt.draw()
        plt.pause(0.1)  # Pause briefly to allow the plot to update

    # Control the update rate (e.g., update every 5 seconds)
    #time.sleep(1)