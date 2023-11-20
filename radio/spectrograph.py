#!/usr/bin/env python3
"""Show a text-mode spectrogram and xled lights spectrogram using real time audio data."""

import argparse
import math
import shutil
import redis
import json
import itertools

import numpy as np
import sounddevice as sd

from collections import deque

from PIL import Image, ImageDraw, ImageFont

np.set_printoptions(
    linewidth=200,
    formatter={"int": "{:4d}".format},
)

usage_line = " press <enter> to quit, +<enter> or -<enter> to change scaling "
# python ./spectrograph.py -r 200 600 -b 25 -c 32 -g 500 -s -d 7

with open("../data/test_windows_data.json", "r") as file:
    windows_layout = json.load(file)

redis_client = redis.Redis(host="10.10.10.1", port=6379, db=0)

def render_scrolling_text_updated(
    text, width=32, height=32, scroll_speed=1, font_size=24, extra_frames=100
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
        font = ImageFont.truetype("MonaspaceArgon-Bold.otf", font_size)
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
    draw.text((width, ((height - text_height) // 2) - 5), text, font=font, fill=1) # change the subtracted number to scoot up text

    # Scroll the text
    frames = []
    for i in range(0, img_width - width + 1, scroll_speed):
        # Extract the current frame from the image
        frame = img.crop((i, 0, i + width, height))

        for i in range(0, img_width + extra_frames, scroll_speed):
            # Extract the current frame from the image
            frame = img.crop((i, 0, i + width, height))
            # Flip the frame vertically
            #flipped_frame = np.flipud(np.array(frame))
            #frames.append(flipped_frame)
            frames.append(np.array(frame))


        frame_data = np.array(frame)
        frames.append(frame_data)

    return frames




def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text


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
    transformed_y = point_coords[1] * 32  # Transforming Y from [0, 1] to [0, 32]

    # Check if the transformed point is within the area defined by area_coords
    # The area is defined from (x, y) to (x+1, y+1)
    if (
        area_coords[0] <= transformed_x < area_coords[0] + 1
        and area_coords[1] <= transformed_y < area_coords[1] + 1
    ):
        return True
    else:
        return False


try:
    columns, _ = shutil.get_terminal_size()
except AttributeError:
    columns = 80

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    "-l",
    "--list-devices",
    action="store_true",
    help="show list of audio devices and exit",
)
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__ + "\n\nSupported keys:" + usage_line,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser],
)
parser.add_argument(
    "-b",
    "--block-duration",
    type=float,
    metavar="DURATION",
    default=25,
    help="block size (default %(default)s milliseconds)",
)
parser.add_argument(
    "-c", "--columns", type=int, default=32, help="width of spectrogram"
)
parser.add_argument(
    "-d",
    "--device",
    type=int_or_str,
    default=7,
    help="input device (numeric ID or substring)",
)
parser.add_argument(
    "-g",
    "--gain",
    type=float,
    default=500,
    help="initial gain factor (default %(default)s)",
)
parser.add_argument(
    "-r",
    "--range",
    type=float,
    nargs=2,
    metavar=("LOW", "HIGH"),
    default=[200, 600],
    help="frequency range (default %(default)s Hz)",
)

parser.add_argument(
    "-s",
    "--hide-spectrogram",
    action="store_false",
    default=True,
    help="Enable this option to hide the spectrogram.",
)

parser.add_argument(
    "-t",
    "--show-scroll",
    action="store_true",
    default=False,
    help="Enable this option to show scrolling in the standard output.",
)

parser.add_argument(
    "-m",
    "--render-scroll",
    type=int,
    nargs='?',
    const=300,
    default=None,
    help="Enable this option to show scrolling text on the lights. Defaults to 300 if no value is provided.",
)

parser.add_argument(
    "-w",
    "--message",
    type=str,
    nargs='?',
    const="KUTX",
    default="KUTX",
    help="Specify a message to display. Defaults to 'KUTX'.",
)



args = parser.parse_args(remaining)


if args.render_scroll is not None:
    # Create an iterator that repeats each item 4 times
    raw_frames = render_scrolling_text_updated(
        args.message, width=32, height=32, scroll_speed=1, font_size=30, extra_frames=args.render_scroll
    )
else:
    raw_frames = render_scrolling_text_updated(
        args.message, width=32, height=32, scroll_speed=1, font_size=30
    )
repeated_data = itertools.chain.from_iterable(itertools.repeat(x, 3) for x in raw_frames)
text_frames = itertools.cycle(repeated_data)




low, high = args.range
if high <= low:
    parser.error("HIGH must be greater than LOW")

# Create a nice output gradient using ANSI escape sequences.
# Stolen from https://gist.github.com/maurisvh/df919538bcef391bc89f
colors = 30, 34, 35, 91, 93, 97
chars = " :%#\t#%:"
gradient = []
for bg, fg in zip(colors, colors[1:]):
    for char in chars:
        if char == "\t":
            bg, fg = fg, bg
        else:
            gradient.append(f"\x1b[{fg};{bg + 10}m{char}")

try:
    samplerate = sd.query_devices(args.device, "input")["default_samplerate"]

    delta_f = (high - low) / (args.columns - 1)
    fftsize = math.ceil(samplerate / delta_f)
    low_bin = math.floor(low / delta_f)

    sample_buffer = deque(maxlen=32)

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

    def spectrogram_color(value):
        if value < 0 or value > 255:
            raise ValueError("Value must be between 0 and 255")

        if value == 0:
            return {"r": 0, "g": 0, "b": 0}

        # Define the transition points
        blue_end = 255 // 6
        green_end = blue_end + 100

        # Initialize RGB values
        r, g, b = 0, 0, 0

        if value <= blue_end:
            # Fade from black to blue
            b = int(255 * (value / blue_end))
        elif value <= green_end:
            # Fade from blue to green
            b = int(255 * (1 - (value - blue_end) / (green_end - blue_end)))
            g = int(255 * ((value - blue_end) / (green_end - blue_end)))
        else:
            # Fade from green to red
            g = int(255 * (1 - (value - green_end) / (255 - green_end)))
            r = int(255 * ((value - green_end) / (255 - green_end)))

        return {"r": r, "g": g, "b": b}

    def convert_to_color_array(arr):
        if arr.shape != (32, 32):
            return
            # raise ValueError("Array must be 32x32 in size")

        # Create an empty array to hold the RGB values
        color_array = np.empty((32, 32), dtype=object)

        # Apply the spectrogram_color function to each element
        for i in range(arr.shape[0]):
            for j in range(arr.shape[1]):
                color_array[i, j] = spectrogram_color(arr[i, j])

        return color_array

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

    def callback(indata, frames, time, status):
        if status:
            text = " " + str(status) + " "
            print("\x1b[34;40m", text.center(args.columns, "#"), "\x1b[0m", sep="")
        if any(indata):
            text_frame = next(text_frames)
            has_any_text = text_frame.max()

            gain = args.gain
            if has_any_text and args.render_scroll:
                gain = 50

            magnitude = np.abs(np.fft.rfft(indata[:, 0], n=fftsize))
            magnitude *= gain / fftsize
            if args.hide_spectrogram:
                line = (
                    gradient[int(np.clip(x, 0, 1) * (len(gradient) - 1))]
                    for x in magnitude[low_bin : low_bin + args.columns]
                )
                print(*line, sep="", end="\x1b[0m\n")
            

            if args.show_scroll and args.render_scroll:
                for y, row in enumerate(text_frame):
                    for x, pixel in enumerate(row):
                        if pixel:
                            print("X", end="")
                        else:
                            print(".", end="")
                    print()
                print()

            text_frame = np.flip(text_frame, axis=0)

            sample = magnitude[low_bin : low_bin + args.columns]
            sample_buffer.append(sample)
            sample_array = np.array(sample_buffer)
            # normalized_array = sample_array * (255 / sample_array.max()) # always some noise
            normalized_array = sample_array * 255
            normalized_array = normalized_array.astype(np.uint8)
            # print(normalized_array[-1])
            color_matrix = convert_to_color_array(normalized_array)
            if color_matrix is not None:
                light_state = windows_layout.copy()

                for y in range(32):
                    for x in range(32):
                        for key in light_linkage[x][y]:
                            ip, index = key.split(":")
                            index = int(index)

                            if ip == "10.10.10.154":
                                group_name = "Left Window"
                            elif ip == "10.10.10.155":
                                group_name = "Right Window"

                            pixel = text_frame[x][y]
                            if pixel and args.render_scroll:
                                light_state[ip][group_name][index]["color"] = {
                                    "r": 255,
                                    "g": 255,
                                    "b": 255,
                                }
                            else:
                                light_state[ip][group_name][index]["color"] = color_matrix[
                                    y, x
                                ]
                replace_value_atomic(
                    redis_client, "windows_layout", json.dumps(light_state)
                )

        else:
            pass
            # print("no input")

    with sd.InputStream(
        device=args.device,
        channels=1,
        callback=callback,
        blocksize=int(samplerate * args.block_duration / 1000),
        samplerate=samplerate,
    ):
        while True:
            response = input()
            if response in ("", "q", "Q"):
                break
            for ch in response:
                if ch == "+":
                    args.gain *= 2
                elif ch == "-":
                    args.gain /= 2
                else:
                    print(
                        "\x1b[31;40m",
                        usage_line.center(args.columns, "#"),
                        "\x1b[0m",
                        sep="",
                    )
                    break
except KeyboardInterrupt:
    parser.exit("Interrupted by user")
except Exception as e:
    parser.exit(type(e).__name__ + ": " + str(e))
