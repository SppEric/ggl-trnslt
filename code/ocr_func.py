import cv2
import easyocr
import matplotlib.pyplot as plt # Matplotlib library for plotting
import matplotlib.patches as patches
from sklearn.cluster import DBSCAN
from collections import defaultdict
from shapely.geometry import Polygon

import numpy as np

# Variable to generate graphs of the bounding boxes for debugging
DEBUGGING = False

########## EasyOCR Functions ##########
def easy_ocr_function(image: str, from_lang: str):
    """
    Uses EasyOCR to get the bounding boxes and text from an image
    The bounding box coordinates are in the format (top-left, top-right, bottom-right, bottom-left)
    The text is the second to last element of each tuple
    The confidence score is the last element of each tuple
    """
    # TODO: Create dictioniary to map standardized language codes to EasyOCR language codes
    if from_lang == "zh":
        from_lang = "ch_sim"
    
    reader = easyocr.Reader(
        [from_lang], 
        # GPU stuff
        gpu=True
    ) 

    # Read the image and get the bounding boxes
    bounding_boxes = reader.detect(
            image,
            mag_ratio=1.75, # Increase the size of the image to improve accuracy
            # Bounding box parameters 
            width_ths=2, # Maximum horizontal distance to merge boxes - made a little wider)
    )


    if DEBUGGING:
        fig, ax = plt.subplots()
        ax.imshow(image)

        # Display free form bounding boxes
        for top_left, top_right, bottom_right, bottom_left in bounding_boxes[1][0]:
            # Draw the points in blue on top of the original image
            ax.plot([top_left[0], top_right[0], bottom_right[0], bottom_left[0], top_left[0]], 
                    [top_left[1], top_right[1], bottom_right[1], bottom_left[1], top_left[1]], 'bo-')
            
        # Display rectangle bounding boxes
        for x_min, x_max, y_min, y_max in bounding_boxes[0][0]:
            # Draw the points in red on top of the original image
            ax.plot([x_min, x_max, x_max, x_min, x_min], [y_min, y_min, y_max, y_max, y_min], 'ro-')

        plt.axis('equal')
        plt.title("Blue = Free Form Bounding Boxes, Red = Rectangle Bounding Boxes")
        plt.show()


    # Count whether there is a large amount of straight text or text that is rotated
    straight_text_count = len(bounding_boxes[0][0])
    rotated_text_count = len(bounding_boxes[1][0])

    rotation_matrix = None
    if straight_text_count < rotated_text_count: # This is naive, potentially will not work
        # Calculate average text orientation from bounding boxes
        angles = []
        for points in bounding_boxes[1][0]: # bounding_boxes[1] is the list of free form bounding boxes
            print(points)
            top_left, top_right, _, _ = points
            angle = np.arctan2(top_right[1] - top_left[1], top_right[0] - top_left[0]) * 180 / np.pi
            angles.append(angle)
        
        mean_angle = np.mean(angles) if angles else 0
        print(angles)
        
        
        # Create rotation matrix and apply rotation if skew detected
        if abs(mean_angle) > 0.1:  # Only correct if angle is significant
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

            # Display the corrected image
            plt.imshow(image)
            plt.title("Skew Correction using Average of Free Form Bounding Boxes")
            plt.show()
        else:
            print("No rotation matrix necessary!")
    
    # Re-run OCR for actual text-reading on corrected image
    result = reader.readtext(
        image, 
        # General parameters
        detail=1, 
        batch_size=8,
        # Detection parameters
        paragraph=False, 
        rotation_info=[0], 
        decoder="wordbeamsearch",
        mag_ratio=1.75, # Increase the size of the image to improve accuracy
        # Bounding box parameters 
        width_ths=2, # Maximum horizontal distance to merge boxes - made a little wider,
    )
 
    # Extract bounding boxes and text
    bounding_pts = []
    text_list = []
    
    # First pass: collect all rectangular boxes
    rect_boxes = []
    for found_text in result:
        points = found_text[0]
        # Check if this is a rectangular box (all coordinates are integers)
        if all(isinstance(coord, int) for point in points for coord in point):
            rect_boxes.append(points)
    
    # Second pass: add boxes that don't overlap with rectangular boxes
    for found_text in result:
        points = found_text[0]
        text = found_text[1]
        
        # Check if this is a free-form box (has float coordinates)
        is_free_form = any(isinstance(coord, float) for point in points for coord in point)
        
        if is_free_form:
            # Check for overlap with any rectangular box
            overlaps = False
            for rect_box in rect_boxes:
                if rect_distance(points, rect_box) == 0:  # 0 means overlap
                    overlaps = True
                    print(f"Overlap detected between {text} and {rect_box}")
                    break
                    
            if not overlaps:
                top_left, top_right, bottom_right, bottom_left = points[0], points[1], points[2], points[3]
                bounding_pts.append((top_left, top_right, bottom_right, bottom_left))
                text_list.append(text)
        else:
            # Always add rectangular boxes
            top_left, top_right, bottom_right, bottom_left = points[0], points[1], points[2], points[3]
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
    clustering = DBSCAN(eps=10, min_samples=1, metric='precomputed')
    labels = clustering.fit_predict(dists)

    clusters = defaultdict(list)
    clusters_words = defaultdict(list)
    for rect, label, words in zip(boxes, labels, text_list):
    
        clusters[label].append(rect)
        clusters_words[label].append(words)
    
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
            # Draw the points in blue on top of the original image
            ax.plot([top_left[0], top_right[0], bottom_right[0], bottom_left[0], top_left[0]], 
                    [top_left[1], top_right[1], bottom_right[1], bottom_left[1], top_left[1]], 'bo-')
            
        print(clustered_text_list)

        plt.axis('equal')
        plt.title("Clustered Text")
        plt.show()

    # return a list of clusters, a list of strings, and the image
    return cluster_rectangles, clustered_text_list, image, rotation_matrix
