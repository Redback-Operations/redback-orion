
# AFL Ball Tracking: Training and Inference Guide

This guide explains how to:

1. Set up your environment
2. Download and prepare the dataset
3. Train a YOLOv8 model on the AFL ball tracking dataset
4. Use a trained model to track the ball in video files

---

## Environment Setup

### If using JupyterLab, Colab, or VSCode:

```bash
!pip install roboflow ultralytics opencv-python-headless
```

---

## Step 1: Download the Dataset from Roboflow

Authenticate and download the dataset from Roboflow in YOLOv8 format.

```python
from roboflow import Roboflow

# Replace with your actual API key
rf = Roboflow(api_key="RsIHVYfJftsspBQBQPkK")

project = rf.workspace("nfl-ball-tracking").project("afl-ball-tracking")
version = project.version(1)

# Download dataset in YOLOv8 format
dataset = version.download("yolov8")
```

### API Key Notes:
- Your API key authenticates your Roboflow account to download datasets and use inference APIs.
- Keep it secret like a password. You can find it in your [Roboflow account settings](https://roboflow.com/).

---

## Step 2: Train the YOLOv8 Model

Once downloaded, navigate into the dataset directory and run the training:

```bash
cd afl-ball-tracking-1  # Adjust this to your actual dataset folder
```

```python
from ultralytics import YOLO

model = YOLO("yolov8n.pt")  # or "yolov8s.pt" for a slightly larger model

# Train using the Roboflow dataset
model.train(data="data.yaml", epochs=50, imgsz=640)
```

### Output
The trained model will be saved under:
```
runs/detect/train/weights/best.pt
```

---

## Step 3: Run Inference on a Video

### Use the following Python class to detect and annotate AFL balls in a video.

```python
from ultralytics import YOLO
import cv2
import pickle

class BallTracker:
    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def detect_frames(self, frames, read_from_stub=False, stub_path=None):
        if read_from_stub and stub_path:
            with open(stub_path, 'rb') as f:
                return pickle.load(f)
        ball_detections = []
        for frame in frames:
            ball_dict = {}
            results = self.model.predict(frame, conf=0.15)[0]
            for box in results.boxes:
                result = box.xyxy.tolist()[0]
                ball_dict[1] = result
            ball_detections.append(ball_dict)
        if stub_path:
            with open(stub_path, 'wb') as f:
                pickle.dump(ball_detections, f)
        return ball_detections

    def draw_bboxes(self, frames, ball_detections):
        output_frames = []
        for frame, ball_dict in zip(frames, ball_detections):
            for bbox in ball_dict.values():
                x1, y1, x2, y2 = map(int, bbox)
                cv2.putText(frame, "Ball", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            output_frames.append(frame)
        return output_frames
```

### Video Handling Helpers

```python
def load_video_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()
    return frames

def save_video(frames, output_path, fps=30):
    height, width, _ = frames[0].shape
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
    for frame in frames:
        out.write(frame)
    out.release()
```

### Example Usage

```python
video_path = "Test1.mp4"
trained_model_path = "runs/detect/train/weights/best.pt"  # Update with your actual model path

tracker = BallTracker(trained_model_path)
frames = load_video_frames(video_path)
detections = tracker.detect_frames(frames)
output_frames = tracker.draw_bboxes(frames, detections)
save_video(output_frames, "nfl_ball_output.mp4")
```

---

## Optional: Use the Roboflow Hosted Inference API

You can also perform inference without local training using Roboflow’s API.

```bash
base64 YOUR_IMAGE.jpg | curl -d @- "https://detect.roboflow.com/afl-ball-tracking/1?api_key=RsIHVYfJftsspBQBQPkK&confidence=0.25"
```

Replace `YOUR_IMAGE.jpg` with your actual image path.

---

## Summary

- Use Roboflow to get labeled data
- Train YOLOv8 on that data
- Use `BallTracker` to detect and draw bounding boxes on videos
- Optionally call Roboflow’s hosted model via API

---
