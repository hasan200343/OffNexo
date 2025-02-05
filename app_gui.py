import tkinter as tk
from tkinter import ttk
import subprocess
import threading
import queue
import webbrowser
import re


# Global variable to store the Flask process
flask_process = None
added_urls = set()  # To track added URLs

# Function to run Flask app in a separate thread and capture logs
def run_flask_app(log_queue):
    global flask_process

    # Start the Flask app
    flask_process = subprocess.Popen(
        ['Flask.exe'],  # Run Flask app
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )

    # Read output line by line
    for line in iter(flask_process.stdout.readline, ''):
        log_queue.put(line.strip())  # Send logs to queue

    # Ensure flask_process is not None before closing stdout and stderr
    if flask_process:
        flask_process.stdout.close()
        flask_process.stderr.close()


# Function to update GUI with logs
def update_gui_log(log_queue):
    while not log_queue.empty():
        line = log_queue.get_nowait()

        # Use regular expression to extract any URL (IPv4 addresses) from the log
        urls = re.findall(r'http[s]?://(?:[0-9]{1,3}\.){3}[0-9]{1,3}:\d+', line)

        # Check if the URL is of the form "http://<ip_address>:5000"
        for url in urls:
            if url not in added_urls:
                # Temporarily enable the text widget to insert the text
                log_output.config(state=tk.NORMAL)
                log_output.insert(tk.END, f"Running on {url}\n")  # Append the URL to Tkinter text box
                log_output.see(tk.END)  # Auto-scroll to bottom
                log_output.config(state=tk.DISABLED)

                # Create a button for the URL
                create_url_button(url)

    window.after(100, update_gui_log, log_queue)  # Keep updating logs

# Function to create a button for each URL
def create_url_button(url):
    button = ttk.Button(url_frame, text=f"Open {url}", command=lambda: open_url(url), style="URLButton.TButton")
    button.pack(pady=5, fill='x', padx=20)

# Function to open URL in default web browser
def open_url(url):
    webbrowser.open(url)

# Function to start Flask app
def start_flask():
    start_button.config(state=tk.DISABLED)  # Disable button after starting
    stop_button.config(state=tk.NORMAL)    # Enable stop button
    log_queue = queue.Queue()  # Queue to store logs

    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask_app, args=(log_queue,), daemon=True)
    flask_thread.start()

    # Start updating logs in GUI
    window.after(100, update_gui_log, log_queue)

# Function to stop Flask app and clear URL buttons
def stop_flask():
    global flask_process
    if flask_process:
        flask_process.terminate()  # Stop the Flask process
        flask_process = None  # Reset the process variable

    # Destroy all the URL buttons
    for widget in url_frame.winfo_children():
        widget.destroy()
        added_urls.clear()  # Clear the set of added URLs

    stop_button.config(state=tk.DISABLED)  # Disable stop button after stopping
    start_button.config(state=tk.NORMAL)   # Enable start button

# Create Tkinter window
window = tk.Tk()
window.title("OFFNexo")

# Set a fancy font for the window
window.option_add('*Font', 'Helvetica 12')

# Add some styling
style = ttk.Style()

# Customize button styles
style.configure("TButton",
                padding=6,
                relief="flat",
                background="#D32F2F",  # Red color for start button
                foreground="black")
style.map("TButton",
          background=[('active', '#B71C1C')])  # Darker red on hover

# Customize URL buttons
style.configure("URLButton.TButton",
                padding=6,
                relief="flat",
                background="#D32F2F",  # Red color for URL buttons
                foreground="black")
style.map("URLButton.TButton",
          background=[('active', '#B71C1C')])  # Darker red on hover

# Customize the log text area
log_output = tk.Text(window, width=80, height=20, wrap=tk.WORD, bg="#000000", fg="#FF6347", bd=0, font=("Helvetica", 12), state=tk.DISABLED)
log_output.pack(padx=20, pady=10)

# Create a frame for URL buttons
url_frame = tk.Frame(window)
url_frame.pack(pady=10, padx=20, fill='x')

# Create a frame for the start/stop buttons (horizontal layout)
button_frame = tk.Frame(window)
button_frame.pack(pady=10, padx=20)

# Create start and stop buttons inside the button_frame (horizontal layout)
start_button = ttk.Button(button_frame, text="Start OFFNexo", command=start_flask)
start_button.pack(side=tk.LEFT, padx=10)

stop_button = ttk.Button(button_frame, text="Stop OFFNexo", command=stop_flask, state=tk.DISABLED)
stop_button.pack(side=tk.LEFT, padx=10)

# Start Tkinter event loop
window.mainloop()
