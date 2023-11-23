import random
import colorsys
from collections import deque

class BrightnessTracker:
    def __init__(self):
        self.brightness_values = deque(maxlen=4)

    def add_brightness(self, brightness):
        if brightness is not None:
            self.brightness_values.append(brightness)

    def get_average_brightness(self):
        return sum(self.brightness_values) / len(self.brightness_values) if self.brightness_values else 0


def get_random_color():
    return {'r': random.randint(0, 255), 'g': random.randint(0, 255), 'b': random.randint(0, 255)}


def color_generator():
    frame = 0
    while True:
        # Assuming a full cycle through the hue spectrum in 360 frames
        hue = frame % 360 / 360.0
        # Convert HSV to RGB (Saturation and Value are set to 1 for full color)
        rgb = colorsys.hsv_to_rgb(hue, 1, 1)
        # Convert to 8-bit RGB format and return as a dictionary
        rgb_dict = {'r': int(rgb[0] * 255), 'g': int(rgb[1] * 255), 'b': int(rgb[2] * 255)}
        yield rgb_dict
        frame += 1


def scale_brightness(value):
    if value is None:
        return 0
    if value < 15:
        return 0
    elif value > 50:
        return 255
    else:
        return int((value - 15) * (255 / (50 - 15)))


def adjust_brightness(color, brightness):
    return {
        'r': int(color['r'] * brightness / 255),
        'g': int(color['g'] * brightness / 255),
        'b': int(color['b'] * brightness / 255)
    }
