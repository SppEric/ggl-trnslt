# ggl-trnslt

## For environment
Packages to pip install
- translate
- opencv-python
- pytesseract
- scikit-learn


## TODO:
- Address Skew Issues

Do the OCR Library Call to detect amount of rotation required to fix image, and save it

    1 -  figure out if image is skewed
        a - if it is, unskew the image
    2 - continue the process as normal
    3 - use the inital rotation/skew

- Figure out how to approach matching text in boxes

Taking safe estimate of what the box is for now


## Approach:

### 1 - OCR:
`function image_processing():` 
`inputs:` Takes in an image path (TODO: Modify so can be from live video?)  

#### Steps:
Read in image  
Detect and fix visual anomalies (e.g. skew)  
Get bounding boxes for text (initially around each word)  
Get text itself  

`returns:` the image, the text, the skew, and the bounding boxes


### 2 - Translation:
`function translate_text():`  
`inputs:` text, from_language, to_language 

#### Steps:
Translate text, assuming it's in from_language and output in to_language  

`returns:` translated text

### 3 - Projection:
`function project_text()`  
`inputs:` image, translated text, skew, bounding boxes  

#### Steps:
- Remove text by filling in bounding boxes with the detected background color of each bounding box  
- Calculate the overall bounding box our text will live in  
- Put text back in (elaborate)
- Reskew the image to be like the original

`returns:` image with projected text! YAYAYAY





LINKS:

Preprocessing image and skew:
https://stackoverflow.com/questions/57964634/python-opencv-skew-correction-for-ocr
https://pyimagesearch.com/2022/01/31/correcting-text-orientation-with-tesseract-and-python/
https://pyimagesearch.com/2017/02/20/text-skew-correction-opencv-python/
https://gpttutorpro.com/ocr-integration-for-nlp-applications-preprocessing-images-for-ocr/

Putting text on image:
https://www.geeksforgeeks.org/adding-text-on-image-using-python-pil/

cv.inpaint for filling in/removing the text
