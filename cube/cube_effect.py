import sys

sys.path.insert(1, "../radio/lib")

import layout as layout_library
import json

import pygame
import math

layout = layout_library.read_json_from_file("installation_v2_groups.json")

# Initialization
pygame.init()
height = 100
width = 1 * height  # Aspect ratio of 2:1
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# Scale factor
scale_factor = 30  # Adjust this value to scale the cube size

# Cube points
cube_points = [
    [-1, -1, -1],
    [1, -1, -1],
    [1, 1, -1],
    [-1, 1, -1],
    [-1, -1, 1],
    [1, -1, 1],
    [1, 1, 1],
    [-1, 1, 1],
]

# Scale cube points
cube_points = [[scale_factor * x for x in point] for point in cube_points]

# Cube edges
edges = [
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 0),
    (4, 5),
    (5, 6),
    (6, 7),
    (7, 4),
    (0, 4),
    (1, 5),
    (2, 6),
    (3, 7),
]


# Function to draw the cube with adjustable line thickness
def draw_cube(points, screen, width, height, line_thickness=5):
    for edge in edges:
        points1 = points[edge[0]]
        points2 = points[edge[1]]
        pygame.draw.line(
            screen,
            (255, 255, 255),
            (width // 2 + points1[0], height // 2 + points1[1]),
            (width // 2 + points2[0], height // 2 + points2[1]),
            line_thickness,
        )


def transform_coordinate(point, target_x_max=100, target_y_max=100):
    """
    Transforms a point from the first coordinate space (-1 <= X <= 1, 0 < Y < 1)
    to the second coordinate space (0 <= X <= target_x_max, 0 <= Y <= target_y_max).

    :param point: Tuple (x, y) representing the point in the first coordinate space.
    :param target_x_max: The maximum value of X in the target coordinate space.
    :param target_y_max: The maximum value of Y in the target coordinate space.
    :return: Tuple representing the transformed point in the second coordinate space.
    """
    x, y = point

    # Transform X
    # Shift the X value from the range [-1, 1] to [0, 2] and then scale to [0, target_x_max]
    x_transformed = (x + 1) * (target_x_max / 2)

    # Transform Y
    # Scale the Y value from the range [0, 1] to [0, target_y_max]
    y_transformed = y * target_y_max

    return (int(x_transformed), int(y_transformed))


# Function to rotate points in 3D
def rotate_point(point, angleX, angleY, angleZ):
    rad = math.radians(angleX)
    cosa, sina = math.cos(rad), math.sin(rad)
    y = point[1] * cosa - point[2] * sina
    z = point[1] * sina + point[2] * cosa
    rad = math.radians(angleY)
    cosb, sinb = math.cos(rad), math.sin(rad)
    x = point[0] * cosb + z * sinb
    z = z * cosb - point[0] * sinb
    rad = math.radians(angleZ)
    cosc, sinc = math.cos(rad), math.sin(rad)
    x = x * cosc - y * sinc
    y = x * sinc + y * cosc
    return [x, y, z]


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

light_lookup = precompute_light_positions(layout, width, height)
print(light_lookup)


# Main loop
running = True
angleX, angleY, angleZ = 0, 0, 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))
    rotated_points = [
        rotate_point(point, angleX, angleY, angleZ) for point in cube_points
    ]
    draw_cube(rotated_points, screen, width, height)

    for ip in layout:
        for group in layout[ip]:
            for index, light in enumerate(layout[ip][group]):
                transformed_point = transform_coordinate(
                    (
                        light["coordinate"]["x"],
                        light["coordinate"]["y"],
                    ),
                    width - 1,
                    height - 1,
                )
                color_sample = screen.get_at(transformed_point)
                layout[ip][group][index]["color"] = {
                    "r": color_sample[0],
                    "g": color_sample[1],
                    "b": color_sample[2],
                }

    layout_library.replace_value_atomic("installation_layout", json.dumps(layout))

    pygame.display.flip()
    # clock.tick(60)

    angleX += 1
    angleY += 1

pygame.quit()
