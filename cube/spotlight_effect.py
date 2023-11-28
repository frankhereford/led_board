import sys

sys.path.insert(1, "../radio/lib")
import layout as layout_library
import json
import pygame
import random
import colorsys


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


layout = layout_library.read_json_from_file("installation_v2_groups.json")

# Initialization
pygame.init()
height = 50
width = 1 * height
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()


def cycle_hue():
    hue = 0
    while True:
        rgb_color = colorsys.hls_to_rgb(hue / 360, 0.5, 1)  # HLS to RGB
        pygame_color = tuple(int(255 * i) for i in rgb_color)  # Scale to 0-255
        yield pygame_color
        hue = (hue + 1) % 360  # Increment hue


color_generator = cycle_hue()


def bound_value(value, low_limit, high_limit):
    """
    Bounds the given value within the specified limits.

    :param value: The float value to be bounded.
    :param low_limit: The lower limit.
    :param high_limit: The higher limit.
    :return: The bounded value.
    """
    if value < low_limit:
        return low_limit
    elif value > high_limit:
        return high_limit
    return value


light_positions = precompute_light_positions(layout, width, height)

# Circle properties
circle_radius = 5
circle_x, circle_y = width // 2, height // 2
velocity_x, velocity_y = .5, .5  # Adjust these for speed

trail_surface = pygame.Surface((width, height), pygame.SRCALPHA)
fade_amount = 3  # Adjust this for the fade speed

# Main loop
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update circle position
    circle_x += velocity_x
    circle_y += velocity_y

    variance = 0.1

    # Collision detection with slight angle change
    if circle_x - circle_radius <= 0 or circle_x + circle_radius >= width:
        velocity_x *= -1
        velocity_y += random.uniform(
            -1 * variance, variance
        )  # Slight change in y velocity
    if circle_y - circle_radius <= 0 or circle_y + circle_radius >= height:
        velocity_y *= -1
        velocity_x += random.uniform(
            -1 * variance, variance
        )  # Slight change in x velocity

    velocity_x = bound_value(velocity_x, -.6, .6)
    velocity_y = bound_value(velocity_y, -.6, .6)

    trail_surface.fill((0, 0, 0, fade_amount))  # Semi-transparent black surface
    screen.blit(trail_surface, (0, 0))

    circle_color = next(color_generator)

    # Draw the circle
    pygame.draw.circle(screen, circle_color, (circle_x, circle_y), circle_radius)

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
    clock.tick(30)

pygame.quit()
