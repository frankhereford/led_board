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
    draw.text((width, (height - text_height) // 2), text, font=font, fill=1)

    # Scroll the text
    frames = []
    for i in range(0, img_width - width + 1, scroll_speed):
        # Extract the current frame from the image
        frame = img.crop((i, 0, i + width, height))
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


# Example usage
frames = render_scrolling_text_updated(
    "Hello, Austin!", width=32, height=32, scroll_speed=2, font_size=36
)

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
