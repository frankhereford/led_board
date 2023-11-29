import shutil
import os
import time

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from spleeter.separator import Separator

def clean_directories(paths):
    for path in paths:
        # Check if the path exists
        if os.path.exists(path):
            # Iterate over all items in the directory
            for filename in os.listdir(path):
                file_path = os.path.join(path, filename)

                try:
                    # If it's a file, remove it
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    # If it's a directory, remove it and all its contents
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f'Failed to delete {file_path}. Reason: {e}')
        else:
            print(f"Path does not exist: {path}")

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
