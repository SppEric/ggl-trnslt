import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import textwrap
import matplotlib.pyplot as plt
import cv2 as cv

DEBUGGING = False

def calculate_text_width(text, font_size, font_name="arial.ttf"):
    """
    Calculate the total width needed for text at a given font size.
    
    Args:
        text (str): The text to measure
        font_size (int): The font size to test
        font_name (str): The font file to use
        
    Returns:
        float: The total width needed for the text
        list: List of word lengths
    """
    # Create a temporary image and draw object for measurement
    temp_img = Image.new('RGB', (1, 1))
    temp_draw = ImageDraw.Draw(temp_img)
    font = ImageFont.truetype(font_name, size=font_size)
    space_length = temp_draw.textlength(" ", font=font)
    
    # Calculate total width including spaces
    words = text.split()
    word_lengths = [0 for word in words]
    total_width = 0

    for i, word in enumerate(words):
        word_width = temp_draw.textlength(word, font=font)
        word_lengths[i] = word_width    
        if i < len(words) - 1:  # Add space width if not the last word
            total_width += word_width + space_length
        else:
            total_width += word_width
            
    return total_width, word_lengths

def find_optimal_font_size(text, line_lengths, max_height, font_name="arial.ttf", min_font_size=1):
    """
    Find the largest font size that will fit the text within the given dimensions,
    accounting for potential wasted space from line breaks.
    
    Args:
        text (str): The text to fit
        line_lengths (list): List of available line lengths
        max_height (float): Maximum available height
        font_name (str): The font file to use
        min_font_size (int): Minimum font size to try
        
    Returns:
        int: The optimal font size
        list: List of word lengths at optimal font size
        list: List of booleans indicating which lines need horizontal transformation
        list: List of strings containing the text for each line
    """
    # Start with a large font size and decrease until it fits
    font_size = max_height
    word_lengths = [-1 for word in text.split()]
    
    while font_size > min_font_size:
        width, word_lengths = calculate_text_width(text, font_size, font_name)
        
        # Create a temporary image and draw object for measurement
        temp_img = Image.new('RGB', (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        font = ImageFont.truetype(font_name, size=font_size)
        space_length = temp_draw.textlength(" ", font=font)
        
        # Simulate text layout to check if it fits
        words = text.split()
        current_line = 0
        current_pos = 0
        fits = True
        needs_transform = [False] * len(line_lengths)  # Track which lines need transformation
        line_buckets = [[] for _ in range(len(line_lengths))]  # Store words for each line
        
        for i, word in enumerate(words):
            word_len = word_lengths[i]
            # Add space if not first word on line
            if current_pos > 0:
                word_len += space_length
                
            # If word doesn't fit on current line, try next line
            if current_pos + word_len > line_lengths[current_line]:
                # Calculate wasted space if we move to next line
                wasted_space = line_lengths[current_line] - current_pos
                wasted_percentage = wasted_space / line_lengths[current_line]
                
                # If we'd waste more than 20% of the line, mark for transformation
                if wasted_percentage > 0.2:
                    needs_transform[current_line] = True
                    # Continue on same line with transformation
                    current_pos += word_len
                    line_buckets[current_line].append(word)
                else:
                    # Move to next line
                    current_line += 1
                    current_pos = word_len
                    # If we've run out of lines, text doesn't fit
                    if current_line >= len(line_lengths):
                        fits = False
                        break
                    line_buckets[current_line].append(word)
            else:
                current_pos += word_len
                line_buckets[current_line].append(word)
                
        if fits:
            # Convert word lists to strings
            line_texts = [" ".join(bucket) for bucket in line_buckets]
            return font_size, word_lengths, needs_transform, line_texts
            
        font_size = int(font_size * 0.9)  # Reduce by 10% each time
    
    # If we couldn't find a fitting size, return empty buckets
    return min_font_size, word_lengths, [False] * len(line_lengths), [""] * len(line_lengths)

def project_text_onto_image(image, texts, clusters):
    """
    image: Input image where the text will be projected.
    texts: List of translated texts to be projected onto the image.
    clusters: List of clusters - each cluster is a list of tuples representing the corners of a line
    """
    # Convert the image to a PIL Image object
    pil_image = Image.fromarray(np.uint8(image)).convert('RGBA')

    # Get the pixel data of the image
    pixels = pil_image.load()
    original_pixels = np.asarray(pil_image)

    # Iterate over each cluster and project the text
    for lines, text in zip(clusters, texts):
        num_lines = len(lines)
        all_text = text.split()
        
        # Calculate line lengths
        line_lengths = []
        for line in lines:
            (x1, y1), (x2, y2), _, _ = line
            width = int(np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2))
            line_lengths.append(width)

        # Find the optimal font size for the entire cluster
        max_height = min(int(np.sqrt((x1 - x4) ** 2 + (y1 - y4) ** 2)) for (x1, y1), _, _, (x4, y4) in lines)
        optimal_font_size, word_lengths, needs_transform, buckets = find_optimal_font_size(text, line_lengths, max_height)
        font = ImageFont.truetype(font="arial.ttf", size=optimal_font_size)

        # Now perform steps for each line in lines to display them
        for words, line, should_transform in zip(buckets, lines, needs_transform):
            # Get the coordinates of the rectangle
            (x1, y1), (x2, y2), (x3, y3), (x4, y4) = line
            width = int(np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2))
            height = int(np.sqrt((x1 - x4) ** 2 + (y1 - y4) ** 2))

            # Create temporary image and draw object
            temp_img = Image.new('RGB', (1, 1))
            temp_draw = ImageDraw.Draw(temp_img)


            # Calculate text dimensions
            text_height = optimal_font_size
            text_width = temp_draw.textlength(words, font=font)


            # Calculate vertical margin to center the text
            margin_y = (height - text_height) / 2

            # Get corner colors for background and text color
            corner_colors = [pixels[x1+1, y1+1], pixels[x2-1, y2+1], pixels[x4+1, y4-1], pixels[x3-1, y3-1]]
            avg_r = int(np.average([color[0] for color in corner_colors]))
            avg_g = int(np.average([color[1] for color in corner_colors]))
            avg_b = int(np.average([color[2] for color in corner_colors]))

            brightness = 0.2126 * avg_r + 0.7152 * avg_g + 0.0722 * avg_b
            text_color = (0, 0, 0) if brightness >= 128 else (255, 255, 255)

            # Calculate the angle of rotation
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi

            # If this line needs transformation, apply it
            if should_transform:
                # Create a blank canvas for the text
                line_canvas = Image.new('RGB', (int(math.ceil(text_width)), height), 0)
                line_draw = ImageDraw.Draw(line_canvas)
                # Draw background and text
                line_draw.rectangle([(0, 0), (text_width, height)], fill=(avg_r, avg_g, avg_b))
                line_draw.text((0, margin_y), words, font=font, fill=text_color)

                if DEBUGGING:
                    print("Transforming line")
                    print(text_width)
                    print(width)
                    print(words)
                
                # Calculate the scale factor needed to fit the text
                scale_factor = (text_width) / width
                
                # Create transformation matrix for horizontal scaling
                transform_matrix = [
                    scale_factor, 0, 0, # a, b, c
                    0, 1, 0             # d, e, f
                ]
                
                # Apply the transformation
                line_canvas = line_canvas.transform(
                    (width, height),
                    Image.AFFINE,
                    transform_matrix,
                    fillcolor=(avg_r, avg_g, avg_b),
                    resample=Image.BICUBIC
                )
            else:
                # Create a blank canvas for the text
                line_canvas = Image.new('RGB', (width, height), 0)
                line_draw = ImageDraw.Draw(line_canvas)
                # Draw background and text
                line_draw.rectangle([(0, 0), (width, height)], fill=(avg_r, avg_g, avg_b))
                line_draw.text((0, margin_y), words, font=font, fill=text_color)


            # Rotate the line to match the angle of the rectangle
            line_image = line_canvas.rotate(-1 * angle, fillcolor=(avg_r, avg_g, avg_b))
            
            # Add the line to the image
            Image.Image.paste(pil_image, line_image, (int(x1), int(y1)))

            if DEBUGGING:
                plt.imshow(pil_image)
                plt.show()

    return np.asarray(pil_image)
