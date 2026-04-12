# crowd_detection/main.py
# Detects faces in image frames using YOLOv8.

import cv2
from ultralytics import YOLO

from .config import DEFAULT_CONF, DEFAULT_IOU, MODEL_NAME, ANNOTATED_DIR

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

def draw_boxes(frame, detections):
    output = frame.copy()

    for d in detections:
        x1, y1, x2, y2 = d["bbox"]

        # Draw bounding box around face
        cv2.rectangle(output, (x1, y1), (x2, y2), (0, 200, 80), 2)

        # Draw confidence score above the box
        label = f"{d['confidence']:.2f}"
        cv2.putText(output, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 80), 1)

    # Draw total face count in top left corner
    cv2.putText(output, f"Faces: {len(detections)}", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 220, 100), 2)

    return output


def detect_crowd(processed_video: dict) -> dict:
    model       = load_model()
    all_results = []

    # create output folder
    ANNOTATED_DIR.mkdir(parents=True, exist_ok=True)

    for frame_data in processed_video["frames"]:
        frame = cv2.imread(frame_data["frame_path"])

        if frame is None:
            print(f"[WARN] Could not read frame {frame_data['frame_id']} — skipping")
            continue

        detections = detect_faces(model, frame, DEFAULT_CONF, DEFAULT_IOU)

        # save annotated frame
        annotated = draw_boxes(frame, detections)
        cv2.imwrite(str(ANNOTATED_DIR / f"frame_{frame_data['frame_id']:04d}.jpg"), annotated)

        all_results.append({
            "frame_id":     frame_data["frame_id"],
            "timestamp":    frame_data["timestamp"],
            "person_count": len(detections),
            "detections":   detections,
        })

    return {
        "video_id": processed_video["video_id"],
        "frames":   all_results,
    }

    
    