import redis
import sys

# Initialize a single Redis client connection
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def set_all_pixels(r, g, b):
    for x in range(24):
        for y in range(24):
            set_display_value(x, y, (r, g, b))

def set_single_pixel(x, y, r, g, b):
    set_display_value(x, y, (r, g, b))

def set_display_value(x, y, value):
    key = f'display:{x}:{y}'
    with redis_client.pipeline() as pipeline:
        pipeline.multi()
        pipeline.delete(key)
        pipeline.rpush(key, *value)
        pipeline.execute()

def process_instruction(instruction):
    parts = [int(part) for part in instruction.split()]
    if len(parts) == 3:
        set_all_pixels(*parts)
    elif len(parts) == 5:
        set_single_pixel(*parts)
    else:
        print("Invalid instruction format.")

def main():
    print("Enter your instructions:")
    for line in sys.stdin:
        if 'exit' == line.strip():
            break  # Exit the loop if 'exit' command is given
        process_instruction(line.strip())

if __name__ == "__main__":
    main()
