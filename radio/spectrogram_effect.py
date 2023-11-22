#import math
#import json
#import redis
#import shutil
#import itertools
#import numpy as np
#import sounddevice as sd
#from collections import deque

from lib.argparse import parse_arguments
from lib.layout import read_json_from_file
from lib.scroll import render_scrolling_text_updated

args = parse_arguments()
lights_layout = read_json_from_file("installation_v2_groups.json")

text_frames = None
if args.render_scroll:
    text_frames = render_scrolling_text_updated(
        args.message, width=32, height=32, scroll_speed=1, font_size=30, extra_frames=args.render_scroll
    )
