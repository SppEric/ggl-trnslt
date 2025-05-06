import cv2
import easyocr
import matplotlib.pyplot as plt # Matplotlib library for plotting
import matplotlib.patches as patches



# Variable to generate graphs of the bounding boxes for debugging
DEBUGGING = True

########## EasyOCR Functions ##########
def easy_ocr_function(image: str, from_lang: str):
    """
    Uses EasyOCR to get the bounding boxes and text from an image
    The bounding box coordinates are in the format (top-left, top-right, bottom-right, bottom-left)
    The text is the second to last element of each tuple
    The confidence score is the last element of each tuple
    """
    # TODO: Create dictioniary to map standardized language codes to EasyOCR language codes
    reader = easyocr.Reader([from_lang], gpu=True) # Can specify whether to use GPU or not
    # Read the image and get the bounding boxes and text
    result = reader.readtext(image, detail=1, paragraph=False, rotation_info=[0, 90, 180, 270], decoder="wordbeamsearch")
 
    # We want to return the bounding boxes and the text, so we will extract those
    bounding_pts = []
    text_list = []
    for found_text in result:
        points = found_text[0]
        text = found_text[1]

        top_left, top_right, bottom_right, bottom_left  = points[0], points[1], points[2], points[3]
        if DEBUGGING:
            print(f"Bounding box: {points}")
            print(f"Text: {text}")
            
        # If we change to only using easyOCR, we can adjust out clustering function to use this format
        # bounding_pts.append((top_left[0], top_left[1], bottom_right[0] - top_left[0], bottom_right[1] - top_left[1]))
        bounding_pts.append((top_left, top_right, bottom_right, bottom_left))
        text_list.append(text)
    
    return bounding_pts, text_list

########## Perform Image Processing ##########
def image_processing(image_path: str, from_lang: str):
    """takes in an image path and returns the bounding boxes of all words in the image,
    as well as the text contained in the image"""
    # Load the image
    image = cv2.imread(image_path)
    image = image[...,::-1]


    ## Perform image processing to remove noise, skew, etc.
    # unskewed_image, skew_num = unskew_image(image)
    # text = get_text(image)

    ## Perform OCR on the image using pytesseract or EasyOCR
    bounding_pts = []
    cluster_rectangles = []
    text_list = []

    ## Code for using EasyOCR
    # EasyOCR has a different format for the bounding boxes and text 
    # We get the boudning boxes and text from one call to the reader
    # Bounding_pts is a list of tuples, where each tuple is (top-left, top-right, bottom-right, bottom-left)
    # Each tuple is a list of 4 points, where each point is a tuple of (x, y) coordinates
    bounding_pts, text_list = easy_ocr_function(image, from_lang)

    # TODO: See if clustering is needed for EasyOCR - it may be able to do it on its own
    cluster_rectangles = bounding_pts

    if DEBUGGING:
        fig, ax = plt.subplots()
        ax.imshow(image)

        # Original rectangles in blue
        for top_left, top_right, bottom_right, bottom_left in bounding_pts:
            print(top_left, top_right, bottom_right, bottom_left)
            # Draw the points in blue on top of the original image
            ax.plot([top_left[0], top_right[0], bottom_right[0], bottom_left[0], top_left[0]], 
                    [top_left[1], top_right[1], bottom_right[1], bottom_left[1], top_left[1]], 'bo-')
            

            # w = bottom_right[0] - top_left[0]   
            # h = bottom_right[1] - top_left[1]
            # ax.add_patch(patches.Rectangle((top_left[0], top_left[1]), w, h, edgecolor='blue', facecolor='none', linewidth=1, linestyle='--'))

        plt.axis('equal')
        plt.title("Blue = Original Rectangles, Red = Merged Clusters")
        plt.show()

    # return a list of clusters, a list of strings, and the image
    return cluster_rectangles, text_list, image
