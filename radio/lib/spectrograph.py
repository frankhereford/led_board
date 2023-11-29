import math
import sounddevice as sd
from collections import deque
import numpy as np
import time as libtime
import redis
import json
import time
import itertools
from PIL import Image, ImageDraw, ImageFont

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
    text_frames,
    brightness,
    bpm,
) = (None, None, None, None, None, None, None, None, None, None, None, None, None)

spectrograph_frame = None

get_spectrograph_frame = lambda: spectrograph_frame
get_brightness = lambda: brightness


def inject_args(args_in):
    global args
    args = args_in

def set_bpm(bpm_in):
    global bpm
    bpm = bpm_in

def create_text_frames(args):
    global text_frames
    if args.render_scroll:
        raw_frames = render_scrolling_text(
            args.message,
            width=32,
            height=32,
            scroll_speed_up=1,
            scroll_speed_down=2,
            font_size=30,
            extra_frames=args.render_scroll,
        )


def render_scrolling_text(
    text,
    width=32,
    height=32,
    scroll_speed_up=1,
    scroll_speed_down=3,
    font_size=24,
    extra_frames=100,
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
        # font = ImageFont.truetype("MonaspaceArgon-Bold.otf", font_size)
        font = ImageFont.truetype("DejaVuSerif-Bold.ttf", font_size)
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
    draw.text(
        (width, ((height - text_height) // 2) - 5), text, font=font, fill=1
    )  # change the subtracted number to scoot up text

    # Scroll the text
    frames = []
    for i in range(0, img_width - width + 1, scroll_speed_up):
        # Extract the current frame from the image
        frame = img.crop((i, 0, i + width, height))

        for i in range(0, img_width + extra_frames, scroll_speed_up):
            # Extract the current frame from the image
            frame = img.crop((i, 0, i + width, height))
            frames.append(np.array(frame))

        frame_data = np.array(frame)
        frames.append(frame_data)

    repeated_data = itertools.chain.from_iterable(
        itertools.repeat(x, scroll_speed_down) for x in frames
    )

    global text_frames
    text_frames = itertools.cycle(repeated_data)


def create_spectrograph_parameters(layout_in):
    global low, high, gradient, samplerate, delta_f, fftsize, low_bin, sample_buffer, light_linkage, layout

    layout = layout_in
    low, high = args.range
    gradient = define_gradient()

    samplerate = sd.query_devices(args.device, "input")["default_samplerate"]

    delta_f = (high - low) / (args.columns - 1)
    fftsize = math.ceil(samplerate / delta_f)
    #print("fftsize:", fftsize)
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


def is_within_window(area_coords, point_coords, window):
    """
    Check if the transformed point is within the defined window.

    Parameters:
    area_coords (tuple): Coordinates on the LED grid (0-31, 0-31).
    point_coords (tuple): Original point coordinates (-1 to 1, 0 to 1).
    window (dict): Window boundaries {'x_min': -0.5, 'x_max': 0.5, 'y_min': 0.25, 'y_max': 0.75}.

    Returns:
    bool: True if within the window, otherwise False.
    """

    # Scale and translate the point coordinates to fit within the window
    x_range = window["x_max"] - window["x_min"]
    y_range = window["y_max"] - window["y_min"]

    transformed_x = ((point_coords[0] - window["x_min"]) / x_range) * 32
    transformed_y = ((point_coords[1] - window["y_min"]) / y_range) * 32

    # Check if the point is within the defined area on the LED grid
    return (
        area_coords[0] <= transformed_x < area_coords[0] + 1
        and area_coords[1] <= transformed_y < area_coords[1] + 1
    )


def convert_to_color_array(arr):
    # print()
    # print("input", arr)
    if arr.shape != (32, 32):
        return
        # raise ValueError("Array must be 32x32 in size")

    # Create an empty array to hold the RGB values
    color_array = np.empty((32, 32), dtype=object)

    # Apply the spectrogram_color function to each element
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            # print("arr[i, j]", arr[i, j])
            color_array[i, j] = spectrogram_color(arr[i, j])

    # print("color_array", color_array)
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
    window = {"x_min": 0.10, "x_max": 0.60, "y_min": 0.15, "y_max": 0.5}

    light_linkage = []

    for y in range(32):
        light_linkage.append([])
        for x in range(32):
            light_linkage[y].append([])

            for ip in layout:
                if ip not in ("10.10.10.154", "10.10.10.155"):
                    continue
                for group in layout[ip]:
                    for light in layout[ip][group]:
                        index = light["index"]
                        key = f"{ip}:{index}"

                        light_coordinate = (
                            light["coordinate"]["x"],
                            light["coordinate"]["y"],
                        )

                        if is_within_window((x, y), light_coordinate, window):
                            light_linkage[y][x].append(key)
                        # if is_within_area((x, y), light_coordinate):
                        # light_linkage[y][x].append(key)
    return light_linkage


def spectrograph_callback(indata, frames, time, status):
    global spectrograph_frame
    if status:
        text = " " + str(status) + " "
        print("\x1b[34;40m", text.center(args.columns, "#"), "\x1b[0m", sep="")
    if any(indata):
        rms_amplitude = np.sqrt(np.mean(np.square(indata)))

        # Normalize to a range (0 to max_brightness)
        normalized_amplitude = np.clip(rms_amplitude, 0, 1)
        led_brightness = int(normalized_amplitude * 255)

        global brightness
        brightness = led_brightness

        has_any_text = False
        if args.render_scroll:
            text_frame = next(text_frames)
            has_any_text = text_frame.max()

        gain = args.gain
        if has_any_text and args.render_scroll:
            gain = 10

        magnitude = np.abs(np.fft.rfft(indata[:, 0], n=fftsize))
        magnitude *= gain / fftsize
        if args.hide_spectrogram:
            line = (
                gradient[int(np.clip(x, 0, 1) * (len(gradient) - 1))]
                for x in magnitude[low_bin : low_bin + args.columns]
            )
            print(*line, sep="", end=" \x1b[0m")
            print(bpm)


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
                            light_state[ip][group_name][index]["color"] = color_matrix[
                                y, x
                            ]
            spectrograph_frame = light_state

    else:
        pass
        # print("no input")
