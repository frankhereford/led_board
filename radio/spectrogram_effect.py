
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


import json
import sounddevice as sd
from collections import deque
import time

from lib.spectrograph import *
from lib.argparse import parse_arguments
from lib.layout import read_json_from_file, replace_value_atomic
from lib.utilities import BrightnessTracker
from lib.audio_buffer import CircularAudioBuffer
from lib.lights import LightsRedux
from lib.voice import clean_directories

from spleeter.separator import Separator
import whisper
import numpy as np
import tempfile
import wave

import logging

# Set the logging level to WARNING to suppress INFO messages
logging.getLogger('spleeter').setLevel(logging.WARNING)


import warnings

# Suppress specific warnings
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

import tensorflow as tf

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # This will hide the TensorFlow C++ level warnings
tf.get_logger().setLevel('ERROR')         # This will suppress TensorFlow Python warnings



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
    voice_buffer.add_frames(indata)


duration = 15  # seconds
buffer = CircularAudioBuffer(duration, int(samplerate))

# Instantiate VoiceBuffer with a 30-second buffer
voice_buffer_duration = 30  # seconds
voice_buffer = CircularAudioBuffer(voice_buffer_duration, int(samplerate))

# Initialize Spleeter and Whisper
separator = Separator('spleeter:2stems')  # for separating vocals and accompaniment
whisper_model = whisper.load_model("base")

def create_timestamped_filename(directory, prefix='audio', extension='.wav'):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    return os.path.join(directory, f"{prefix}_{timestamp}{extension}")

def save_to_wavefile(audio_data, directory, filename=None):
    if not filename:
        filename = create_timestamped_filename(directory)
    filepath = os.path.join(directory, filename)
    with wave.open(filepath, 'wb') as wave_file:
        wave_file.setnchannels(1)
        wave_file.setsampwidth(2)  # Assuming 16-bit audio
        wave_file.setframerate(samplerate)
        wave_file.writeframes(audio_data)
    print(filepath)
    #quit()
    return filepath

def transcribe_audio(model, file_path):
    transcription = model.transcribe(file_path)
    return transcription["text"]

def split_audio(input_wav, output_directory):
    # Initialize the spleeter separator for 2 stems: vocals and accompaniment
    separator = Separator('spleeter:2stems')

    # Perform the separation
    separator.separate_to_file(input_wav, output_directory)

    # Determine the paths of the output files
    base_name = os.path.splitext(os.path.basename(input_wav))[0]
    vocal_path = os.path.join(output_directory, base_name, 'vocals.wav')
    accompaniment_path = os.path.join(output_directory, base_name, 'accompaniment.wav')

    # Check if both files exist and return their paths
    if os.path.exists(vocal_path) and os.path.exists(accompaniment_path):
        return vocal_path, accompaniment_path
    else:
        return None, None

def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


if args.sample:
    directories_to_clean = [
        "/home/frank/development/lightboard/voice/samples/spleeter_output",
        "/home/frank/development/lightboard/voice/samples/raw_samples",
        "/home/frank/development/lightboard/voice/samples/in_flight_voice"  # Add the new directory to the list
    ]

    clean_directories(directories_to_clean)
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

                # Inside the main loop where you save the audio data
                if args.sample and time.time() - last_save_time >= 15:
                    # Check if there is audio data to save
                    if np.any(voice_buffer.get_current_buffer() != 0):
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav', dir='/tmp') as temp_file:
                            voice_buffer.save(voice_buffer.get_current_buffer(), temp_file.name)

                            # Transcribe the audio (optional, if you need transcription)
                            transcription = transcribe_audio(whisper_model, temp_file.name)

                            # Split the audio into vocal and accompaniment
                            vocal_path, accompaniment_path = split_audio(temp_file.name, '/tmp')

                            # Save the vocal track to the specified directory with a timestamp
                            vocal_filename = create_timestamped_filename("/home/frank/development/lightboard/voice/samples/in_flight_voice", prefix='vocal')
                            os.rename(vocal_path, vocal_filename)

                            # Remove the original temp file and accompaniment file
                            os.remove(temp_file.name)
                            os.remove(accompaniment_path)

                        # Print transcription or filename (as needed)
                        print("Vocal track saved:", vocal_filename)
                        print("Transcription:", transcription)

                    else:
                        print("No audio data to save.")

                    last_save_time = time.time()

            replace_value_atomic("installation_layout", json.dumps(frame))


except KeyboardInterrupt:
    exit("Interrupted by user")
