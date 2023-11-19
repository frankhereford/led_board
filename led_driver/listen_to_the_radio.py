import pyaudio
import numpy as np
from scipy.fft import fft
import matplotlib.pyplot as plt

# Initialize PyAudio
pa = pyaudio.PyAudio()

# Open the stream for the microphone
stream = pa.open(format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=1024)

try:
    while True:
        # Read data from the audio stream
        data = np.frombuffer(stream.read(1024), dtype=np.int16)

        # Perform Fourier Transform
        fft_data = fft(data)

        # Process and display the spectrogram
        plt.specgram(data, Fs=44100)
        plt.pause(0.05)
finally:
    stream.stop_stream()
    stream.close()
    pa.terminate()
