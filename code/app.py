from flask import Flask, request, render_template, redirect, url_for, send_from_directory, flash
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
    print(f"request.files: {request.files}")
    print(f"request.form: {request.form}")

    if 'image' not in request.files:
        flash('No file part. Please try again.')
        return redirect(url_for('upload_form'))

    file = request.files['image']
    if file.filename == '':
        flash('No selected file. Please choose an image.')
        return redirect(url_for('upload_form'))

    filename = file.filename
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    from_lang = request.form.get('from_lang')
    to_lang = request.form.get('to_lang')

    if not from_lang or not to_lang:
        flash('Missing language selection. Please try again.')
        return redirect(url_for('upload_form'))

    print(f"Image saved at: {filepath}")

    altered_path = process_image(filepath, from_lang, to_lang)
    processed_filename = os.path.basename(altered_path)

    return render_template('upload.html',
                           original_image=filename,
                           processed_image=processed_filename)

@app.route('/images/<filename>')
def get_original_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/outputs/images/<filename>')
def get_processed_image(filename):
    return send_from_directory(PROCESSED_FOLDER, filename)

app.secret_key = '\xf0?a\x9a\\\xff\xd4;\x0c\xcbHi'

if __name__ == '__main__':
    app.run(debug=True)
