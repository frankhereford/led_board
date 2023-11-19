import cProfile
import sys
import json
import random
import time
import redis

from xled_plus.ledcolor import hsl_color
from xled_plus.effect_base import Effect
from xled_plus.highcontrol import HighControlInterface
from xled.simple_udp import SimpleUDPClient

with open('../data/lights.json', 'r') as file:
    house_layout = json.load(file)

redis_client = redis.Redis(host='localhost', port=6379, db=0)

class BleakEffect(Effect):
    def __init__(self, ctr):
        super(BleakEffect, self).__init__(ctr)
    
    def reset(self, numframes):
        strings = {
            '10.10.10.78': 400,
            '10.10.10.151': 600,
            '10.10.10.152': 600,
        }

    def ticking_color(self, index):
        if index == int(time.time()) % 100:
            return (255, 0, 0)
        else:
            return (0, 0, 0)

    def random_color(self, index):
        print(self.ctr.host)
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def get_light_color(self, index):
        ip = self.ctr.host
        key = f"{ip}:{index}"
        color_data = redis_client.get(key)
        
        if color_data is None:
            # Set default value to black
            default_color = {'r': 0, 'g': 0, 'b': 0}
            redis_client.set(key, json.dumps(default_color))
            return (0, 0, 0)
        else:
            # Load the color data and return as a tuple
            color_data = json.loads(color_data)
            return (color_data['r'], color_data['g'], color_data['b'])


    def getnext(self):
        return self.ctr.make_func_pattern(lambda index: self.get_light_color(index))
        #return self.ctr.make_layout_pattern(lambda position: self.get_pixel(*position))


def bleak(ip):
    print("Starting bleak effect on: ", ip)
    board = HighControlInterface(ip)
    board._udpclient = SimpleUDPClient(7777, board.host) # alt UDP client
    BleakEffect(board).launch_rt()

host = sys.argv[1]
bleak(host)
#cProfile.run('bleak(host)', 'profile_output')

