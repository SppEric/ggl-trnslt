from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import os
from main import process_image

app = Flask(__name__)
UPLOAD_FOLDER = 'images'
PROCESSED_FOLDER = os.path.join('outputs', 'images')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)


@app.route('/')
def upload_form():
    return render_template('upload.html', processed_image=None)


@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return 'No file part'
    
    file = request.files['image']
    if file.filename == '':
        return 'No selected file'
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    from_lang = request.form.get('from_lang')
    to_lang = request.form.get('to_lang')

    # You can now access the file at `filepath`
    print(f"Image saved at: {filepath}")

    altered_path = process_image(filepath, from_lang, to_lang)
    processed_filename = os.path.basename(altered_path)
    return render_template('upload.html', processed_image=processed_filename)


@app.route('/outputs/images/<filename>')
def get_processed_image(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)


if __name__ == '__main__':
    app.run(debug=True)
