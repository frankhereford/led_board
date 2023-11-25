import sounddevice as sd
import numpy as np
import librosa
from collections import deque

samplerate = 44100
#samplerate = 48000

# Initialize a buffer to accumulate audio data
audio_buffer = np.array([], dtype=np.float32)
# Initialize a deque to store the last 10 tempo values
tempo_values = deque(maxlen=10)

# Define the callback function to process the incoming audio
def audio_callback(indata, frames, time, status):
    global audio_buffer, tempo_values
    if status:
        print(status)
    # Append new audio data to the buffer
    audio_data = np.frombuffer(indata, dtype=np.float32)
    audio_buffer = np.concatenate((audio_buffer, audio_data))[-1 * samplerate *10:]


    # Process the buffer if it's long enough
    if len(audio_buffer) >= samplerate * 10:  # For example, 10 seconds of audio
        tempo, beats = librosa.beat.beat_track(y=audio_buffer, sr=samplerate)
        if beats.any():
            #print(f"Tempo: {tempo}, Beats: {beats}")
            # Append the new tempo value to the deque
            tempo_values.append(tempo)
            # Calculate the average tempo
            average_tempo = sum(tempo_values) / len(tempo_values)
            print(f"Average Tempo (last 10): {average_tempo}")
        # Clear the buffer after processing
        audio_buffer = np.array([], dtype=np.float32)

# Stream audio from the default input device
with sd.InputStream(callback=audio_callback):
    sd.sleep(10000000)  # Keep the stream open for a defined time
