#!/usr/bin/env python3

import sys
import redis
import random
import json

from xled_plus.ledcolor import hsl_color
from xled_plus.effect_base import Effect
from xled_plus.highcontrol import HighControlInterface

host = sys.argv[1]
board = HighControlInterface(host)

redis_client = redis.Redis(host='localhost', port=6379, db=0)


class RedisEffect(Effect):
    def __init__(self, ctr):
        super(RedisEffect, self).__init__(ctr)
    
    def reset(self, numframes):
        self.step_count = 0
        #self.set_bounding_boxes()
        pass

    def set_bounding_boxes(self):
        bounding_boxes = [
            {"color": [255, 0, 0], "min_x": 0.02, "max_x": 0.26, "min_y": 0.15, "max_y": 0.83}, 
            {"color": [0, 255, 0], "min_x": -0.28, "max_x": 0.0, "min_y": 0.19, "max_y": 0.62},
            {"color": [0, 0, 255], "min_x": -0.18, "max_x": 0.0, "min_y": 0.63, "max_y": 0.9}, 
            {"color": [255, 0, 0], "min_x": -0.51, "max_x": -0.3, "min_y": 0.58, "max_y": 0.97},
            {"color": [0, 255, 0], "min_x": 0.31, "max_x": 0.46, "min_y": 0.3, "max_y": 0.73},
            {"color": [0, 0, 255], "min_x": -0.5, "max_x": -0.3, "min_y": 0.18, "max_y": 0.49},
            {"color": [0, 0, 255], "min_x": 0.34, "max_x": 0.43, "min_y": 0.07, "max_y": 0.25},
            {"color": [0, 0, 255], "min_x": -0.29, "max_x": -0.2, "min_y": 0.67, "max_y": 0.83},
        ]

        redis_client.set('bounding_boxes', json.dumps(bounding_boxes))


    def random_color(self):
        """Returns a random color as an RGB tuple."""
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def get_pixel(self, x, y):
        return self.random_color()
        return tuple(map(int, value)) if value else (0, 0, 0)

    def is_within_extent(self, x, y):
        return (self.extent['min_x'] <= x <= self.extent['max_x']) and \
            (self.extent['min_y'] <= y <= self.extent['max_y'])

    def find_color_in_boxes(self, x, y, bounding_boxes, selected_boxes):
        for i, box in enumerate(bounding_boxes):
            if i in selected_boxes:
                if box['min_x'] <= x <= box['max_x'] and box['min_y'] <= y <= box['max_y']:
                    return tuple(box['color'])
        return None

    def get_bounding_box_color(self, x, y):
        bounding_boxes_data = redis_client.get('bounding_boxes')
        
        if bounding_boxes_data is not None:
            bounding_boxes = json.loads(bounding_boxes_data)
            
            color = self.find_color_in_boxes(x, y, bounding_boxes, [0,1,2,3,4,5,6,7])
            if color is not None:
                return color
            else:
                return self.random_color() 
            #for box in bounding_boxes:
                #if box['min_x'] <= x <= box['max_x'] and box['min_y'] <= y <= box['max_y']:
                    #return tuple(box['color'])

        return (0, 0, 0)


    def blue_and_red(self, index):
        if index == self.step_count:
            return (255, 0, 0)
        else:
            return (0, 0, 255)

    def inspect_layout(self, x, y):

        #if self.is_within_extent(x, y):
            #return (255, 0, 0)

        return (0, 0, 255)

    def getnext(self):
        #print("Step: ", self.step_count)
        self.step_count += 1

        #return self.ctr.make_func_pattern(lambda index: self.blue_and_red(index))
        #return self.ctr.make_layout_pattern(lambda position: self.get_pixel(*position))
        return self.ctr.make_layout_pattern(lambda position: self.get_bounding_box_color(*position))

RedisEffect(board).launch_rt()
