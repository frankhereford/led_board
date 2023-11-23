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
    def __init__(self, modulus=8, advance_rate=20, group_size=2):
        self.current_frame = 0
        self.modulus = modulus
        self.advance_rate = advance_rate
        self.group_size = group_size
        self.internal_counter = 0

    def is_active(self, index):
        # Adjusted to return True for a configurable number of lights in the group
        for i in range(self.group_size):
            if (index - self.current_frame - i) % self.modulus == 0:
                return True
        return False

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
        # Sets a new group size
        self.group_size = new_group_size

frame_tracker = FrameTracker()


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
                            #frame[ip][group][index]['color'] = {'r': 255, 'g': 0, 'b': 255}
                            #frame[ip][group][index]['color'] = get_random_color()
                            frame[ip][group][index]['color'] = color
                        else:
                            frame[ip][group][index]['color'] = {'r': 0, 'g': 0, 'b': 0}

            replace_value_atomic(
                "installation_layout", json.dumps(frame)
            )
            #time.sleep(0.05) 

except KeyboardInterrupt:
    exit("Interrupted by user")


