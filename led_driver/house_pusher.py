import redis
import json
import random
import time

with open('lights.json', 'r') as file:
    house_layout = json.load(file)

redis_client = redis.Redis(host='localhost', port=6379, db=0)

if True:
    for ip in house_layout:
        for group in house_layout[ip]:
            for light in house_layout[ip][group]:
                index = light['index']
                key = f"{ip}:{index}"
                redis_client.set(key, json.dumps({'r': 0, 'g': 0, 'b': 0}))
    #quit()

all_pixels = []
for ip in house_layout:
    for group in house_layout[ip]:
        for light in house_layout[ip][group]:
            index = light['index']
            key = f"{ip}:{index}"
            all_pixels.append({'key': key, 'brightness': 255})

active_pixels = []
iteration = 0

while True:
    # time.sleep(0.05)
    print(f"Active pixels: {len(active_pixels)}")
    print(f"Iteration: {iteration}")
    if iteration == 0:
        iteration += 1
        random_element = random.choice(all_pixels)
        active_pixels.append(random_element)
    elif iteration == 10:
        iteration = 0
    else:
        iteration += 1

    #input()

    for pixel in active_pixels:
        brightness = pixel['brightness']
        #print("Brightness: ", brightness)
        brightness -= 1
        if brightness <= 0:
            active_pixels.remove(pixel)
            redis_client.set(pixel['key'], json.dumps({'r': 0, 'g': 0, 'b': 0}))
        else:
            pixel['brightness'] = brightness
            redis_client.set(pixel['key'], json.dumps({'r': brightness, 'g': brightness, 'b': brightness}))

