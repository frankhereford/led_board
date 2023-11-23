# rtl_fm -M wbfm -f 98.9M | play -r 32k -t raw -e s -b 16 -c 1 -V1 -

import time
import json
import random
import colorsys

import sounddevice as sd

from lib.argparse import parse_arguments
from lib.layout import read_json_from_file, replace_value_atomic
from lib.spectrograph import *

args = parse_arguments()
layout = read_json_from_file("installation_v2_groups.json")

inject_args(args)
create_text_frames(args)
samplerate = create_spectrograph_parameters(layout)
from collections import deque


class BrightnessTracker:
    def __init__(self):
        self.brightness_values = deque(maxlen=4)

    def add_brightness(self, brightness):
        if brightness is not None:
            self.brightness_values.append(brightness)

    def get_average_brightness(self):
        return sum(self.brightness_values) / len(self.brightness_values) if self.brightness_values else 0

brightness_tracker = BrightnessTracker()


def get_random_color():
    return {'r': random.randint(0, 255), 'g': random.randint(0, 255), 'b': random.randint(0, 255)}

def color_generator():
    frame = 0
    while True:
        # Assuming a full cycle through the hue spectrum in 360 frames
        hue = frame % 360 / 360.0
        # Convert HSV to RGB (Saturation and Value are set to 1 for full color)
        rgb = colorsys.hsv_to_rgb(hue, 1, 1)
        # Convert to 8-bit RGB format and return as a dictionary
        rgb_dict = {'r': int(rgb[0] * 255), 'g': int(rgb[1] * 255), 'b': int(rgb[2] * 255)}
        yield rgb_dict
        frame += 1

color_gen = color_generator()

def scale_brightness(value):
    if value is None:
        return 0
    if value < 15:
        return 0
    elif value > 50:
        return 255
    else:
        return int((value - 15) * (255 / (50 - 15)))

def adjust_brightness(color, brightness):
    return {
        'r': int(color['r'] * brightness / 255),
        'g': int(color['g'] * brightness / 255),
        'b': int(color['b'] * brightness / 255)
    }



try:
    with sd.InputStream(
        device=args.device,
        channels=1,
        callback=callback,
        blocksize=int(samplerate * args.block_duration / 1000),
        samplerate=samplerate,
    ):
        while True:
            frame = get_spectrograph_frame()
            brightness = scale_brightness(get_brightness())
            brightness_tracker.add_brightness(brightness)
            average_brightness = brightness_tracker.get_average_brightness()
            if not frame:
                continue

            #print("brightness", brightness)
            color = adjust_brightness(next(color_gen), average_brightness)
            for ip in frame:
                if ip in ['10.10.10.155', '10.10.10.154']:
                    continue
                for group in frame[ip]:
                    for index, light in enumerate(frame[ip][group]):
                        #frame[ip][group][index]['color'] = {'r': 255, 'g': 0, 'b': 255}
                        #frame[ip][group][index]['color'] = get_random_color()
                        frame[ip][group][index]['color'] = color

            replace_value_atomic(
                "installation_layout", json.dumps(frame)
            )




            time.sleep(0.05) 

except KeyboardInterrupt:
    exit("Interrupted by user")


