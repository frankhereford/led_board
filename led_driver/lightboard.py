import sys
import random
import redis
import math

from xled_plus.highcontrol import HighControlInterface
from xled_plus.effect_base import Effect
from xled_plus.ledcolor import hsl_color

x_width = 24
y_height = 24

# Initialize a single Redis client connection
redis_client = redis.Redis(host='localhost', port=6379, db=0)

host = sys.argv[1]
board = HighControlInterface(host)

def generate_tuples(n):
    return [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(n)]

def initialize_display(width=24, height=24):    
    redis_client.flushall()
    pipeline = redis_client.pipeline()

    for x in range(width):
        for y in range(height):
            pipeline.multi()
            pipeline.delete(f'display:{x}:{y}')
            random_values = generate_tuples(1)[0]
            pipeline.rpush(f'display:{x}:{y}', *random_values)
            pipeline.execute()

class RedisEffect(Effect):
    def __init__(self, ctr):
        super(RedisEffect, self).__init__(ctr)
    
    def reset(self, numframes):
        initialize_display()

    def map_to_range(self, value, max):
        return math.floor(value * max)

    def get_value_from_redis(self, x, y):
        x = self.map_to_range(x, x_width - 1) + (x_width // 2)
        y = self.map_to_range(y, y_height - 1)
        key = f"display:{x}:{y}"
        value = redis_client.lrange(key, 0, -1)
        return tuple(map(int, value)) if value else (0, 0, 0)

    def getnext(self):
        return self.ctr.make_layout_pattern(lambda position: self.get_value_from_redis(*position))

RedisEffect(board).launch_rt()
