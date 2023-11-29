# rtl_fm -M wbfm -f 98.9M | play -r 32k -t raw -e s -b 16 -c 1 -V1 -

import json
import sounddevice as sd
from collections import deque
import wave
import time

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


def write_buffer_to_wav(buffer, filename):
    """Write the contents of the buffer to a WAV file."""
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)  # Assuming 16-bit audio, hence 2 bytes per sample
        wav_file.setframerate(int(samplerate))
        wav_file.writeframes(buffer.read_all())


try:
    last_save_time = time.time()

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

            if args.sample and time.time() - last_save_time >= 15:
                buffer.save()  # Use the save method of CircularAudioBuffer
                last_save_time = time.time()

except KeyboardInterrupt:
    exit("Interrupted by user")
