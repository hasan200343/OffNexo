import os
from flask import Flask, render_template, request, send_from_directory, abort

app = Flask(__name__)

# Automatically set the uploads folder relative to where the script is run
BASE_DIR = os.getcwd()  # Current working directory
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle multiple file uploads
        files = request.files.getlist('files')  # Retrieve all files
        for file in files:
            if file:
                # Save each file to the uploads folder
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)

    # List files in the upload folder
    try:
        files = os.listdir(app.config['UPLOAD_FOLDER'])
    except FileNotFoundError:
        files = []

    return render_template("index.html", files=files)  # Pass the file list to the template


@app.route('/uploads/<filename>')
def download_file(filename):
    # Serve the file for download if it exists
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
