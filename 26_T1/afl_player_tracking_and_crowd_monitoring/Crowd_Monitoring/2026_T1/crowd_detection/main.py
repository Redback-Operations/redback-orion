# crowd_detection/main.py
# Detects faces in image frames using YOLOv8.

import cv2
from ultralytics import YOLO
from pathlib import Path

from .config import DEFAULT_CONF, DEFAULT_IOU, MODEL_NAME, PEOPLE_ANNOTATED_DIR, PEOPLE_MODEL_NAME, ANNOTATED_DIR

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FACE_OUTPUT_DIR = ANNOTATED_DIR if ANNOTATED_DIR.is_absolute() else PROJECT_ROOT / ANNOTATED_DIR
PEOPLE_OUTPUT_DIR = PEOPLE_ANNOTATED_DIR if PEOPLE_ANNOTATED_DIR.is_absolute() else PROJECT_ROOT / PEOPLE_ANNOTATED_DIR

def load_models():
    print(f"[INFO] Loading face model: {MODEL_NAME}")
    face_model = YOLO(MODEL_NAME)

    print(f"[INFO] Loading people model: {PEOPLE_MODEL_NAME}")
    people_model = YOLO(PEOPLE_MODEL_NAME)

    print("[INFO] Models ready ✓\n")
    return face_model, people_model



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

def detect_people(model, frame, conf, iou):
    results = model(frame, conf=conf, iou=iou, verbose=False)[0]
    detections = []

    for box in results.boxes:
        cls = int(box.cls[0])

        # COCO class 0 = person
        if cls != 0:
            continue

        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())

        detections.append({
            "bbox": [x1, y1, x2, y2],
            "confidence": round(float(box.conf[0]), 4),
        })

    return detections

def draw_people_boxes(frame, detections):
    output = frame.copy()

    for d in detections:
        x1, y1, x2, y2 = d["bbox"]

        # Blue boxes for people
        cv2.rectangle(output, (x1, y1), (x2, y2), (255, 100, 0), 2)

        label = f"{d['confidence']:.2f}"
        cv2.putText(output, label, (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (255, 100, 0), 1)
  
    cv2.putText(output, f"People: {len(detections)}", (10, 25),cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 100, 0), 2)

    return output

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
    face_model, people_model = load_models() 
    all_results = []
    
    # create output folder
    FACE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PEOPLE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for frame_data in processed_video["frames"]:
        frame_path = frame_data["frame_path"]
        resolved_frame_path = Path(frame_path)
        if not resolved_frame_path.is_absolute():
            resolved_frame_path = PROJECT_ROOT / resolved_frame_path

        frame = cv2.imread(str(resolved_frame_path))

        if frame is None:
            print(f"[WARN] Could not read frame {frame_data['frame_id']} — skipping")
            continue

        face_detections = detect_faces(face_model, frame, DEFAULT_CONF, DEFAULT_IOU)
        people_detections = detect_people(people_model, frame, DEFAULT_CONF, DEFAULT_IOU)

        # save annotated frame
        annotated = draw_boxes(frame, face_detections)
        face_output_path = FACE_OUTPUT_DIR / f"frame_{frame_data['frame_id']:04d}.jpg"
        cv2.imwrite(str(face_output_path), annotated)

        # save annotated frame for people
        people_annotated = draw_people_boxes(frame, people_detections)
        people_output_path = PEOPLE_OUTPUT_DIR / f"frame_{frame_data['frame_id']:04d}.jpg"
        cv2.imwrite(str(people_output_path), people_annotated)
        face_annotated_frame_path = str(face_output_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
        people_annotated_frame_path = str(people_output_path.relative_to(PROJECT_ROOT)).replace("\\", "/")

        all_results.append({
            "frame_id": frame_data["frame_id"],
            "timestamp": frame_data["timestamp"],
            "frame_path": frame_path,
            "face_annotated_frame_path": face_annotated_frame_path,
            "people_annotated_frame_path": people_annotated_frame_path,
            "person_count": len(people_detections),
            "face_count": len(face_detections),
            "face_detections": face_detections,
            "people_detections": people_detections,
        })

    return {
        "video_id": processed_video["video_id"],
        "frames":   all_results,
    }

    
    
