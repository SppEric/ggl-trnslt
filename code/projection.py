import numpy as np
from PIL import Image, ImageDraw, ImageFont
import textwrap
import matplotlib.pyplot as plt
import cv2 as cv

def project_text_onto_image(image, texts, clusters):
    """
    image: Input image where the text will be projected.
    texts: List of translated texts to be projected onto the image.
    clusters: List of clusters - each cluster is a list of tuples representing the corners of a line
    """
    # Convert the image to a PIL Image object
    pil_image = Image.fromarray(np.uint8(image)).convert('RGB')

    # Get the pixel data of the image
    pixels = pil_image.load()

    # Iterate over the rectangles and project the text
    for lines, text in zip(clusters, texts):
        num_lines = len(lines)
        remaining_text = text.split(" ")
        # split_text = str.split(text)
        # num_words = len(split_text)
        # words_per_line = num_words // num_lines
        # text_list = [split_text[i:i + words_per_line] for i in range(0, len(split_text), words_per_line)] 
        # # text list is now a list of strings, where each string is the w
        # text_list = [" ".join(words) for words in text_list]
        
        # Now perform steps for each line in lines to display them
        for line in lines:
            # Get the coordinates of the rectangle
            # x1-4 are the coordinates of the four corners of the rectangle clockwise starting from top left
            (x1, y1), (x2, y2), (x3, y3), (x4, y4) = line
            # Calculate the width and height of the rectangle
            width = int(np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2))
            height = int(np.sqrt((x1 - x4) ** 2 + (y1 - y4) ** 2))

            # Now use height for font size 
            # Define a font and its size TODO: Customize font to match the original image style
            font_size = int(np.floor((height - (height/4))))
            font = ImageFont.truetype("arial.ttf", size=font_size)

            # Create a blank canvas for the text
            line_canvas = Image.new('RGB', (width, height), 0)
            line_draw = ImageDraw.Draw(line_canvas)

            # Calculate the length of a space in the font
            space_length = line_draw.textlength(text=" ", font=font)
            
            # calculate how much of the text should go on the line, 
            # taking x amount from the beginning of the string based on the height and width of the box
            # for each word:
            running_width = 0
            displayed_text = ""
            for i, word in enumerate(remaining_text):
                # measure the length of a word + space
                word_length = line_draw.textlength(text=word, font=font) + space_length
                running_width += word_length

                # check if less than remaining space
                if running_width > width:
                    displayed_text = " ".join(remaining_text[:i])
                    remaining_text = remaining_text[i:]
                    break

            #color
            corner_colors = [pixels[x1+1, y1+1], pixels[x2-1, y2+1], pixels[x4+1, y4-1], pixels[x3-1, y3-1]]
            print(corner_colors)
            # Find the average of these colors
            avg_r = int(np.average([color[0] for color in corner_colors]))
            avg_g = int(np.average([color[1] for color in corner_colors]))
            avg_b = int(np.average([color[2] for color in corner_colors]))
            print(avg_r, avg_g, avg_b)

            # draw a background rectangle using this color
            line_draw.rectangle([(0, 0), (width, height)], fill=(avg_r, avg_g, avg_b))

            # Display displayed_text on the line canvas
            line_draw.text((0, 0), displayed_text, font=font, fill=255) # TODO: Add color to text, change location of text

            # Convert the new line canvas to a numpy array
            line_array = np.array(line_canvas)
            
            # Rotate the line array to match the angle of the rectangle
            # Calculate the angle of rotation
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
            
            # Rotate the line array
            line_array = cv.warpAffine(line_array, cv.getRotationMatrix2D((width // 2, height // 2), angle, 1), (width, height))
            
            # Convert the rotated line array back to a PIL Image in integer values
            line_image = Image.fromarray(line_array)

            # Add the line to the image
            Image.Image.paste(pil_image, line_image, (int(x1), int(y1)))

            





    # for pair, text in zip(rectangles, texts):
    #     rect, lines = pair
    #     x1, y1, width, height = rect

    #     # Create a blank canvas for the text
    #     text_canvas = Image.new('RGB', (width, height), 0)
    #     text_draw = ImageDraw.Draw(text_canvas)

    #     # TODO: Should probably not be needed, now that we aren't running in paragraph=True
    #     # Width should be max number of characters we want
    #     # To find max number of characters we can fit its = rect width / font_size width
    #     # Define a font and its size TODO: Customize font to match the original image style
       
    #     font_size = int(np.floor((height / lines)))
    #     print(font_size)
    #     print(width)
    #     font = ImageFont.truetype("arial.ttf", size=font_size)
    #     lines = textwrap.wrap(text, width=int(width//))
    #     lines = '\n'.join(lines)
    #     print(lines)

    #     # Get the x and y coordinates of the top left corner of the box
    #     x, y, w, h = rect
    #     # Get the RGB values at the corners of the box - one pixel in
    #     corner_colors = [pixels[x+1, y+1], pixels[x+w-1, y+1], pixels[x+1, y+h-1], pixels[x+w-1, y+h-1]]
    #     print(corner_colors)
    #     # Find the average of these colors
    #     avg_r = int(np.average([color[0] for color in corner_colors]))
    #     avg_g = int(np.average([color[1] for color in corner_colors]))
    #     avg_b = int(np.average([color[2] for color in corner_colors]))
    #     print(avg_r, avg_g, avg_b)

    #     # draw a background rectangle using this color
    #     text_draw.rectangle([(0, 0), (w, h)], fill=(avg_r, avg_g, avg_b))
    #     text_draw.multiline_text((0, 0), lines, font=font, fill=0)

    #     # Convert the text canvas to a numpy array
    #     text_array = np.array(text_canvas)

    #     ## Calculate transformation matrix for rotation and scaling
    #     # Find corners in the original image to map to the corners of the text canvas
    #     #dst = cv.cornerHarris(gray,2,3,0.04)

    #     # Resize the text array to fit the rectangltext_draw.textlength(text[0], font=font)e
    #     #text_array_resized = Image.fromarray(text_array).resize((width, height))
    #     Image.Image.paste(pil_image, Image.fromarray(text_array), (x1, y1))

    return np.asarray(pil_image)
