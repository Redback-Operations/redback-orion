# Import necessary libraries
from ultralytics import YOLO  # YOLOv8 for object detection
import cv2                    # OpenCV for image/video processing
import json                   # JSON used to safely store detection results
import os

# Define a class for tracking the ball using YOLO
class BallTracker:
    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def detect_frames(self, frames, read_from_stub=False, stub_path=None):
        ball_detections = []

        # Load detection data from JSON stub if available
        if read_from_stub and stub_path and os.path.exists(stub_path):
            with open(stub_path, 'r') as f:
                return json.load(f)

        # Perform detection on each frame
        for frame in frames:
            ball_dict = self.detect_frame(frame)
            ball_detections.append(ball_dict)

        # Save detection data to JSON stub
        if stub_path:
            with open(stub_path, 'w') as f:
                json.dump(ball_detections, f, indent=2)

        return ball_detections

    def detect_frame(self, frame):
        results = self.model.predict(frame, conf=0.15)[0]
        ball_dict = {}
        for box in results.boxes:
            result = box.xyxy.tolist()[0]  # Get bounding box
            ball_dict[1] = result          # Dummy ID (can be expanded)
        return ball_dict

    def draw_bboxes(self, frames, ball_detections):
        output_frames = []
        for frame, ball_dict in zip(frames, ball_detections):
            for track_id, bbox in ball_dict.items():
                x1, y1, x2, y2 = map(int, bbox)
                cv2.putText(frame, f"Ball", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            output_frames.append(frame)
        return output_frames

# Function to read video frames from a file
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

# Function to save video frames to a new output video
def save_video(frames, output_path, fps=30):
    height, width, _ = frames[0].shape
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
    for frame in frames:
        out.write(frame)
    out.release()

# === Run Inference ===
if __name__ == "__main__":
    video_path = "Test1.mp4"  # Update as needed
    trained_model_path = "runs/detect/train/weights/best.pt"  # Update path
    stub_path = "ball_detections.json"  # Optional: cache file

    tracker = BallTracker(trained_model_path)
    frames = load_video_frames(video_path)

    # Use stub if file exists, otherwise do fresh detection
    detections = tracker.detect_frames(frames, read_from_stub=True, stub_path=stub_path)

    output_frames = tracker.draw_bboxes(frames, detections)
    save_video(output_frames, "nfl_ball_output.mp4")
