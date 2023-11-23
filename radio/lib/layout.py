import json
import os

def read_json_from_file(filename):
    file_path = os.path.join("../data/", filename)
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def write_json_to_file(data, filename):
    file_path = os.path.join("../data/", filename)
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)
