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

def blank_canvas():
    for ip in house_layout:
        for group in house_layout[ip]:
            for light in house_layout[ip][group]:
                index = light['index']
                key = f"{ip}:{index}"
                redis_client.set(key, json.dumps({'r': 0, 'g': 0, 'b': 0}))

def get_all_pixels():
    all_pixels = []
    for ip in house_layout:
        for group in house_layout[ip]:
            for light in house_layout[ip][group]:
                index = light['index']
                key = f"{ip}:{index}"
                all_pixels.append({'key': key, 'brightness': 255})
    return all_pixels

def set_all_random(all_pixels):
    for pixel in all_pixels:
        color = {
            'r': 100,
            'g': 0,
            'b': 0,
        }
        redis_client.set(pixel['key'], json.dumps(random_color()))
        #redis_client.set(pixel['key'], json.dumps(color))


# blank_canvas()
blank_pixels = get_all_pixels()
set_all_random(blank_pixels)
