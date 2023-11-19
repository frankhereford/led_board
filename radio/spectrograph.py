#!/usr/bin/env python3
"""Show a text-mode spectrogram using live microphone data."""
import argparse
import math
import shutil
import redis
import json

import numpy as np
import sounddevice as sd

from collections import deque

np.set_printoptions(
    linewidth=200,
    formatter={'int': '{:4d}'.format},
    )

usage_line = " press <enter> to quit, +<enter> or -<enter> to change scaling "
#python ./spectrograph.py -r 200 600 -b 25 -c 32 -g 500 -s -d 7

with open("../data/test_windows_data.json", "r") as file:
    windows_layout = json.load(file)

redis_client = redis.Redis(host="10.10.10.1", port=6379, db=0)



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
    transformed_y = point_coords[1] * 32        # Transforming Y from [0, 1] to [0, 32]

    # Check if the transformed point is within the area defined by area_coords
    # The area is defined from (x, y) to (x+1, y+1)
    if (area_coords[0] <= transformed_x < area_coords[0] + 1 and
        area_coords[1] <= transformed_y < area_coords[1] + 1):
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
    "-d", "--device", type=int_or_str, default=7, help="input device (numeric ID or substring)"
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
    "-s", "--hide-spectrogram",
    action="store_false",
    default=True,
    help="Enable this option to hide the spectrogram.",
)


args = parser.parse_args(remaining)
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
            return {'r': 0, 'g': 0, 'b': 0}

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

        return {'r': r, 'g': g, 'b': b}


    def convert_to_color_array(arr):
        if arr.shape != (32, 32):
            return
            #raise ValueError("Array must be 32x32 in size")

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
            magnitude = np.abs(np.fft.rfft(indata[:, 0], n=fftsize))
            magnitude *= args.gain / fftsize
            if args.hide_spectrogram:
                line = (
                    gradient[int(np.clip(x, 0, 1) * (len(gradient) - 1))]
                    for x in magnitude[low_bin : low_bin + args.columns]
                )
                print(*line, sep="", end="\x1b[0m\n")
            sample = magnitude[low_bin : low_bin + args.columns]
            sample_buffer.append(sample)
            sample_array = np.array(sample_buffer)
            #normalized_array = sample_array * (255 / sample_array.max()) # always some noise
            normalized_array = sample_array * 255
            normalized_array = normalized_array.astype(np.uint8)
            #print(normalized_array[-1])
            color_matrix = convert_to_color_array(normalized_array)
            if color_matrix is not None:
                light_state = windows_layout.copy()

                for y in range(32):
                    for x in range(32):
                        for key in light_linkage[x][y]:
                            ip, index= key.split(":")
                            index = int(index)

                            if ip == '10.10.10.154':
                                group_name = 'Left Window'
                            elif ip == '10.10.10.155':
                                group_name = 'Right Window'

                            light_state[ip][group_name][index]['color'] = color_matrix[y, x]
                replace_value_atomic(redis_client, 'windows_layout', json.dumps(light_state))

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
