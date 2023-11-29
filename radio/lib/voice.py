import shutil
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


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
