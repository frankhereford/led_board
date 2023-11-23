# rtl_fm -M wbfm -f 98.9M | play -r 32k -t raw -e s -b 16 -c 1 -V1 -

import time
import json
import random
import colorsys
import sounddevice as sd
from collections import deque
from lib.spectrograph import *
from lib.argparse import parse_arguments
from lib.layout import read_json_from_file, replace_value_atomic
from lib.utilities import BrightnessTracker, get_random_color, color_generator, scale_brightness, adjust_brightness


args = parse_arguments()
layout = read_json_from_file("installation_v2_groups.json")
inject_args(args)
create_text_frames(args)
samplerate = create_spectrograph_parameters(layout)
brightness_tracker = BrightnessTracker()
color_gen = color_generator()


class FrameTracker:
    def __init__(self, modulus=50, advance_rate=20, group_size=1, fade_length=0):
        self.current_frame = 0
        self.modulus = modulus
        self.advance_rate = advance_rate
        self.group_size = group_size
        self.fade_length = fade_length
        self.internal_counter = 0

    def is_active(self, index):
        # Check if the index is within the active group
        for i in range(self.group_size):
            if (index - self.current_frame - i) % self.modulus == 0:
                return 255  # Full brightness

        # Check for fade effect behind the group
        for i in range(1, self.fade_length + 1):
            fade_index = (index - self.current_frame - self.group_size - i + 1) % self.modulus
            if fade_index < self.fade_length:
                # Calculate brightness (linear interpolation from 255 to 0)
                brightness = 255 * (1 - fade_index / self.fade_length)
                return int(brightness)

        return 0  # Pixel is not active

    def advance_frame(self):
        self.internal_counter += 1
        if self.internal_counter >= self.advance_rate:
            self.current_frame += 1
            self.internal_counter = 0

    def set_modulus(self, new_modulus):
        self.modulus = new_modulus

    def set_advance_rate(self, new_rate):
        self.advance_rate = new_rate

    def set_group_size(self, new_group_size):
        self.group_size = new_group_size

    def set_fade_length(self, new_fade_length):
        self.fade_length = new_fade_length

frame_tracker = FrameTracker()

def dim_color(color, brightness):
    # Ensure brightness is within the valid range
    brightness = max(0, min(brightness, 255))
    
    # Calculate the dimmed color components
    dimmed_color = {
        'r': int(color['r'] * (brightness / 255)),
        'g': int(color['g'] * (brightness / 255)),
        'b': int(color['b'] * (brightness / 255))
    }
    
    return dimmed_color

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

            frame_tracker.advance_frame()

            #reduced_average_brightness = int(average_brightness / 255 * 10)
            #frame_tracker.set_modulus(reduced_average_brightness + 1)

            color = adjust_brightness(next(color_gen), average_brightness)
            for ip in frame:
                if ip in ['10.10.10.155', '10.10.10.154']:
                    continue
                for group in frame[ip]:
                    for index, light in enumerate(frame[ip][group]):
                        if frame_tracker.is_active(index):
                            activity_brightness = frame_tracker.is_active(index)
                            dimmed_color = dim_color(color, activity_brightness)
                            #frame[ip][group][index]['color'] = {'r': 255, 'g': 0, 'b': 255}
                            #frame[ip][group][index]['color'] = get_random_color()
                            frame[ip][group][index]['color'] = dimmed_color
                        else:
                            frame[ip][group][index]['color'] = {'r': 0, 'g': 0, 'b': 0}

            replace_value_atomic(
                "installation_layout", json.dumps(frame)
            )
            #time.sleep(0.05) 

except KeyboardInterrupt:
    exit("Interrupted by user")


