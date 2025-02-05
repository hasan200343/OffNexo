import logging
import os
import psutil
import sys
from flask import Flask, render_template, request, send_from_directory, abort

# Define base_path to point to the current working directory
base_path = os.getcwd()

# Now you can use base_path to set the template folder
template_folder = os.path.join(base_path, 'templates')

app = Flask(__name__, template_folder=os.path.join(base_path, 'templates'))

# Force logs to flush immediately
logging.basicConfig(level=logging.DEBUG, format="%(message)s", handlers=[logging.StreamHandler(sys.stdout)])

@app.before_request
def flush_logs():
    sys.stdout.flush()

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

def is_flask_running():
    # Check if Flask is already running using the process name and PID
    current_pid = os.getpid()
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if proc.info['name'] == 'python.exe' and proc.info['pid'] != current_pid:
            try:
                if 'flask' in proc.info['cmdline']:
                    return True
            except psutil.NoSuchProcess:
                pass
    return False

if __name__ == "__main__":
    # Check if Flask is already running before starting a new instance
    if not is_flask_running():
        app.logger.info("Starting Flask app...")
        app.run(debug=True, host='0.0.0.0', use_reloader=False)  # Disable reloader to prevent multiple instances
    else:
        print("Flask app is already running.")
