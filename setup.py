import subprocess
import sys
# Define the Python version you want to use
python_version = "3.8"

# Create the virtual environment
subprocess.check_call([sys.executable, "-m", "venv", "venv"])

# Activate the virtual environment
if sys.platform == "win32":
    activate_script = "venv\\Scripts\\activate.bat"
else:
    activate_script = "venv/bin/activate"
subprocess.check_call([activate_script])

# Upgrade pip
subprocess.check_call(["python", "-m", "pip", "install", "--upgrade", "pip"])

# Install the required packages
subprocess.check_call(["pip", "install", "-r", "requirements.txt"])