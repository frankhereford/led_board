import redis
import random
import time

# Initialize a single Redis client connection
redis_client = redis.Redis(host='localhost', port=6379, db=0)

w, h = 24, 24  # for a grid of 24x24 LEDs


def generate_tuples(step=3):
    for r in range(0, 256, step):
        yield (r, 0, 0)
    for g in range(0, 256, step):
        yield (255, g, 0)
    for b in range(0, 256, step):
        yield (255, 255, b)
    for r in reversed(range(0, 256, step)):
        yield (r, 255, 255)
    for g in reversed(range(0, 256, step)):
        yield (0, g, 255)
    for b in reversed(range(0, 256, step)):
        yield (0, 0, b)

def set_display_value(x, y, value):
    key = f'display:{x}:{y}'
    with redis_client.pipeline() as pipeline:
        pipeline.multi()
        pipeline.delete(key)
        pipeline.rpush(key, *value)
        pipeline.execute()


def main():
    tuple_generator = generate_tuples()
    while True:
        for y in range(h):
            for x in range(w):
                try:
                    value = next(tuple_generator)
                except StopIteration:
                    tuple_generator = generate_tuples()
                    value = next(tuple_generator)
                set_display_value(x, y, value)
                # Control the speed of updates to prevent overwhelming Redis
                time.sleep(.05)

if __name__ == "__main__":
    main()