import redis
import matplotlib.pyplot as plt
import json
import time
import pygame

r = redis.Redis(host="10.10.10.1", port=6379, db=0)


def parse_data(data):
    points = []
    data_dict = json.loads(data)  # Assuming data is a JSON string

    # print(data_dict)
    if not data_dict:
        return points

    for _, nested_data in data_dict.items():
        for _, points_list in nested_data.items():
            for point in points_list:
                x = ((point["coordinate"]["x"] + 1) * 400) + 10
                y = 600 - ((point["coordinate"]["y"] * 600) + 10)
                color = (0, 0, 0)
                if "color" in point:
                    color = (
                        point["color"]["r"],
                        point["color"]["g"],
                        point["color"]["b"],
                    )
                points.append((x, y, color))
    return points


# Initialize Pygame
pygame.init()

# Screen dimensions and setup
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Real-Time Data Visualization")

# Main loop flag
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Retrieve and parse data
    data = r.get("installation_layout")
    if data:
        points = parse_data(data)

        # Clear screen
        screen.fill((0, 0, 0))

        # Draw points
        for x, y, color in points:
            pygame.draw.circle(
                screen, color, (int(x), int(y)), 4
            )  # 5 is the radius of the circle

    # Update the screen
    pygame.display.flip()

    # Control the update rate
    time.sleep(0.01)  # Adjust this value as needed

# Quit Pygame
pygame.quit()
