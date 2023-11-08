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
        #initialize_display()
        self.populate_display()

    def map_to_range(self, value, max):
        return round(value * max)

    def populate_display(self, width=24, height=24):
        for x in range(width):
            for y in range(height): 
                x_mapped = self.map_to_range(x + 0.5, x_width - 1)  # Shift x to a 0 to 1 range before mapping
                #x_mapped = self.map_to_range(x_width - x - 1.5, x_width - 1)
                y_mapped = self.map_to_range(y, y_height - 1)
                #print(f"{x}, {y} -> {x_mapped}, {y_mapped}")
                x_flipped = 23 - x_mapped 
                key = f"display:{x_flipped}:{y_mapped}"
                value = redis_client.lrange(key, 0, -1)

    def get_value_from_redis(self, x, y):
        x_mapped = self.map_to_range(x + 0.5, x_width - 1)  # Shift x to a 0 to 1 range before mapping
        #x_mapped = self.map_to_range(x_width - x - 1.5, x_width - 1)
        y_mapped = self.map_to_range(y, y_height - 1)
        #print(f"{x}, {y} -> {x_mapped}, {y_mapped}")
        x_flipped = 23 - x_mapped 
        key = f"display:{x_flipped}:{y_mapped}"
        value = redis_client.lrange(key, 0, -1)
        return tuple(map(int, value)) if value else (0, 0, 0)

    def getnext(self):
        return self.ctr.make_layout_pattern(lambda position: self.get_value_from_redis(*position))

RedisEffect(board).launch_rt()
