# Face Detection with YOLOv8

## Project Overview
This project aims to develop an efficient and robust **face detection system** using the YOLOv8 framework. The system can process images, videos, and real-time camera feeds, making it versatile for various applications such as surveillance, user authentication, and video analysis. The project demonstrates the integration of state-of-the-art machine learning techniques with real-world deployment.

---

## Objectives

### Core Functionality
- Implement face detection on images, videos, and real-time streams with high accuracy.
- Ensure a modular design for scalability and further enhancements.

### Efficiency and Usability
- Optimize the YOLOv8 model for deployment on systems with constrained resources.
- Provide clear and detailed documentation for reproducibility and collaboration.

### Collaboration and Knowledge Sharing
- Assist team members in improving detection systems through advanced techniques.
- Contribute to smooth project handovers with comprehensive documentation.

---

## Completed Deliveries

### Dataset Selection and Preparation
- Selected and configured a **face detection dataset** from Roboflow.
- Ensured compliance with the dataset license (**CC BY 4.0**) for ethical use.

### Model Training and Evaluation
- Trained the YOLOv8 model on the prepared dataset with hyperparameter optimization.
- Evaluated model performance using metrics like precision, recall, mAP50, and mAP50-95 to ensure reliability.

### Feature Integration
- Implemented functionalities for:
  - **Image Prediction**: Detect faces in single images.
  - **Video Prediction**: Process videos for face detection, frame by frame.
  - **Real-Time Prediction**: Perform live detection using a connected camera.

### Documentation and Collaboration
- Documented all program code and testing results.
- Shared the project on GitHub for team collaboration and review.

---

## Performance Analysis
### Key Metrics
- **Precision (P):** 0.959
- **Recall (R):** 0.942
- **mAP50:** 0.979
- **mAP50-95:** 0.879

The YOLOv8 model achieved high accuracy, making it suitable for real-world applications.

---

## How to Use

### Requirements
- Python 3.8+
- Install the following libraries manually:
  ```python
  pip install torch==1.4.0
  pip install opencv-python
  pip install numpy
  pip install matplotlib
  pip install moviepy
  pip install ultralytics
  ```

### Instructions
1. **Set Up Your Environment**: Ensure Python is installed, and manually install the required libraries as listed above.
2. **Run Image Prediction**:
- Open the `image_prediction.py` script, and set the paths for the input image and YOLOv8 model directly in the code:
```python
img_path = "path_to_image.jpg"
model_path = "face_detector.pt"
```
- Run the script:
```bash
python image_prediction.py
```
3. **Run Video Prediction**:
- Open the `video_prediction.py` script, and set the paths for the input video and YOLOv8 model:
```python
video_path = "path_to_video.mp4"
model_path = "face_detector.pt"
```
- Run the script:
```bash
python video_prediction.py
```
4. **Run Real-Time Prediction**: Open the `realtime_prediction.py` script, ensure your webcam is accessible, and run the script:
```bash
python realtime_prediction.py
```

---

## Example Code

### Image Prediction
```python
from ultralytics import YOLO
import cv2

model = YOLO("face_detector.pt")
img = cv2.imread("path_to_image.jpg")
results = model(img)
results.show()
```

### Real-Time Prediction
```python
import cv2
from ultralytics import YOLO

model = YOLO("face_detector.pt")
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    results = model(frame)
    results.show()
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

## Open Issues
- **Optimization**: Improve real-time processing speed to enhance performance in live environments.
- **Resource Efficiency**: Reduce memory usage and computational overhead to make the model more suitable for deployment on devices with limited hardware capabilities.
- **Error Handling**: Add better error-handling mechanisms for edge cases, such as unsupported file formats or camera connection failures.
- **Scalability**: Ensure the system can handle larger datasets and more complex scenarios in future iterations.

## Contributors
- Yuekai Zhang
