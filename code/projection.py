import numpy as np
from PIL import Image, ImageDraw, ImageFont
import textwrap
import matplotlib.pyplot as plt

def project_text_onto_image(image, texts, rectangles):
    """
    image: Input image where the text will be projected.
    texts: List of translated texts to be projected onto the image.
    rectangles: List of tuples (x1, y1, x2, y2) defining the rectangles for text projection.
    """
    # Convert the image to a PIL Image object
    pil_image = Image.fromarray(np.uint8(image)).convert('RGB')

    # Get the pixel data of the image
    pixels = pil_image.load()

    # Iterate over the rectangles and project the text
    for rect, text in zip(rectangles, texts):
        x1, y1, width, height = rect

        # Create a blank canvas for the text
        text_canvas = Image.new('L', (width, height), 0)
        text_draw = ImageDraw.Draw(text_canvas)

        # TODO: Should probably not be needed, now that we aren't running in paragraph=True
        # Width should be max number of characters we want
        # To find max number of characters we can fit its = rect width / font_size width
        # Define a font and its size TODO: Customize font to match the original image style
        font_size = height // 1.
        font = ImageFont.truetype("arial.ttf", size=font_size)
        lines = textwrap.wrap(text, width=width//text_draw.textlength(text[0], font=font))
        lines = '\n'.join(lines)
        print(lines)

        # Assuming a white background for simplicity
        #TODO: Read correct background color from image
        # Get the x and y coordinates of the top left corner of the box
        x, y, w, h = rect
        # Get the RGB values at the corners of the box
        corner_colors = (pixels[x, y], pixels[x+w, y], pixels[x, y+h], pixels[x+w, y+h])
        # Find the average of these colors
        avg_r = int(np.average([color[0] for color in corner_colors]))
        avg_g = int(np.average([color[1] for color in corner_colors]))
        avg_b = int(np.average([color[2] for color in corner_colors]))
        hex_avg_color = '#{:02X}{:02X}{:02X}'.format(avg_r, avg_g, avg_b)

        # Color of the top left corner
        # TODO: delete if not using this
        # r, g, b = pixels[x, y]
        # rgb_color = (r, g, b)
        # hex_color = '#{:02X}{:02X}{:02X}'.format(r, g, b)
        # draw a background rectangle using this color

        # text_size = text_draw.textbbox(x,y, text, font=font)
        text_draw.rectangle([(0, 0), (w, h)], fill=hex_avg_color)
        text_draw.multiline_text((0, 0), lines, font=font, fill=0, align='center')

        # Convert the text canvas to a numpy array
        text_array = np.array(text_canvas)

        # Resize the text array to fit the rectangle
        #text_array_resized = Image.fromarray(text_array).resize((width, height))
        Image.Image.paste(pil_image, Image.fromarray(text_array), (x1, y1))

    return np.asarray(pil_image)
