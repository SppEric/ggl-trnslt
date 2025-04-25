import numpy as np
from PIL import Image, ImageDraw, ImageFont

def project_text_onto_image(image, texts, rectangles):
    """
    image: Input image where the text will be projected.
    texts: List of translated texts to be projected onto the image.
    rectangles: List of tuples (x1, y1, x2, y2) defining the rectangles for text projection.
    """
    # Convert the image to a PIL Image object
    pil_image = Image.fromarray(np.uint8(image)).convert('RGB')

    # Define a basic font TODO: Customize font to match the original image style
    font = ImageFont.load_default()

    # Iterate over the rectangles and project the text
    for rect, text in zip(rectangles, texts):
        x1, y1, width, height = rect

        # Create a blank canvas for the text
        text_canvas = Image.new('L', (width, height), 0)
        text_draw = ImageDraw.Draw(text_canvas)

        # Assuming a white background for simplicity
        #TODO: Read correct background color from image
        text_draw.text((0, 0), text, font=font, fill=255)

        # Convert the text canvas to a numpy array
        text_array = np.array(text_canvas)

        # Resize the text array to fit the rectangle
        text_array_resized = Image.fromarray(text_array).resize((width, height))
        Image.Image.paste(pil_image, text_array_resized, (x1, y1))

    return np.asarray(pil_image)