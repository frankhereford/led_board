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

layout = board.fetch_layout()
print(layout)