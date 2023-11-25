import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from datetime import datetime
import librosa

class CircularAudioBuffer:
    def __init__(self, duration, sample_rate):
        self.duration = duration
        self.sample_rate = sample_rate
        self.buffer_size = duration * sample_rate
        self.recording = np.zeros((self.buffer_size, 2), dtype=np.float32)
        self.current_frame = 0

    def add_frames(self, indata):
        frames = len(indata)
        end_frame = self.current_frame + frames
        if end_frame < self.buffer_size:
            # If the end frame is within the buffer size
            self.recording[self.current_frame:end_frame] = indata
        else:
            # Wrap around the buffer
            remaining = self.buffer_size - self.current_frame
            self.recording[self.current_frame:self.buffer_size] = indata[:remaining]
            self.recording[0:end_frame - self.buffer_size] = indata[remaining:]

        self.current_frame = end_frame % self.buffer_size

    def get_current_buffer(self):
        return np.roll(self.recording, -self.current_frame, axis=0)

    def save(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.wav"
        write(filename, self.sample_rate, self.get_current_buffer())
        print(f"Saved as {filename}")

    def estimate_tempo(self):
        # Convert the buffer to a mono signal by averaging the two channels
        mono_signal = np.mean(self.get_current_buffer(), axis=1)
        
        # Use librosa to estimate the tempo
        tempo, _ = librosa.beat.beat_track(y=mono_signal, sr=self.sample_rate)
        return tempo


def callback(indata, frames, time, status):
    if status:
        print(status)
    buffer.add_frames(indata)

duration = 15  # seconds
sample_rate = 44100

buffer = CircularAudioBuffer(duration, sample_rate)

with sd.InputStream(samplerate=sample_rate, channels=2, callback=callback):
    while True:
        input("Press Enter to save the current 15-second buffer...")  # Blocks until Enter is pressed
        print("Estimated tempo:", buffer.estimate_tempo())
        #buffer.save()

