# human-pose-estimation-opencv
Perform Human Pose Estimation in OpenCV Using OpenPose MobileNet

![OpenCV Using OpenPose MobileNet](output.JPG)


# How to use

System requirement:Windows

All the materials and footage are acquired from Google and YouTube for education use

- Test with webcam

```
python openpose.py
```

- Test with image
```
python openpose.py --input image.jpg
```

- Use `--thr` to increase confidence threshold

```
python openpose.py --input image.jpg --thr 0.5
```

# Improvements and Explanations
1.Code Structure and Readability:

- Added comments to explain the purpose of different sections, which improves readability.
  Grouped related constants and structures together (BODY_PARTS and POSE_PAIRS) to enhance organization.

2.Error Handling:

- Added a print statement to notify when no frame is captured, helping with debugging.

3.Performance Improvements:

- The use of frame.shape[:2] instead of separate width and height variables to enhance clarity.
  Created a blob before setting it as input to the network to clarify data preparation.

4.Assertions and Conditions:

- Kept assertions for checking the dimensions of the output against the defined body parts, ensuring data consistency.

# Notes:
- Ensure that the TensorFlow model file (graph_opt.pb) is correctly specified in your working directory.
- The program is designed to capture video frames either from a specified file or directly from a camera. Ensure the input source is correctly set when running the script.
- Adjust the threshold (--thr) and width/height parameters when running the script to optimize performance for different environments or video resolutions.
- Run this script from the command line, passing in the appropriate arguments [python openpose.py --input video.mp4 --thr 0.3 --width 640 --height 480
]