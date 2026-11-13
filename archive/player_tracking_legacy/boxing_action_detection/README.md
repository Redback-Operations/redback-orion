
# Boxing Action Detection Using YOLOv8

This project focuses on detecting boxing actions (such as punches and kicks) in video footage using computer vision techniques. The project leverages the YOLOv8 object detection model to process video frames and count the number of punches and kicks detected in real-time.

## Project Overview
The project involves:
- Detecting actions such as punches and kicks using a YOLOv8-based model.
- Counting the number of punches and kicks in a boxing match.
- Real-time detection and analysis using video frames from boxing/MMA matches.

The solution can be applied to combat sports analytics, helping trainers and analysts to track and assess fighter performance.

## Main Components
- **boxing_detection.py**: Python script for detecting boxing actions (punches and kicks) in video frames.
- **training_punch_detection.ipynb**: Jupyter notebook for training a custom YOLOv8 model for punch and kick detection.
- **mma_test.mp4**: Input test video of a boxing or MMA match for detecting actions.

## Pretrained Model
The YOLOv8 model used in this project is pretrained and fine-tuned on the kick-and-punch dataset. The model detects actions such as kicks and punches and classifies them accordingly. You can train the model using the `training_punch_detection.ipynb` notebook or the following Python code.

```python
%run training_punch_detection.ipynb
```

## Training the Boxing Detection Model
The boxing action detection model was trained using the `training_punch_detection.ipynb` script. This script handles downloading the dataset and training the YOLOv8 model.

### Training Instructions (Google Colab or Jupyter Notebook):
1. Open the `training_punch_detection.ipynb` script in a Google Colab or Jupyter Notebook environment.
2. Run the cells in the notebook to execute the training process.

Alternatively, if you'd like to directly run the script within a Jupyter Notebook, you can use the `%run` magic command in a Jupyter cell:

```python
%run training_punch_detection.ipynb
```

## Folder Structure

```
project/
│
├── data/
│   └── test_data/            # Folder containing input video files for detection
│       └── mma_test.mp4       # Example input video of a boxing or MMA match
│   └── output_data/           # Folder containing output video files after processing
│       └── mma_output.mp4     # Example output video showing detected punches and kicks
│
├── demo/                      # Folder containing demo images showing detection results
│   └── without_detection.png   # Screenshot of the input video without detection
│   └── detection1.png          # Screenshot showing punch detection
│   └── detection2.png          # Screenshot showing kick detection
│
├── boxing_detection.py         # Script for detecting and counting punches and kicks
├── training_punch_detection.ipynb # Script for training the custom YOLOv8 model for punch and kick detection
└── README.md                   # Project documentation
```

## Dependencies
The following dependencies are required to run the project:

- TensorFlow
- OpenCV
- YOLOv8 (Ultralytics)
- Roboflow
- Matplotlib
- NumPy

Install the dependencies with the following command:

```python
pip install ultralytics==8.0.196 opencv-python roboflow matplotlib numpy
```

## Instructions to Run

1. **Ensure all dependencies are installed**: Before running the notebook or script, ensure that you have installed all the necessary dependencies (see the Dependencies section).
2. **Place your video file**: Put your video file for detection into the `data/test_data/` directory.
3. **Run the detection script**:
   - Open a terminal and navigate to the project directory.
   - Run the detection script on the test video:

   ```python
   python boxing_detection.py --input data/test_data/mma_test.mp4 --output data/output_data/mma_output.mp4
   ```

   The script will process the video file and generate an output video with detected punches and kicks. The output video will be saved in the `data/output_data/` directory as `mma_output.mp4`.

### Example Workflow:
1. Open the `training_punch_detection.ipynb` notebook in Jupyter Notebook or Google Colab.
2. Run each cell in sequence to:
   - Load the video file.
   - Apply punch and kick detection using the YOLOv8 model.
   - Save and display the output video.
3. Once the notebook runs successfully, the output video will be saved in the `data/output_data/` directory.

### Google Colab Instructions:
If you are using Google Colab:
1. Upload the `training_punch_detection.ipynb` notebook and video files to your Colab environment or connect it to your GitHub repository.
2. Install the necessary dependencies within Colab by running the following in a cell:

```python
!pip install ultralytics==8.0.196 opencv-python roboflow matplotlib numpy
```

## Evaluation Metrics
During training and testing, the following metrics are used to evaluate model performance:
- **mAP (mean Average Precision)**: Measures the precision of predictions at different confidence thresholds.
- **Precision**: Measures the accuracy of true positive predictions against all positive predictions.
- **Recall**: Measures the proportion of true positives against all actual positives.

You can use the evaluation scripts provided in the training notebooks to assess your trained models.


