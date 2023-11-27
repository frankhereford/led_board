import sys

sys.path.insert(1, "../radio/lib")
import layout as layout_library
import pygame
import random
import json

# Initialize Pygame
pygame.init()

# Screen dimensions
width, height = 50, 50
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# Star properties
num_stars = 100
star_speed = 2


def transform_coordinate(point, target_x_max=100, target_y_max=100):
    x, y = point

    # Transform X
    # Shift the X value from the range [-1, 1] to [0, 2] and then scale to [0, target_x_max]
    x_transformed = (x + 1) * (target_x_max / 2)

    # Transform Y
    # Scale the Y value from the range [0, 1] to [0, target_y_max]
    y_transformed = y * target_y_max

    return (int(x_transformed), int(y_transformed))


def precompute_light_positions(layout, width, height):
    light_positions = {}
    for ip in layout:
        for group in layout[ip]:
            for index, light in enumerate(layout[ip][group]):
                # Calculate the transformed coordinate
                transformed_point = transform_coordinate(
                    (light["coordinate"]["x"], light["coordinate"]["y"]),
                    width - 1,
                    height - 1,
                )

                # Ensure the coordinate is a key in the dictionary
                if transformed_point not in light_positions:
                    light_positions[transformed_point] = []

                # Append the light identifier to the list for this coordinate
                light_positions[transformed_point].append((ip, group, index))

    return light_positions


class Star:
    def __init__(self):
        self.x = random.randint(-width, width)
        self.y = random.randint(-height, height)
        self.z = random.randint(1, width)

    def update(self):
        self.z -= star_speed
        if self.z <= 0:
            self.x = random.randint(-width, width)
            self.y = random.randint(-height, height)
            self.z = width

    def show(self, screen):
        x, y = self.x / self.z, self.y / self.z
        x = int(x * width / 2 + width / 2)
        y = int(y * height / 2 + height / 2)

        if 0 <= x < width and 0 <= y < height:
            pygame.draw.circle(screen, (255, 255, 255), (x, y), max(1, int(5 / self.z)))


# Create stars
stars = [Star() for _ in range(num_stars)]


layout = layout_library.read_json_from_file("installation_v2_groups.json")
light_positions = precompute_light_positions(layout, width, height)


# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))

    for star in stars:
        star.update()
        star.show(screen)

    for (x, y), lights in light_positions.items():
        color_sample = screen.get_at((x, y))
        for ip, group, index in lights:
            layout[ip][group][index]["color"] = {
                "r": color_sample[0],
                "g": color_sample[1],
                "b": color_sample[2],
            }

    layout_library.replace_value_atomic("installation_layout", json.dumps(layout))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
