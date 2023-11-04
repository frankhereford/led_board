import redis
import random
import time

# Initialize a single Redis client connection
redis_client = redis.Redis(host='localhost', port=6379, db=0)

w, h = 24, 24  # Define the width and height for a grid

def generate_tuples(n):
    return [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(n)]

def set_display_value(x, y, value):
    key = f'display:{x}:{y}'
    with redis_client.pipeline() as pipeline:
        pipeline.multi()
        pipeline.delete(key)
        pipeline.rpush(key, *value)
        pipeline.execute()

def main():
    while True:
        for i in range(w * h):
            x, y = divmod(i, w)  # Convert linear index to x, y coordinates
            value = generate_tuples(1)[0]  # Generate a single tuple
            set_display_value(x, y, value)
            time.sleep(.05)

if __name__ == "__main__":
    main()
