import time

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
