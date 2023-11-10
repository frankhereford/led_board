import redis
from PIL import Image, ImageEnhance
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

def darken_image(image, darken_factor):
    # Apply an enhancement filter to darken the image
    enhancer = ImageEnhance.Brightness(image)
    return enhancer.enhance(darken_factor)

def process_image(source, darken_factor=1.0):
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
        # Darken the image
        image_darkened = darken_image(image, darken_factor)

        # Calculate the size to crop the central part of the image
        min_dimension = min(image_darkened.size)
        left = (image_darkened.width - min_dimension) / 2
        top = (image_darkened.height - min_dimension) / 2
        right = (image_darkened.width + min_dimension) / 2
        bottom = (image_darkened.height + min_dimension) / 2

        # Crop the center of the image
        img_cropped = image_darkened.crop((left, top, right, bottom))

        # Resize to 24x24 pixels
        img_resized = img_cropped.resize((24, 24), Image.Resampling.LANCZOS)

        # Process the 24x24 image and write to Redis
        for y in range(24):
            for x in range(24):
                # Get the RGB values of the pixel
                #r, g, b = img_resized.getpixel((x, y))
                threshold = 10  # Define the threshold for "almost black"
                r, g, b = img_resized.getpixel((x, y))
                if r < threshold and g < threshold and b < threshold:
                    r, g, b = 0, 0, 0  # Set the pixel to black
                set_display_value(x, y, (r, g, b))

if __name__ == "__main__":
    # Take the image source and darken factor from the command line arguments
    image_source = sys.argv[1]
    darken_factor = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    process_image(image_source, darken_factor)
