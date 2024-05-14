import os
import glob
import whisper

# Load the Whisper model (you can choose a different model size if needed)
model = whisper.load_model("base")

# Define the base directory where your files are located
base_dir = "/home/frank/development/lightboard/voice/samples/spleeter_output"

# Iterate over all 'vocals.wav' files in the directory structure
for vocals_file in glob.glob(os.path.join(base_dir, "**/vocals.wav"), recursive=True):
    # Transcribe the audio file
    result = model.transcribe(vocals_file)

    # Print the file path and its transcription
    print(f"Transcribing {vocals_file}...")
    print(result["text"])
    print("\n" + "-" * 80 + "\n")
