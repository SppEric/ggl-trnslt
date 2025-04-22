import cv2
import pytesseract

from translation import translate_text

def get_bounding_box(image):
    # Use pytesseract to get bounding box and text data
    boxes = pytesseract.image_to_data(image)

    return_pts = []
    # For each bounding box
    for i, line in enumerate(boxes.splitlines()):
        # skip header
        if i == 0:
            continue
        # each bounding box contains 12 pieces of information
        parts = line.split()
        # check to make sure the format has all fields
        if len(parts) == 12:
            # get the top left x and y, and the width and height
            x, y, w, h = int(parts[6]), int(parts[7]), int(parts[8]), int(parts[9])
            return_pts.append((x, y, w, h))
            # create a bounding box rectangle to show the text - don't need this
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    # Show the result
    cv2.imshow('Image with Bounding Boxes', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return return_pts

def get_text(image):
    words = pytesseract.image_to_string(image)
    return words

def image_processing(image_path: str):
    # Load the image
    image = cv2.imread(image_path)
    # Convert image to RGB (OpenCV loads images in BGR)
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    bounding_pts = get_bounding_box(rgb_image)
    text = get_text(image)

    return image, text, bounding_pts

image, text, bounding_pts = image_processing("code/example_text.jpg")
print(bounding_pts)
print(text)

print(translate_text(text, "en", "fr"))

