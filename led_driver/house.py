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

cache = {}
cache_expiry = 0.01  # seconds


with open('../data/lights.json', 'r') as file:
    house_layout = json.load(file)

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_color_data_with_cache():
    current_time = time.time()
    if 'color_data' not in cache or current_time - cache['color_data']['timestamp'] > cache_expiry:
        color_data_json = redis_client.get('installation_layout').decode('utf-8')

        if color_data_json:
            color_data = json.loads(color_data_json)
            cache['color_data'] = {
                'data': color_data,
                'timestamp': current_time
            }
        else:
            return None
    return cache['color_data']['data']

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

    def dict_to_rgb(self, color_dict):
        """
        Converts a dictionary with keys 'r', 'g', and 'b' to an RGB tuple.

        :param color_dict: Dictionary with the keys 'r', 'g', and 'b'.
        :return: Tuple representing the RGB color.
        """
        return (color_dict['r'], color_dict['g'], color_dict['b'])


    def get_light_color_fast(self, index):
        color_data = get_color_data_with_cache()
        if not color_data:
            return (0, 0, 0)
        ip = self.ctr.host
        
        group_name = next(iter(color_data[ip]))

        if 'color' in color_data[ip][group_name][index]:
            return self.dict_to_rgb(color_data[ip][group_name][index]['color'])
        else:
            return (0, 0, 0)

    def getnext(self):
        return self.ctr.make_func_pattern(lambda index: self.get_light_color_fast(index))
        #return self.ctr.make_layout_pattern(lambda position: self.get_pixel(*position))


def bleak(ip):
    print("Starting bleak effect on: ", ip)
    board = HighControlInterface(ip)
    board._udpclient = SimpleUDPClient(7777, board.host) # alt UDP client
    BleakEffect(board).launch_rt()

host = sys.argv[1]
bleak(host)
#cProfile.run('bleak(host)', 'profile_output')

