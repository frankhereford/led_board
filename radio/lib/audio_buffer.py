import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from datetime import datetime, timedelta
import librosa


class CircularAudioBuffer:
    def __init__(self, duration, sample_rate):
        self.duration = duration
        self.sample_rate = sample_rate
        self.buffer_size = duration * sample_rate
        self.recording = np.zeros((self.buffer_size, 2), dtype=np.float32)
        self.current_frame = 0
        self.last_tempo = None
        self.last_tempo_time = None
        self.cache_duration = timedelta(seconds=5)

    def add_frames(self, indata):
        frames = len(indata)
        end_frame = self.current_frame + frames
        if end_frame < self.buffer_size:
            # If the end frame is within the buffer size
            self.recording[self.current_frame : end_frame] = indata
        else:
            # Wrap around the buffer
            remaining = self.buffer_size - self.current_frame
            self.recording[self.current_frame : self.buffer_size] = indata[:remaining]
            self.recording[0 : end_frame - self.buffer_size] = indata[remaining:]

        self.current_frame = end_frame % self.buffer_size

    def get_current_buffer(self):
        return np.roll(self.recording, -self.current_frame, axis=0)

    def save(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.wav"
        write(filename, self.sample_rate, self.get_current_buffer())
        print(f"Saved as {filename}")

    def estimate_tempo(self):
        # Check if we can use the cached tempo
        if (
            self.last_tempo_time
            and datetime.now() - self.last_tempo_time < self.cache_duration
        ):
            return self.last_tempo

        # Convert the buffer to a mono signal by averaging the two channels
        mono_signal = np.mean(self.get_current_buffer(), axis=1)

        # Use librosa to estimate the tempo
        tempo, _ = librosa.beat.beat_track(y=mono_signal, sr=self.sample_rate)
        tempo = int(tempo)

        # Update cache
        self.last_tempo = tempo
        self.last_tempo_time = datetime.now()

        #print("Estimating tempo...", tempo)

        return tempo
