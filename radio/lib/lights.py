import time
import random
import colorsys

class LightsRedux:
    def __init__(self, initial_config, bpm=60):
        self.lights = {}
        for ip, groups in initial_config.items():
            self.lights[ip] = {}
            for group_name, lights in groups.items():
                self.lights[ip][group_name] = [
                    {'index': light['index'], 'coordinate': light['coordinate'], 'color': {'r': 0, 'g': 0, 'b': 0}}
                    for light in lights
                ]
        self.bpm = bpm
        self.last_beat_time = time.time()
        self.group_names = self.get_group_names()
        self.color_gen = self.color_generator()
        self.beat_count = 0  # Initialize beat counter
        # Assign individual color generators to each group
        self.group_generators = {}
        for group_name in self.group_names:
            speed = random.uniform(0.8, 5)  # Adjust this range as needed
            self.group_generators[group_name] = self.color_generator(speed)

    def color_generator(self, speed=1):
        frame = 0
        while True:
            #print("speed", speed)
            hue = (frame * speed) % 360 / 360.0
            rgb = colorsys.hsv_to_rgb(hue, 1, 1)
            rgb_dict = {'r': int(rgb[0] * 255), 'g': int(rgb[1] * 255), 'b': int(rgb[2] * 255)}
            yield rgb_dict
            frame += 1

    def advance_frame(self):
        current_time = time.time()
        self._darken_lights_by_percentage(3)

        if self.bpm == 0:
            return
        beat_interval = 60 / self.bpm  # Convert bpm to seconds per beat
        if current_time - self.last_beat_time >= beat_interval:
            self._update_on_beat()
            self.last_beat_time = current_time

    def _darken_lights_by_percentage(self, percentage):
        for ip in self.lights:
            for group in self.lights[ip].values():
                for light in group:
                    light['color'] = {color: max(0, int(value * (1 - percentage / 100))) for color, value in light['color'].items()}


    def get_random_color(self):
        return {'r': random.randint(0, 255), 'g': random.randint(0, 255), 'b': random.randint(0, 255)}

    def get_random_hsl_color(self, hue=None, saturation=None, lightness=None):
        # If hue, saturation, or lightness are not provided, assign them random values
        hue = random.randint(0, 360) if hue is None else hue
        saturation = random.uniform(0, 1) if saturation is None else saturation
        lightness = random.uniform(0, 1) if lightness is None else lightness

        # Convert HSL to RGB
        chroma = (1 - abs(2 * lightness - 1)) * saturation
        x = chroma * (1 - abs((hue / 60) % 2 - 1))
        match = lightness - chroma / 2

        if hue < 60:
            red, green, blue = chroma, x, 0
        elif hue < 120:
            red, green, blue = x, chroma, 0
        elif hue < 180:
            red, green, blue = 0, chroma, x
        elif hue < 240:
            red, green, blue = 0, x, chroma
        elif hue < 300:
            red, green, blue = x, 0, chroma
        else:
            red, green, blue = chroma, 0, x

        red, green, blue = [int(255 * (value + match)) for value in (red, green, blue)]

        return {'r': red, 'g': green, 'b': blue}

    def _update_on_beat(self):
        print("Beat!")
        self.beat_count += 1
        for group_name in self.group_names:
            color = next(self.group_generators[group_name])
            self.set_color_by_group(group_name, color)

    def set_bpm(self, new_bpm):
        """
        Sets a new BPM (beats per minute).
        """
        self.bpm = new_bpm


    def get_color(self, ip, group, index):
        """
        Returns the color of the light identified by ip, group, and index.
        """
        try:
            light = self.lights[ip][group][index]
            return light['color']
        except KeyError:
            return "Light not found"


    def get_group_names(self):
        """
        Returns a list of all unique group names.
        """
        group_names = set()
        for ip in self.lights:
            for group_name in self.lights[ip]:
                print("group_name", group_name)
                if group_name in ['Left Window', 'Right Window', 'Hidden Roof Lights', 'Around the Bend', 'Thin Window Bridges']:
                    continue
                group_names.add(group_name)
        return list(group_names)


    def set_color_by_group(self, group_name, color):
        """
        Sets the color of all lights in a given group to the specified color.
        """
        for ip in self.lights:
            if group_name in self.lights[ip]:
                for index, light in enumerate(self.lights[ip][group_name]):
                    if abs(index - self.beat_count) % 5 == 0:
                        light['color'] = color



class Lights:
    def __init__(self, modulus=30):
        self.modulus = modulus
        self.frame = 0
        self.set_tempo(120)  # Default tempo is 60 BPM
        self.last_advance_time = time.time()
        self.light_cache = {}  # Initialize cache for light colors


    def set_tempo(self, bpm):
        # Calculate time interval for each advance based on bpm
        if bpm == 0:
            bpm = 1
        self.advance_interval = 60.0 / bpm

    def advance_frame(self):
        current_time = time.time()
        if current_time - self.last_advance_time >= self.advance_interval:
            self.frame += 1
            self.last_advance_time = current_time

    def get_light_color(self, index, group):
        light_id = (index, group)  # Unique identifier for each light
        if (index % self.modulus) == self.frame % self.modulus:
            self.light_cache[light_id] = {'r': 255, 'g': 255, 'b': 255}  # Store white light in cache
            return self.light_cache[light_id]
        else:
            if light_id in self.light_cache:
                # Reduce brightness by 50%
                cached_color = self.light_cache[light_id]
                reduced_color = {color: max(int(value * 0.999), 0) for color, value in cached_color.items()}
                
                # Check if reduced color is less than #101010, then remove from cache
                if all(value <= 16 for value in reduced_color.values()):
                    del self.light_cache[light_id]
                    return {'r': 0, 'g': 0, 'b': 0}
                else:
                    self.light_cache[light_id] = reduced_color
                    return reduced_color
            else:
                return {'r': 0, 'g': 0, 'b': 0}  # Return black if not in cache
