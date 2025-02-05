import sys
from cx_Freeze import setup, Executable

# List of additional packages to include
build_exe_options = {
    "packages": ["flask", "tkinter", "threading", "queue", "webbrowser", "re", "psutil", "subprocess", "logging", "os", "sys"],
    "include_files": ['templates'],  # Ensure the templates folder is included
}

# Define the main script and base (no GUI mode)
base = None
if sys.platform == "win32":
    base = "Win32GUI"

# Create the Executable configuration for both app.py (Flask) and app_gui.py (Tkinter)
executables = [
    Executable("app.py", base=base, target_name="Flask.exe"),
    Executable("app_gui.py", base=base, target_name="OFFNexo.exe")
]

# Set up the build process
setup(
    name="OFFNexo",
    version="1.0",
    description="OFFNexo Utility",
    options={"build_exe": build_exe_options},
    executables=executables
)
