# rtl_fm -M wbfm -f 98.9M | play -r 32k -t raw -e s -b 16 -c 1 -V1 -

import json
import sounddevice as sd
from collections import deque

from lib.spectrograph import *
from lib.argparse import parse_arguments
from lib.layout import read_json_from_file, replace_value_atomic
from lib.utilities import BrightnessTracker
from lib.audio_buffer import CircularAudioBuffer
from lib.lights import LightsRedux


args = parse_arguments()
layout = read_json_from_file("installation_v2_groups.json")
light_redux = LightsRedux(layout)
group_names = light_redux.get_group_names()
inject_args(args)
create_text_frames(args)
samplerate = create_spectrograph_parameters(layout)
brightness_tracker = BrightnessTracker()

def callback(indata, frames, time, status): # handle incoming audio sample
    spectrograph_callback(indata, frames, time, status)
    buffer.add_frames(indata)

duration = 15  # seconds
buffer = CircularAudioBuffer(duration, int(samplerate))

try:
    with sd.InputStream(
        device=args.device,
        channels=1,
        callback=callback,
        blocksize=int(samplerate * args.block_duration / 1000),
        samplerate=samplerate,
    ):
        while True:
            tempo = buffer.estimate_tempo()
            set_bpm(tempo) # set this in the spectorgraph module so i can print it
            light_redux.set_bpm(tempo)
            frame = get_spectrograph_frame()
            if not frame:
                continue

            light_redux.advance_frame()

            for ip in frame:
                if ip in ["10.10.10.155", "10.10.10.154"]:
                    continue
                for group in frame[ip]:
                    for index, light in enumerate(frame[ip][group]):
                        frame[ip][group][index]["color"] = light_redux.get_color(
                            ip, group, index
                        )

            replace_value_atomic("installation_layout", json.dumps(frame))

except KeyboardInterrupt:
    exit("Interrupted by user")
