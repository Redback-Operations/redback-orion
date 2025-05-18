# RoboFlow Dataset Installation Guide  
AFL Ball Tracking Project

This guide shows you how to install and download your Roboflow dataset using three different methods:

- Jupyter Notebook (for Python-based environments)
- Terminal/Command Line (Linux, Mac, Windows WSL)
- Direct Web Download (manual method)

---

*************************** Install via Juptyer Notbook ***************************

Use this if you're working in JupyterLab, Colab, or VSCode with a Jupyter kernel.

```python
# Step 1: Install the Roboflow Python library
!pip install roboflow

# Step 2: Authenticate with your API key
from roboflow import Roboflow
rf = Roboflow(api_key="RsIHVYfJftsspBQBQPkK")  # Replace with your own API key if needed

# Step 3: Access the project and version
project = rf.workspace("nfl-ball-tracking").project("afl-ball-tracking")
version = project.version(1)

# Step 4: Download the dataset in YOLOv8 format
dataset = version.download("yolov8")


*************************** Install In Terminal ***************************

# Step 1: Download the zip file
curl -L "https://app.roboflow.com/ds/3bx9OSFFC0?key=KWq14P5EUZ" -o roboflow.zip

# Step 2: Extract it
unzip roboflow.zip

# Step 3: Clean up
rm roboflow.zip



*************************** Download the Link ***************************

Once Downloaded 
# Step 1: Extract it
Unzip roboflow.zip

# Step 2: Clean up
place unzipped folder inside directory 


https://app.roboflow.com/ds/3bx9OSFFC0?key=KWq14P5EUZ



*************************** API URL ***************************

API_URL = "https://detect.roboflow.com/afl-ball-tracking/1?api_key=RsIHVYfJftsspBQBQPkK&confidence=0.2"
