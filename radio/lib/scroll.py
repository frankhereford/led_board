import numpy as np
from PIL import Image, ImageDraw, ImageFont

def render_scrolling_text_updated(
    text, width=32, height=32, scroll_speed=1, font_size=24, extra_frames=100
):
    """
    Render scrolling text for a low-resolution display, updated for Pillow 9.5.0.
    The font size is increased to make the text take up more of the display.

    :param text: The text to be displayed.
    :param width: Width of the display in pixels.
    :param height: Height of the display in pixels.
    :param scroll_speed: Number of pixels to shift the text per frame.
    :param font_size: Font size for the text.
    :return: A list of frames, each frame being a 2D array representing the display.
    """

    # Load a larger font
    try:
        #font = ImageFont.truetype("MonaspaceArgon-Bold.otf", font_size)
        font = ImageFont.truetype("DejaVuSerif-Bold.ttf", font_size)
    except IOError:
        print("Default font not found, using load_default() instead.")
        font = ImageFont.load_default()

    # Determine text size using getbbox and create an image wide enough to contain the scrolled text
    bbox = font.getbbox(text)
    text_width, text_height = bbox[2], bbox[3]
    img_width = text_width + width
    img = Image.new("1", (img_width, height), color=0)

    # Create a drawing context
    draw = ImageDraw.Draw(img)

    # Draw the text onto the image
    draw.text((width, ((height - text_height) // 2) - 5), text, font=font, fill=1) # change the subtracted number to scoot up text

    # Scroll the text
    frames = []
    for i in range(0, img_width - width + 1, scroll_speed):
        # Extract the current frame from the image
        frame = img.crop((i, 0, i + width, height))

        for i in range(0, img_width + extra_frames, scroll_speed):
            # Extract the current frame from the image
            frame = img.crop((i, 0, i + width, height))
            frames.append(np.array(frame))

        frame_data = np.array(frame)
        frames.append(frame_data)

    return frames
