# Import necessary libraries
from ultralytics import YOLO  # YOLOv8 for object detection
import cv2                    # OpenCV for image/video processing
import pickle                 # Used to save/load intermediate detection results
import os

# Define a class for tracking the ball using YOLO
class BallTracker:
    def __init__(self, model_path):
        # Load a trained YOLOv8 model
        self.model = YOLO(model_path)

    def detect_frames(self, frames, read_from_stub=False, stub_path=None):
        # This method detects balls in a list of frames
        # It supports reading from a cached result (stub) to avoid reprocessing
        ball_detections = []

        # If using cached detection results
        if read_from_stub and stub_path:
            with open(stub_path, 'rb') as f:
                return pickle.load(f)

        # Perform detection on each frame
        for frame in frames:
            ball_dict = self.detect_frame(frame)
            ball_detections.append(ball_dict)

        # Optionally save detections to stub
        if stub_path:
            with open(stub_path, 'wb') as f:
                pickle.dump(ball_detections, f)

        return ball_detections

    def detect_frame(self, frame):
        # Run inference on a single frame and return bounding box as a dictionary
        results = self.model.predict(frame, conf=0.15)[0]  # Confidence threshold can be adjusted
        ball_dict = {}
        for box in results.boxes:
            result = box.xyxy.tolist()[0]  # Get bounding box coordinates
            ball_dict[1] = result  # Using 1 as a dummy ID (can be improved for real tracking)
        return ball_dict

    def draw_bboxes(self, frames, ball_detections):
        # Draw bounding boxes and labels on the frames
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
    # === STEP 1: Provide path to the input video file ===
    video_path = "Test1.mp4"  # <-- Replace with your video file path

    # === STEP 2: Provide path to your trained YOLOv8 model ===
    trained_model_path = "runs/detect/train/weights/best.pt"  # <-- Update this with the correct model file path

    # Create an instance of BallTracker using the trained model
    tracker = BallTracker(trained_model_path)

    # Load frames from the input video
    frames = load_video_frames(video_path)

    # Detect the ball in each frame
    detections = tracker.detect_frames(frames)

    # Draw bounding boxes on the frames
    output_frames = tracker.draw_bboxes(frames, detections)

    # Save the resulting video with detections
    save_video(output_frames, "nfl_ball_output.mp4")  # Output file name can be changed
