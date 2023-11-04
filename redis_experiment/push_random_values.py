import redis
import random
import time

# Initialize a single Redis client connection
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def generate_tuples(n):
    return [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(n)]


def set_display_value(i, value):
    with redis_client.pipeline() as pipeline:
        pipeline.multi()
        pipeline.delete(f'display:{i}')
        pipeline.rpush(f'display:{i}', *value)
        pipeline.execute()

def main():
    while True:
      for i in range(577):
          value = generate_tuples(1)[0]  # Generate a single tuple
          set_display_value(i, value)
          time.sleep(.05)

if __name__ == "__main__":
    main()