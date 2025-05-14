# ggl-trnslt

## For environment
Packages to pip install
- translate
- opencv-python
- easyocr
- scikit-learn


## Running the Code

There are two ways to run the code. The first way is running the code directly from the terminal. When doing this, make sure to set the DEBUGGING flag to True on all files, to ensure that the output images are shown. This shows a more intermediate product of the project. To run via the terminal, use the command

```
python main.py --image_path --from_lang --to_lang
```
from the code directory.

The second way, which demonastrates the full finished product of the project, involves a locally-hosted website which can be launched using the terminal command 
```
python app.py
```
from the code directory. This will launch a Flask app with a UI to submit images and see the results.

Additionally, we have setup a pipeline to download images locally so that they can be given to the model in `form.py`. This requires setting up a Google Drive folder for the images to be put in and Google authetication for that account.

### Note
As is, this code cannot be run on Apple computers. The fontbook for Apple and Windows computers is different, and so the code will error for Mac users due to the incompatible font.
