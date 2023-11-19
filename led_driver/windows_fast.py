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

with open('../data/test_windows_data.json', 'r') as file:
    house_layout = json.load(file)

redis_client = redis.Redis(host='localhost', port=6379, db=0)

class BleakEffect(Effect):
    def __init__(self, ctr):
        super(BleakEffect, self).__init__(ctr)
    
    def reset(self, numframes):
        strings = {
            '10.10.10.154': 210,
            '10.10.10.155': 210,
        }

    def dict_to_rgb(self, color_dict):
        """
        Converts a dictionary with keys 'r', 'g', and 'b' to an RGB tuple.

        :param color_dict: Dictionary with the keys 'r', 'g', and 'b'.
        :return: Tuple representing the RGB color.
        """
        return (color_dict['r'], color_dict['g'], color_dict['b'])


    def get_light_color(self, index):
        ip = self.ctr.host
        color_data_json = redis_client.get('windows_layout').decode('utf-8')
        color_data = json.loads(color_data_json)
        #print(color_data)
        if ip == '10.10.10.154':
            group_name = 'Left Window'
        elif ip == '10.10.10.155':
            group_name = 'Right Window'

        #print(color_data[ip][group_name][index])
        if 'color' in color_data[ip][group_name][index]:

            return self.dict_to_rgb(color_data[ip][group_name][index]['color'])
            print(color_data[ip][group_name][index]['color'])
        else:
            return (0, 0, 0)


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

