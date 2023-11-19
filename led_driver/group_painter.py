import redis
import json
import random
import time

with open('../data/lights.json', 'r') as file:
    house_layout = json.load(file)

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def random_color():
    return {
        'r': random.randint(0, 255),
        'g': random.randint(0, 255),
        'b': random.randint(0, 255)
    }


def random_color_paint_groups():
    for ip in house_layout:
        print("IP: ", ip)
        for group in house_layout[ip]:
            color = random_color()
            for light in house_layout[ip][group]:
                index = light['index']
                key = f"{ip}:{index}"
                print("Setting key: ", key, " to color: ", color)
                redis_client.set(key, json.dumps(color))


while True:
    time.sleep(.2)
    random_color_paint_groups()