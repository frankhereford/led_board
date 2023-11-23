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
            #time.sleep(0.05) 

except KeyboardInterrupt:
    exit("Interrupted by user")


