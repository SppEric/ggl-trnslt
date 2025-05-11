import argparse
import os
import cv2
import pytesseract
from ocr_func import image_processing
from translation import translate_text
from projection import project_text_onto_image
import matplotlib.pyplot as plt
from PIL import Image

DEBUGGING = True

def parse_arguments():
    parser = argparse.ArgumentParser(description="Specify which image in the images folder to read.")

    parser.add_argument(
        '--image_path',
        type=str,
        required=True,
        help="Name of the image file in the 'images' folder to translate."
    )
    parser.add_argument(
        '--from_lang',
        '-f',
        type=str,
        required=True,
        help="Language of the text that will be in the image to be translated."
    )
    parser.add_argument(
        '--to_lang',
        '-t',
        type=str,
        required=True,
        help="Language of the text that will be projected onto the image."
    )

    args = parser.parse_args()

    # Check if the specified image exists in the images folder
    image_path = os.path.join('images', args.image_path)
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"The specified image '{args.image_path}' does not exist in the 'images' folder.")
    
    return image_path, args.from_lang, args.to_lang

def process_image(image_path, from_lang, to_lang):
    if DEBUGGING:
        print(f"Image to read: {image_path}")
    # Load the image
    original_image = cv2.imread(image_path)
    original_image = original_image[...,::-1]

    # Call code to process the image to get the text, bounding boxes, and fixed image (if adjusting for skew)
    cluster_rectangles, texts, image, rotation_matrix = image_processing(original_image, from_lang)
    translated_texts = []
    for text in texts:
        # Code to translate the text using the translation API
        translation = translate_text(text, from_lang, to_lang)
        translated_texts.append(translation)

    if DEBUGGING:
        print(f"Original text: {texts}")
        print(f"Translated text: {translated_texts}")

    # Code to project text back onto the image
    altered_image = project_text_onto_image(image, translated_texts, cluster_rectangles)

    # Apply inverse of the rotation matrix to the image to recorrect for skew
    if rotation_matrix is not None:
        # Get original dimensions before any rotation was applied
        orig_h, orig_w = original_image.shape[:2]
        
        # Calculate inverse rotation matrix
        rotation_matrix_inv = cv2.invertAffineTransform(rotation_matrix)
        
        # Warp back using original dimensions
        altered_image = cv2.warpAffine(altered_image, rotation_matrix_inv, (orig_w, orig_h), 
                                     flags=cv2.INTER_LINEAR,
                                     borderMode=cv2.BORDER_CONSTANT,
                                     borderValue=(255,255,255))

    output_filepath = os.path.join('outputs', image_path)
    # altered_image is RGBA, so we drop the alpha channel when saving
    img = Image.fromarray(altered_image[...,:3].astype('uint8'), 'RGB') 
    
    img.save(output_filepath)

    if DEBUGGING:
        plt.imshow(altered_image)
        plt.title(f"Final Result: {output_filepath}")
        plt.show()

    return output_filepath

if __name__ == "__main__":
    image_path, from_lang, to_lang = parse_arguments()
    process_image(image_path, from_lang, to_lang)
    