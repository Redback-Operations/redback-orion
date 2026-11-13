# Pose and Weapon Detection in Fencing Using Computer Vision

This project focuses on detecting player poses and weapons (such as swords in fencing) using computer vision techniques. It includes custom models for pose estimation and weapon detection, leveraging machine learning frameworks like TensorFlow and YOLO.

## Project Overview
The project involves:
- Detecting player poses using MoveNet.
- Detecting weapons using a YOLO-based model.
- Real-time detection and analysis using video frames.

The solution can be applied to real-time sports analysis, specifically for monitoring and tracking athletes in fencing matches.

## Main Components
- **main.ipynb**: Jupyter notebook for integrating pose estimation and weapon detection workflows.
- **pose_estimation.py**: Python script for detecting player poses using the MoveNet model.
- **weapon_detection.py**: Python script for detecting weapons (swords) using YOLO-based object detection.




## Data Sources
- **Weapon Detection Dataset**: [Fencing Dataset on Roboflow](https://universe.roboflow.com/phineas-pham/fencing-fxdmr)
To download the dataset:
  ```python
  from roboflow import Roboflow
  rf = Roboflow(api_key="YOUR_API_KEY")
  project = rf.workspace("phineas-pham").project("fencing-fxdmr")
  version = project.version(4)
  dataset = version.download("yolov8")
  ```

- **Pose estimation model** load the MoveNet model for pose detection, use the following code
```python
import tensorflow_hub as hub
# Load the MoveNet model from TensorFlow Hub
model = hub.load('https://tfhub.dev/google/movenet/multipose/lightning/1')
movenet = model.signatures['serving_default']
```

## Training the Sword Detection Model

The sword detection model was trained using the `training_weapon.ipynb` script, which is included in this repository. The script handles downloading the dataset, filtering the labels to focus only on the "weapon" class, and training the YOLOv8 model.

### Training Instructions (Google Colab or Jupyter Notebook):
1. Open the `training_weapon.ipynb` script in a Google Colab or Jupyter Notebook environment.
2. Run the cells in the notebook to execute the training process.

Alternatively, if you'd like to directly run the script within a Jupyter Notebook, you can use the `%run` magic command in a Jupyter cell:

   ```python
   %run training_weapon.ipynb
```

## Folder Structure

Here’s an overview of the project folder structure:

```plaintext
project/
│
├── data/
│   └── test_data/            # Folder containing input video files for detection
│       └── fencing_test.mp4   # Example input video
│   └── output_data/           # Folder containing output video files after processing
│       └── output_video.avi   # Example output video showing pose and weapon detection
│
├── demo/                      # Folder containing demo images showing detection results
│   └── without_detection.png   # Screenshot of the input video without detection
│   └── detection1.png          # Screenshot showing pose and weapon detection (1st stage)
│   └── detection2.png          # Screenshot showing pose and weapon detection (final output)
│
├── main.py                    # Main script that integrates pose and weapon detection
├── pose_estimation.py          # Script for detecting player poses using MoveNet
├── weapon_detection.py         # Script for detecting weapons (swords) using the custom YOLOv8 model
├── main.ipynb                  # Jupyter notebook with an integrated workflow for pose and weapon detection
└── training_weapon.ipynb       # Script for training the custom YOLOv8 model for sword detection

```




## Dependencies
The following dependencies are required to run the project:

- TensorFlow
- TensorFlow Hub
- OpenCV
- YOLOv8 (Ultralytics)
- Matplotlib
- NumPy
- Roboflow

To install these dependencies, run the following command:

!pip install opencv-python tensorflow tensorflow_hub ultralytics matplotlib numpy roboflow


## Entry Point and Instructions

### Entry Point
The entry point to the project is the `main.ipynb` notebook. This notebook integrates the functionality of both the `pose_estimation.py` and `weapon_detection.py` scripts and runs the full pipeline for pose and weapon detection.

### Instructions to Run

1. **Ensure all dependencies are installed**: Before running the notebook, ensure that you have installed all the necessary dependencies (see the **Dependencies** section).

2. **Place your video file**: Put your video file for detection into the `data/test_data/` directory.

3. **Running the Notebook**:
   - Open the `main.ipynb` notebook in your Jupyter environment or Google Colab.
   - Ensure that your environment has access to the necessary scripts (`pose_estimation.py` and `weapon_detection.py`).
   - Follow the cells in the notebook sequentially to run the pose and weapon detection pipeline.

4. **Output**: The notebook will process the video file and generate an output video with both player poses and weapons detected. The output video will be saved in the `data/output_data/` directory as `output_video.avi`.

### Example Workflow:
- Open `main.ipynb` in Jupyter Notebook or Google Colab.
- Run each cell in sequence to:
   1. Load the video file.
   2. Apply pose estimation using the MoveNet model.
   3. Apply weapon detection using the YOLOv8 model.
   4. Save and display the output video.

Once the notebook runs successfully, you will see an output video saved in the `data/output_data/` directory.

### Google Colab Instructions:
If you are using Google Colab:
1. Upload the `main.ipynb` notebook and video files to your Colab environment or connect it to your GitHub repository.
2. Install the necessary dependencies within Colab by running the following in a cell:
   ```python
   !pip install opencv-python tensorflow tensorflow_hub ultralytics matplotlib numpy roboflow
```
