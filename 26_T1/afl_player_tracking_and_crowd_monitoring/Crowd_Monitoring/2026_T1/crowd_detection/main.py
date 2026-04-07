# crowd_detection/main.py
# Detects faces in image frames using YOLOv8.

import cv2
from ultralytics import YOLO

from .config import DEFAULT_CONF, DEFAULT_IOU, MODEL_NAME


def load_model():
    print(f"[INFO] Loading model: {MODEL_NAME}")
    model = YOLO(MODEL_NAME)
    print("[INFO] Model ready ✓\n")
    return model



def detect_faces(model, frame, conf, iou):
    results = model(frame, conf=conf, iou=iou, verbose=False)[0]
    detections = []
    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        
        detections.append({
            "bbox": [x1, y1, x2, y2],
            "confidence": round(float(box.conf[0]), 4),
        })
    return detections



def detect_crowd(processed_video: dict) -> dict:
   
    model       = load_model()
    all_results = []

    for frame_data in processed_video["frames"]:
        
        frame = cv2.imread(frame_data["frame_path"])

        if frame is None:
            print(f"[WARN] Could not read frame {frame_data['frame_id']} — skipping")
            continue

        detections = detect_faces(model, frame, DEFAULT_CONF, DEFAULT_IOU)

        all_results.append({
            "frame_id":     frame_data["frame_id"],
            "timestamp":    frame_data["timestamp"],
            "person_count": len(detections),
            "detections": detections
        })

    return {
        "video_id": processed_video["video_id"],
        "frames":   all_results
    }

    
    