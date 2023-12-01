import sys

sys.path.insert(1, "../radio/lib")
import layout as layout_library

import pygame
import math
import json
import colorsys

# Initialize Pygame
pygame.init()

# Screen dimensions and setup
width, height = 200, 200
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Simulation")

# Circle properties
circle_center = (width // 2, height // 2)
circle_radius = 150
num_slices = 512

# Colors for each slice
slice_colors = [(0, 0, 0)] * num_slices  # Initialize all slices as black

frame = 0


#! todo stick in library
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


def transform_coordinate(point, target_x_max=100, target_y_max=100):
    x, y = point

    # Transform X
    # Shift the X value from the range [-1, 1] to [0, 2] and then scale to [0, target_x_max]
    x_transformed = (x + 1) * (target_x_max / 2)

    # Transform Y
    # Scale the Y value from the range [0, 1] to [0, target_y_max]
    y_transformed = y * target_y_max

    return (int(x_transformed), int(y_transformed))


def cycle_hue(slice_index):
    hue = 0  # Starting hue is the same for all slices
    rate_of_change = .002
    hue_increment = (
        1 + rate_of_change * slice_index
    )  # Speed of color change increases with slice index

    while True:
        rgb_color = colorsys.hls_to_rgb(hue / 360, 0.5, 1)
        pygame_color = tuple(int(255 * i) for i in rgb_color)
        yield pygame_color
        hue = (hue + hue_increment) % 360


# Create a list of color generators, one for each slice
color_generators = [cycle_hue(i) for i in range(num_slices)]


def set_slice_color(slice_index, color):
    """Set the color of a specific slice."""
    if 0 <= slice_index < num_slices:
        slice_colors[slice_index] = color
    else:
        print("Invalid slice index")


def draw_circle():
    """Draw the circle with colored slices."""
    for i in range(num_slices):
        start_angle = (360 / num_slices) * i
        end_angle = start_angle + (360 / num_slices)
        points = [
            circle_center,
            (
                circle_center[0] + circle_radius * math.cos(math.radians(start_angle)),
                circle_center[1] + circle_radius * math.sin(math.radians(start_angle)),
            ),
            (
                circle_center[0] + circle_radius * math.cos(math.radians(end_angle)),
                circle_center[1] + circle_radius * math.sin(math.radians(end_angle)),
            ),
        ]
        pygame.draw.polygon(screen, slice_colors[i], points)


layout = layout_library.read_json_from_file("installation_v2_groups.json")
light_positions = precompute_light_positions(layout, width, height)


# Main game loop
running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    frame += 1

    screen.fill((0, 0, 0))  # Fill the screen with black
    draw_circle()  # Draw the circle with colored slices

    for n in range(num_slices):
        set_slice_color(n, next(color_generators[n]))

    for (x, y), lights in light_positions.items():
        # Invert the y-coordinate to correct the upside-down issue
        inverted_y = height - y - 1  # Subtracting 1 because coordinates are 0-indexed

        color_sample = screen.get_at((x, inverted_y))
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
