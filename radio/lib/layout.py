import json
import os
import redis

redis_client = redis.Redis(host="10.10.10.1", port=6379, db=0)


def read_json_from_file(filename):
    file_path = os.path.join("../data/", filename)
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


def write_json_to_file(data, filename):
    file_path = os.path.join("../data/", filename)
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


def replace_value_atomic(key, value):
    """
    Replaces the value of a key in Redis atomically using pipeline.

    :param redis_client: The Redis client instance.
    :param key: The key whose value is to be replaced.
    :param value: The new value to set for the key.
    """
    pipeline = redis_client.pipeline()
    pipeline.delete(key)
    pipeline.set(key, value)
    pipeline.execute()
