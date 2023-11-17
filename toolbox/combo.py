import sys
import random
import time

# writing this against main in respective github repos
from xled_plus.multicontrol import MultiHighControlInterface
from xled_plus.effect_base import Effect
from xled_plus.ledcolor import hsl_color

board = MultiHighControlInterface(['10.10.10.151', '10.10.10.149'])

class RedisEffect(Effect):
    def __init__(self, ctr):
        super(RedisEffect, self).__init__(ctr)
    
    def reset(self, numframes):
        pass

    def map_to_range(self, value, max):
        return round(value * max)

    def random_color(self):
        """Returns a random color as an RGB tuple."""
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def get_pixel(self, x, y):
        print("x: ", x, "y: ", y)
        return self.random_color()
        return tuple(map(int, value)) if value else (0, 0, 0)

    def getnext(self):
        return self.ctr.make_layout_pattern(lambda position: self.get_pixel(*position))

RedisEffect(board).launch_rt()
