import cv2
import easyocr
import matplotlib.pyplot as plt # Matplotlib library for plotting
import matplotlib.patches as patches
from sklearn.cluster import DBSCAN
from collections import defaultdict
from shapely.geometry import Polygon

import numpy as np

# Variable to generate graphs of the bounding boxes for debugging
DEBUGGING = True
######## HELPER FUNCTIONS ########
## Unskew Image
# def unskew_image(image):
#     """Uses cv2 to detect the skew of the text in an image
#     and return the skew of the original image and a 'corrected' image
#     with the skew removed"""

#     img_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
#     # Apply skew correction using Hough transform
#     # Find the edges in the image using Canny edge detector
#     edges = cv2.Canny(img_gray, 50, 150, apertureSize=3)


#     # ### Non Probabilitic Hough Transform ###
#     # # Find the lines in the image using Hough transform
#     # lines = cv2.HoughLines(edges, 1, np.pi / 180, 40, None, 50, 10)

#     #     # Calculate the mean angle of the lines
#     # angles = []
#     # if lines is None:
#     #     print("No lines found")
#     #     return image, None
#     # else:
#     #     for line in lines:
#     #         rho, theta = line[0]
#     #         angles.append(theta)
#     # # # Filter angles that are very vertical and horizontal
#     # # filtered_angles = [
#     # #     theta for line in lines for rho, theta in [line[0]]
#     # #     if np.deg2rad(20) < theta < np.deg2rad(160)  # Exclude near-vertical (around 0 and 180 deg)
#     # # ]

#     # mean_angle = np.mean(angles)
#     # # Convert the angle from radians to degrees
#     # mean_angle = mean_angle * 180 / np.pi
#     # # Create a rotation matrix using the mean angle
#     # height, width = img_gray.shape
#     # center = (width/2, height/2)
#     # rotation_matrix = cv2.getRotationMatrix2D(center, mean_angle, 1)

#     ### Probabilistic Hough Transform ###
#     # Find the lines in the image using probabilistic Hough transform
#     # linesP is a list of lines in the form of (x_start, y_start, x_end, y_end)
#     linesP = cv2.HoughLinesP(edges, 1, np.pi / 180, 50, None, 50, 10)

#     # Do same computation but with linesP
#     # Calculate the mean angle of the lines
#     anglesP = []
#     if linesP is None:
#         print("No lines found")
#         return image, None
#     else:
#         for line in linesP:
#             x1, y1, x2, y2 = line[0]
#             angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
#             anglesP.append(angle)
#     mean_angleP = np.median(anglesP)

#     ## Convert the angle from radians to degrees
#     #mean_angleP = mean_angleP * 180 / np.pi
    
#     # Create a rotation matrix using the mean angle
#     height, width = img_gray.shape
#     center = (width/2, height/2)
#     rotation_matrix = cv2.getRotationMatrix2D(center, mean_angleP, 1)

    
#     ## Apply the rotation to the image
#     # Calculate bounding box size after rotation
#     cos = np.abs(rotation_matrix[0, 0])
#     sin = np.abs(rotation_matrix[0, 1])
#     new_w = int((height * sin) + (width * cos))
#     new_h = int((height * cos) + (width * sin))

#     # Adjust the rotation matrix to account for the translation
#     rotation_matrix[0, 2] += (new_w / 2) - center[0]
#     rotation_matrix[1, 2] += (new_h / 2) - center[1]

#     # Rotate with the new bounding box
#     img_rotated = cv2.warpAffine(image, rotation_matrix, (new_w, new_h), borderMode=cv2.BORDER_REPLICATE)
#     #image2 = cv2.rotate(img_rotated, cv2.ROTATE_90_CLOCKWISE)
#     image2 = img_rotated

#     # Debugging for lines
#     #print(lines.shape)
#     print(linesP.shape)
#     for i in range(0, len(linesP)):
#         l = linesP[i][0]

#         # Convert the image to BGR format for OpenCV
#         image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

#         # Draw the lines on the image
#         cv2.line(image, (l[0], l[1]), (l[2], l[3]), (0,0,255), 3, cv2.LINE_AA)

#     ## Graphing the results
#     plt.figure(figsize=(12,8)) # Create a figure with a larger size
#     plt.subplot(1,2,1) # Create a subplot in the first position
#     plt.imshow(image) # Display the original image
#     # Add found hough lines to the image
#     plt.title("Original Image") # Add a title
#     plt.subplot(1,2,2) # Create a subplot in the second position
#     plt.imshow(image2) # Display the corrected image
#     plt.title("Skew Correction using Hough Transform") # Add a title
#     plt.show()
#     return image2, rotation_matrix

########## EasyOCR Functions ##########
def easy_ocr_function(image: str, from_lang: str):
    """
    Uses EasyOCR to get the bounding boxes and text from an image
    The bounding box coordinates are in the format (top-left, top-right, bottom-right, bottom-left)
    The text is the second to last element of each tuple
    The confidence score is the last element of each tuple
    """
    # TODO: Create dictioniary to map standardized language codes to EasyOCR language codes
    reader = easyocr.Reader(
        [from_lang], 
        # GPU stuff
        gpu=True
    ) 

    # Read the image and get the bounding boxes
    bounding_boxes = reader.detect(
            image,
            mag_ratio=1.5, # Increase the size of the image to improve accuracy
            # Bounding box parameters 
            width_ths=1, # Maximum horizontal distance to merge boxes - made a little wider )
    )
    # Calculate average text orientation from bounding boxes
    angles = []
    for points in bounding_boxes[1][0]: # bounding_boxes[1] is the list of free form bounding boxes
        print(points)
        top_left, top_right, _, _ = points
        angle = np.arctan2(top_right[1] - top_left[1], top_right[0] - top_left[0]) * 180 / np.pi
        angles.append(angle)
    
    mean_angle = np.median(angles) if angles else 0
    
    rotation_matrix = None
    # Create rotation matrix and apply rotation if skew detected
    if abs(mean_angle) > 0.2:  # Only correct if angle is significant
        print("Rotation matrix necessary!")
        height, width = image.shape[:2]
        center = (width/2, height/2)
        rotation_matrix = cv2.getRotationMatrix2D(center, mean_angle, 1)
        
        # Calculate new image dimensions
        cos = np.abs(rotation_matrix[0, 0])
        sin = np.abs(rotation_matrix[0, 1])
        new_w = int((height * sin) + (width * cos))
        new_h = int((height * cos) + (width * sin))
        
        # Adjust rotation matrix
        rotation_matrix[0, 2] += (new_w / 2) - center[0]
        rotation_matrix[1, 2] += (new_h / 2) - center[1]
        
        # Apply rotation
        image = cv2.warpAffine(image, rotation_matrix, (new_w, new_h), borderMode=cv2.BORDER_REPLICATE)

        # # Display the corrected image
        # plt.imshow(image)
        # plt.title("Skew Correction using Average of Free Form Bounding Boxes")
        # plt.show()
        
        # Re-run OCR for actual text-reading on corrected image
        result = reader.readtext(
            image, 
            # General parameters
            detail=1, 
            batch_size=8,
            # Detection parameters
            paragraph=False, 
            rotation_info=[0, 90, 180, 270], 
            decoder="wordbeamsearch",
            mag_ratio=1.5, # Increase the size of the image to improve accuracy
            # Bounding box parameters 
            width_ths=1, # Maximum horizontal distance to merge boxes - made a little wider
        )
    else:
        print("No rotation matrix necessary!")
 
    # Extract bounding boxes and text
    bounding_pts = []
    text_list = []
    for found_text in result:
        points = found_text[0]
        text = found_text[1]

        top_left, top_right, bottom_right, bottom_left = points[0], points[1], points[2], points[3]
        if DEBUGGING:
            print(f"Bounding box: {points}")
            print(f"Text: {text}")
            
        bounding_pts.append((top_left, top_right, bottom_right, bottom_left))
        text_list.append(text)
    
    return bounding_pts, text_list, image, rotation_matrix

def cluster_boxes(boxes: list, text_list: list):
    """Cluster the text regions based on distance, in order to get discrete
    text boxes to translate more effectively"""
    N = len(boxes)
    dists = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            dists[i, j] = rect_distance(boxes[i], boxes[j])

    # Cluster with DBSCAN
    clustering = DBSCAN(eps=50, min_samples=1, metric='precomputed')
    clustering = DBSCAN(eps=30, min_samples=1, metric='precomputed')
    labels = clustering.fit_predict(dists)

    clusters = defaultdict(list)
    clusters_words = defaultdict(list)
    for rect, label, words in zip(boxes, labels, text_list):
    
        clusters[label].append(rect)
        clusters_words[label].append(words)

    # def merge_rects(rect_list):
    #     xs = [x for x, y, w, h in rect_list]
    #     ys = [y for x, y, w, h in rect_list]
    #     xws = [x + w for x, y, w, h in rect_list]
    #     yhs = [y + h for x, y, w, h in rect_list]
    #     x_min, y_min = min(xs), min(ys)
    #     x_max, y_max = max(xws), max(yhs)
    #     # together = " ".join(words_list)
    #     return (int(x_min), int(y_min), int(x_max - x_min), int(y_max - y_min))
    
    # merged_rects = [(merge_rects(rlist), len(rlist)) for rlist in clusters.values()]
    merged_text = [" ".join(word_list) for word_list in clusters_words.values()]
    #list of lists of rectangle coordinates, so its a big list and each list within it is one cluster
    #in other words a list of what rectangles go in each cluster.
    # the second return is a list of strings associated with each cluster
    # so index 0 in clusters.values() refers to the same area as the string in index 0 of merged text
    return clusters.values(), merged_text
   

#this calculates the distance between boxes
def rect_distance(p1, p2):
    """Calculates distance between two non-axis-aligned rectangles.
    Each p is a list of 4 (x, y) tuples: [top_left, top_right, bottom_right, bottom_left]
    """

    poly1 = Polygon(p1)
    poly2 = Polygon(p2)

    if poly1.intersects(poly2):
        return 0  # They overlap

    return poly1.distance(poly2)

########## MAIN RETURNED FUNCTION ##########
def image_processing(image: np.ndarray, from_lang: str):
    """takes in an image path and returns the bounding boxes of all words in the image,
    as well as the text contained in the image"""


    ## Perform image processing to remove noise, skew, etc.
    # unskewed_image, skew_num = unskew_image(image)
    
    ## Code for using EasyOCR
    # EasyOCR has a different format for the bounding boxes and text 
    # We get the boudning boxes and text from one call to the reader
    # Bounding_pts is a list of tuples, where each tuple is (top-left, top-right, bottom-right, bottom-left)
    # Each tuple is a list of 4 points, where each point is a tuple of (x, y) coordinates
    bounding_pts, text_list, image, rotation_matrix = easy_ocr_function(image, from_lang)

    # TODO: See if clustering is needed for EasyOCR - it may be able to do it on its own
    cluster_rectangles, clustered_text_list = cluster_boxes(bounding_pts, text_list)

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

        print(clustered_text_list)

        plt.axis('equal')
        plt.title("Blue = Original Rectangles, Red = Merged Clusters")
        plt.show()

    # return a list of clusters, a list of strings, and the image
    return cluster_rectangles, clustered_text_list, image, rotation_matrix
