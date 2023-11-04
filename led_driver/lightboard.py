import sys
import random
import redis

from xled_plus.highcontrol import HighControlInterface
from xled_plus.effect_base import Effect
from xled_plus.ledcolor import hsl_color

# Initialize a single Redis client connection
redis_client = redis.Redis(host='localhost', port=6379, db=0)

host = sys.argv[1]
board = HighControlInterface(host)

def generate_tuples(n):
    return [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(n)]

def initialize_display(length=576):    
    redis_client.flushall()
    pipeline = redis_client.pipeline()

    for i in range(length):
        pipeline.multi()
        pipeline.delete(f'display:{i}')
        random_values = generate_tuples(1)[0]
        pipeline.rpush(f'display:{i}', *random_values)
        pipeline.execute()

class RedisEffect(Effect):
    def __init__(self, ctr):
        super(RedisEffect, self).__init__(ctr)
    
    def reset(self, numframes):
        initialize_display()

    def get_value_from_redis(self, index):
        key = f"display:{index}"
        value = redis_client.lrange(key, 0, -1)
        return tuple(map(int, value)) if value else (0, 0, 0)
    
    def getnext(self):
        return self.ctr.make_func_pattern(lambda i: self.get_value_from_redis(i))
    
RedisEffect(board).launch_rt()
