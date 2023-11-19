import time
import json
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import math
import redis
import random

with open("../data/test_windows_data.json", "r") as file:
    windows_layout = json.load(file)

redis_client = redis.Redis(host="localhost", port=6379, db=0)


def render_scrolling_text_updated(
    text, width=32, height=32, scroll_speed=1, font_size=24
):
    """
    Render scrolling text for a low-resolution display, updated for Pillow 9.5.0.
    The font size is increased to make the text take up more of the display.

    :param text: The text to be displayed.
    :param width: Width of the display in pixels.
    :param height: Height of the display in pixels.
    :param scroll_speed: Number of pixels to shift the text per frame.
    :param font_size: Font size for the text.
    :return: A list of frames, each frame being a 2D array representing the display.
    """

    # Load a larger font
    try:
        # Change 'arial.ttf' to the path of a TrueType font available on your system if needed
        font = ImageFont.truetype("DejaVuSans.ttf", font_size)
    except IOError:
        print("Default font not found, using load_default() instead.")
        font = ImageFont.load_default()

    # Determine text size using getbbox and create an image wide enough to contain the scrolled text
    bbox = font.getbbox(text)
    text_width, text_height = bbox[2], bbox[3]
    img_width = text_width + width
    img = Image.new("1", (img_width, height), color=0)

    # Create a drawing context
    draw = ImageDraw.Draw(img)

    # Draw the text onto the image
    draw.text((width, ((height - text_height) // 2) - 5), text, font=font, fill=1)

    # Scroll the text
    frames = []
    for i in range(0, img_width - width + 1, scroll_speed):
        # Extract the current frame from the image
        frame = img.crop((i, 0, i + width, height))

        for i in range(0, img_width - width + 1, scroll_speed):
            # Extract the current frame from the image
            frame = img.crop((i, 0, i + width, height))
            # Flip the frame vertically
            #flipped_frame = np.flipud(np.array(frame))
            #frames.append(flipped_frame)
            frames.append(np.array(frame))


        frame_data = np.array(frame)
        frames.append(frame_data)

    return frames


def map_x(value):
    return (value / 16) - 1


def map_y(value):
    return value / 32


def map_coordinate(x, y):
    return (map_x(x), map_y(y))


def distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

def is_within_area(area_coords, point_coords):
    """
    Function to check if the transformed point is within the defined area.

    Parameters:
    area_coords (tuple): A tuple of two integers, each between 0 and 31.
    point_coords (tuple): A tuple of two floats, X between -1 and 1, Y between 0 and 1.

    Returns:
    bool: True if the transformed point is within the area, otherwise False.
    """

    # Transform the point coordinates to 32x32 space
    transformed_x = (point_coords[0] + 1) * 16  # Transforming X from [-1, 1] to [0, 32]
    transformed_y = point_coords[1] * 32        # Transforming Y from [0, 1] to [0, 32]

    # Check if the transformed point is within the area defined by area_coords
    # The area is defined from (x, y) to (x+1, y+1)
    if (area_coords[0] <= transformed_x < area_coords[0] + 1 and
        area_coords[1] <= transformed_y < area_coords[1] + 1):
        return True
    else:
        return False


def random_color():
    return {
        'r': random.randint(0, 255),
        'g': random.randint(0, 255),
        'b': random.randint(0, 255)
    }

def blank_canvas():
    for ip in windows_layout:
        for group in windows_layout[ip]:
            for light in windows_layout[ip][group]:
                index = light['index']
                key = f"{ip}:{index}"
                redis_client.set(key, json.dumps({'r': 0, 'g': 0, 'b': 0}))


def replace_value_atomic(redis_client, key, value):
    """
    Replaces the value of a key in Redis atomically using pipeline.
    
    :param redis_client: The Redis client instance.
    :param key: The key whose value is to be replaced.
    :param value: The new value to set for the key.
    """
    pipeline = redis_client.pipeline()
    pipeline.delete(key)
    pipeline.set(key, value)
    pipeline.execute()


# Example usage
frames = render_scrolling_text_updated(
    "HI AUSTIN!", width=32, height=32, scroll_speed=2, font_size=30
)

blank_canvas()


light_linkage = []

for y in range(32):
    light_linkage.append([])
    for x in range(32):
        light_linkage[y].append([])

        for ip in windows_layout:
            for group in windows_layout[ip]:
                for light in windows_layout[ip][group]:
                    index = light["index"]
                    key = f"{ip}:{index}"

                    light_coordinate = (
                        light["coordinate"]["x"],
                        light["coordinate"]["y"],
                    )

                    if is_within_area((x, y), light_coordinate):
                        light_linkage[y][x].append(key)

for frame in frames:
    time.sleep(.15)

    frame = frame[::-1]
    #print(frame)
    #quit()

    for y, row in enumerate(frame):
        for x, pixel in enumerate(row):
            if pixel:
                print("X", end="")
            else:
                print(".", end="")
        print()
    print()


    light_state = windows_layout.copy()

    for y, row in enumerate(frame):
        for x, pixel in enumerate(row):
            for key in light_linkage[y][x]:
                ip, index= key.split(":")
                index = int(index)

                if ip == '10.10.10.154':
                    group_name = 'Left Window'
                elif ip == '10.10.10.155':
                    group_name = 'Right Window'

                if pixel:
                    #print("ip: ", ip, "index: ", index)
                    #print("light_state[ip_address][group_name][index]: ", light_state[ip][group_name][index])
                    light_state[ip][group_name][index]['color'] = {'r': 0, 'g': 0, 'b': 255}
                    #redis_client.set(key, json.dumps({'r': 0, 'g': 0, 'b': 255}))
                else:
                    light_state[ip][group_name][index]['color'] = {'r': 0, 'g': 0, 'b': 0}
                    #redis_client.set(key, json.dumps({'r': 0, 'g': 0, 'b': 0}))
        
    replace_value_atomic(redis_client, 'windows_layout', json.dumps(light_state))

quit()

light_linkage = []

for y in range(32):
    light_linkage.append([])
    for x in range(32):
        light_linkage[y].append([])
        font_coordinate = map_coordinate(x, 31 - y)
        #print(font_coordinate)

        for ip in windows_layout:
            for group in windows_layout[ip]:
                for light in windows_layout[ip][group]:
                    index = light["index"]
                    key = f"{ip}:{index}"

                    light_coordinate = (
                        light["coordinate"]["x"],
                        light["coordinate"]["y"],
                    )

                    if distance(light_coordinate, font_coordinate) < 0.1:
                        light_linkage[y][x].append(key)


print("Light linkage: ", light_linkage[10][10])

for frame in frames:
    for y, row in enumerate(frame):
        for x, pixel in enumerate(row):
            if pixel:
                print("X", end="")
            else:
                print(".", end="")
        print()
    print()


    time.sleep(.2)
    blank_canvas()
    for y, row in enumerate(frame):
        for x, pixel in enumerate(row):
            if pixel:
                for key in light_linkage[y][x]:
                    redis_client.set(key, json.dumps({'r': 255, 'g': 0, 'b': 0}))
            else:
                pass
                #print(".", end="")




quit()

# Print the first few frames as an example
for frame in frames:
    for y, row in enumerate(frame):
        for x, pixel in enumerate(row):
            if pixel:
                print("X", end="")
            else:
                print(".", end="")
        print()

    for y, row in enumerate(frame):
        for x, pixel in enumerate(row):
            font_coordinate = map_coordinate(x, y)

            for ip in windows_layout:
                for group in windows_layout[ip]:
                    for light in windows_layout[ip][group]:
                        index = light["index"]
                        key = f"{ip}:{index}"

                        light_coordinate = (
                            light["coordinate"]["x"],
                            light["coordinate"]["y"],
                        )
                        # print(light_coordinate)
                        if distance(light_coordinate, font_coordinate) < 0.3:
                            redis_client.set(
                                key, json.dumps({"r": 255, "g": 0, "b": 0})
                            )
                        else:
                            redis_client.set(
                                key, json.dumps({"r": 0, "g": 0, "b": 255})
                            )

                        # print(light_coordinates)
                        # redis_client.set(key, json.dumps({'r': 0, 'g': 0, 'b': 0}))
