import redis
import random
import time

# Initialize a single Redis client connection
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def generate_tuples(step=5):
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



def set_display_value(i, value):
    with redis_client.pipeline() as pipeline:
        pipeline.multi()
        pipeline.delete(f'display:{i}')
        pipeline.rpush(f'display:{i}', *value)
        pipeline.execute()

def main():
    tuple_generator = generate_tuples()
    while True:
        for i in range(577):
            try:
                value = next(tuple_generator)
            except StopIteration:
                tuple_generator = generate_tuples()
                value = next(tuple_generator)
            set_display_value(i, value)
            time.sleep(.05)

if __name__ == "__main__":
    main()