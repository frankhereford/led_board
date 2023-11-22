import math
import sounddevice as sd
from collections import deque
import numpy as np
import time as libtime
import redis
import json
import time

text_frames = None
(
    low,
    high,
    gradient,
    samplerate,
    delta_f,
    fftsize,
    low_bin,
    sample_buffer,
    light_linkage,
    layout,
    redis_client,
) = (None, None, None, None, None, None, None, None, None, None, None)


def inject_args(args_in):
    global args
    args = args_in


def create_text_frames(args):
    if args.render_scroll:
        text_frames = render_scrolling_text_updated(
            args.message,
            width=32,
            height=32,
            scroll_speed=1,
            font_size=30,
            extra_frames=args.render_scroll,
        )


def create_spectrograph_parameters(layout_in):
    global low, high, gradient, samplerate, delta_f, fftsize, low_bin, sample_buffer, light_linkage, layout, redis_client
    
    redis_client = redis.Redis(host="localhost", port=6379, db=0)


    layout = layout_in
    low, high = args.range
    gradient = define_gradient()

    samplerate = sd.query_devices(args.device, "input")["default_samplerate"]

    delta_f = (high - low) / (args.columns - 1)
    fftsize = math.ceil(samplerate / delta_f)
    print("fftsize:", fftsize)
    low_bin = math.floor(low / delta_f)

    sample_buffer = deque(maxlen=32)

    light_linkage = make_light_linkage(layout)
    return samplerate


def define_gradient():
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
    return gradient


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

def convert_to_color_array(arr):
    #print()
    #print("input", arr)
    if arr.shape != (32, 32):
        return
        # raise ValueError("Array must be 32x32 in size")

    # Create an empty array to hold the RGB values
    color_array = np.empty((32, 32), dtype=object)

    # Apply the spectrogram_color function to each element
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            #print("arr[i, j]", arr[i, j])
            color_array[i, j] = spectrogram_color(arr[i, j])

    #print("color_array", color_array)
    return color_array

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


def make_light_linkage(layout):
    light_linkage = []

    for y in range(32):
        light_linkage.append([])
        for x in range(32):
            light_linkage[y].append([])

            for ip in layout:
                if ip not in ('10.10.10.154', '10.10.10.155'):
                    continue
                for group in layout[ip]:
                    for light in layout[ip][group]:
                        index = light["index"]
                        key = f"{ip}:{index}"

                        light_coordinate = (
                            light["coordinate"]["x"],
                            light["coordinate"]["y"],
                        )

                        if is_within_area((x, y), light_coordinate):
                            light_linkage[y][x].append(key)
    return light_linkage


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
        has_any_text = False
        if args.render_scroll:
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

        if args.render_scroll:
            text_frame = np.flip(text_frame, axis=0)

        sample = magnitude[low_bin : low_bin + args.columns]
        sample_buffer.append(sample)
        sample_array = np.array(sample_buffer)
        # normalized_array = sample_array * (255 / sample_array.max()) # always some noise
        normalized_array = sample_array * 255
        normalized_array = normalized_array.astype(np.uint8)
        color_matrix = convert_to_color_array(normalized_array)
        if color_matrix is not None:
            light_state = layout.copy()

            for y in range(32):
                for x in range(32):
                    for key in light_linkage[x][y]:
                        ip, index = key.split(":")
                        index = int(index)

                        # this gets you the first one every time!
                        group_name = next(iter(layout[ip]))

                        pixel = False
                        if args.render_scroll:
                            pixel = text_frame[x][y]
                        if pixel and args.render_scroll:
                            light_state[ip][group_name][index]["color"] = {
                                "r": 255,
                                "g": 255,
                                "b": 255,
                            }
                        else:
                            light_state[ip][group_name][index]["color"] = color_matrix[ y, x ]
            replace_value_atomic(
                redis_client, "installation_layout", json.dumps(light_state)
            )

    else:
        pass
        # print("no input")
