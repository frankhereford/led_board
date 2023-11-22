#import math
#import json
#import redis
#import shutil
#import itertools
#import numpy as np
#import sounddevice as sd
#from collections import deque

from lib.argparse import parse_arguments
args = parse_arguments()

from lib.scroll import render_scrolling_text_updated
text_frames = render_scrolling_text_updated("Hello World", width=32, height=32, scroll_speed=1, font_size=24, extra_frames=100)

from lib.layout import read_json_from_file
lights_layout = read_json_from_file("lights_layout.json")
