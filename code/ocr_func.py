import cv2
import pytesseract
import numpy as np
import matplotlib.pyplot as plt # Matplotlib library for plotting
import matplotlib.patches as patches
from sklearn.cluster import DBSCAN
from collections import defaultdict

from translation import translate_text


# TODO: either use or delete
def unskew_image(image):
    """Uses pytesseract to detect the skew of the text in an image
    and return the skew of the original image and a 'corrected' image
    with the skew removed"""

    img_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    # Apply skew correction using Hough transform
    # Find the edges in the image using Canny edge detector
    edges = cv2.Canny(img_gray, 50, 150, apertureSize=3)

    # Find the lines in the image using Hough transform
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 40, None, 0, 0)
    
    # Calculate the mean angle of the lines
    angles = []
    for line in lines:
        rho, theta = line[0]
        angles.append(theta)
    mean_angle = np.mean(angles)
    # Convert the angle from radians to degrees
    mean_angle = mean_angle * 180 / np.pi
    # Create a rotation matrix using the mean angle
    height, width = img_gray.shape
    center = (width/2, height/2)
    rotation_matrix = cv2.getRotationMatrix2D(center, mean_angle, 1)
    # Apply the rotation to the image
    img_rotated = cv2.warpAffine(image, rotation_matrix, (width, height))
    image2 = cv2.rotate(img_rotated, cv2.ROTATE_90_CLOCKWISE)
    print(image.shape)
    print(image2.shape)

    # TODO: Make sure that rotation_matrix is manually multiplied by rotate_90_CLOCKWISE

    plt.figure(figsize=(12,8)) # Create a figure with a larger size
    plt.subplot(1,2,1) # Create a subplot in the first position
    plt.imshow(image) # Display the original image
    plt.title("Original Image") # Add a title
    plt.subplot(1,2,2) # Create a subplot in the second position
    plt.imshow(image2) # Display the corrected image
    plt.title("Skew Correction using Hough Transform") # Add a title
    plt.show()
    # data = pytesseract.image_to_osd(image, config=' -c min_characters_to_try=1', output_type='dict')
    # print(data)
    # angle = float(data.split("\n")[2].split(":")[1].strip())
    # angle = data['rotate'] #or orientation???
    # orientation = data['orientation']
    # (h, w) = image.shape[:2]
    # center = (w // 2, h // 2)
    # # rotation matrix
    # M = cv2.getRotationMatrix2D(center, angle, 1.0)
    # rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    # cv2.imshow('Deskewed Image', rotated)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    #cv2.imwrite('deskewed_image.png', rotated)

    return image2, rotation_matrix




def get_bounding_box(image):
    """Uses pytesseract to get bounding box coordinates for words in an image
    returns: a list of 4-tuples, one for each word, with the 
    top left x and y coords, the width, and the height of the bounding box"""
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
    # TODO: Use the below lines to visually show bounding boxes - messes with translation so don't use for real
            # create a bounding box rectangle to show the text - don't need this
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
    # Show the result
    cv2.imshow('Image with Bounding Boxes', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return return_pts

def get_text(image):
    """Uses pytesseract to get the text of an image"""
    words = pytesseract.image_to_string(image)
    return words


def cluster_boxes(boxes: list):
    """Cluster the text regions based on distance, in order to get discrete
    text boxes to translate more effectively"""
    N = len(boxes)
    dists = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            dists[i, j] = rect_distance(boxes[i], boxes[j])

    # Cluster with DBSCAN
    clustering = DBSCAN(eps=30, min_samples=1, metric='precomputed')
    labels = clustering.fit_predict(dists)
    
    clusters = defaultdict(list)
    for rect, label in zip(boxes, labels):
        clusters[label].append(rect)

    def merge_rects(rect_list):
        xs = [x for x, y, w, h in rect_list]
        ys = [y for x, y, w, h in rect_list]
        xws = [x + w for x, y, w, h in rect_list]
        yhs = [y + h for x, y, w, h in rect_list]
        x_min, y_min = min(xs), min(ys)
        x_max, y_max = max(xws), max(yhs)
        return (x_min, y_min, x_max - x_min, y_max - y_min)

    merged= [merge_rects(rlist) for rlist in clusters.values()]
    return merged

def rect_distance(r1, r2):
    """Calculates distance between boxes"""
    x1, y1, w1, h1 = r1
    x2, y2, w2, h2 = r2

    left = max(x1, x2)
    right = min(x1 + w1, x2 + w2)
    top = max(y1, y2)
    bottom = min(y1 + h1, y2 + h2)

    if right > left and bottom > top:
        return 0  # Overlapping

    dx = max(x2 - (x1 + w1), x1 - (x2 + w2), 0)
    dy = max(y2 - (y1 + h1), y1 - (y2 + h2), 0)
    return (dx**2 + dy**2)**0.5


def image_processing(image_path: str):
    """takes in an image path and returns the bounding boxes of all words in the image,
    as well as the text contained in the image"""
    # Load the image
    image = cv2.imread(image_path)
    # Convert image to RGB (OpenCV loads images in BGR) - Not needed
    # TODO: cut this out if we don't need it
    # rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # unskewed_image, skew_num = unskew_image(image)
    text = get_text(image)
    bounding_pts = get_bounding_box(image)
    # text = get_text(image)
    
    return image, text, bounding_pts#, skew_num


# Plot the clustered boundaries
image, text, bounding_pts = image_processing("code/example_text.jpg")
merged = cluster_boxes(bounding_pts)

fig, ax = plt.subplots()


# Original rectangles in blue
for x, y, w, h in bounding_pts:
    ax.add_patch(patches.Rectangle((x, y), w, h, edgecolor='blue', facecolor='none', linewidth=1, linestyle='--'))

# Merged rectangles in red
for x, y, w, h in merged:
    ax.add_patch(patches.Rectangle((x, y), w, h, edgecolor='red', facecolor='none', linewidth=2))

plt.gca().invert_yaxis()  # Flip Y axis to match typical top-left origin
plt.axis('equal')
plt.title("Blue = Original Rectangles, Red = Merged Clusters")
plt.show()
# image, text, bounding_pts = image_processing("code/skew.png")
# image, text, bounding_pts, skew_num = image_processing("code/PbjyR.png")


print(bounding_pts)
print(text)

print(translate_text(text, "en", "fr"))

