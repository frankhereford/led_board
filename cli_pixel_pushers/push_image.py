import redis
from PIL import Image
import sys
import requests
from io import BytesIO

# Initialize a single Redis client connection
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def set_display_value(x, y, value):
    key = f'display:{x}:{y}'
    with redis_client.pipeline() as pipeline:
        pipeline.multi()
        pipeline.delete(key)
        pipeline.rpush(key, *value)
        pipeline.execute()

def process_image(source):
    # Determine if source is a URL or a local file path
    if source.startswith('http://') or source.startswith('https://'):
        response = requests.get(source)
        # Check if the request was successful
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
        else:
            raise ValueError("Could not retrieve image from URL.")
    else:
        # Open the image file from a local path
        img = Image.open(source)

    with img as image:
        # Calculate the size to crop the central part of the image
        min_dimension = min(image.size)
        left = (image.width - min_dimension) / 2
        top = (image.height - min_dimension) / 2
        right = (image.width + min_dimension) / 2
        bottom = (image.height + min_dimension) / 2

        # Crop the center of the image
        img_cropped = image.crop((left, top, right, bottom))

        # Resize to 24x24 pixels
        img_resized = img_cropped.resize((24, 24), Image.Resampling.LANCZOS)

        # Process the 24x24 image and write to Redis
        for y in range(24):
            for x in range(24):
                # Get the RGB values of the pixel
                r, g, b = img_resized.getpixel((x, y))
                set_display_value(x, y, (r, g, b))

if __name__ == "__main__":
    # Take the image source from the command line argument
    image_source = sys.argv[1]
    process_image(image_source)
