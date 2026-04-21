# crowd_detection/main.py
# Detects faces in image frames using YOLOv8.

import cv2
from ultralytics import YOLO

from .config import DEFAULT_CONF, DEFAULT_IOU, MODEL_NAME, PEOPLE_ANNOTATED_DIR, PEOPLE_MODEL_NAME, ANNOTATED_DIR

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
    ANNOTATED_DIR.mkdir(parents=True, exist_ok=True)
    PEOPLE_ANNOTATED_DIR.mkdir(parents=True, exist_ok=True)

    for frame_data in processed_video["frames"]:
        frame = cv2.imread(frame_data["frame_path"])

        if frame is None:
            print(f"[WARN] Could not read frame {frame_data['frame_id']} — skipping")
            continue

        face_detections = detect_faces(face_model, frame, DEFAULT_CONF, DEFAULT_IOU)
        people_detections = detect_people(people_model, frame, DEFAULT_CONF, DEFAULT_IOU)

        # save annotated frame
        annotated = draw_boxes(frame, face_detections)
        cv2.imwrite(str(ANNOTATED_DIR / f"frame_{frame_data['frame_id']:04d}.jpg"), annotated)

        # save annotated frame for people
        people_annotated = draw_people_boxes(frame, people_detections)
        cv2.imwrite(str(PEOPLE_ANNOTATED_DIR / f"frame_{frame_data['frame_id']:04d}.jpg"), people_annotated)

        all_results.append({
            "frame_id": frame_data["frame_id"],
            "timestamp": frame_data["timestamp"],
            "person_count": len(face_detections),
            "face_detections": face_detections,
            "people_detections": people_detections,
        })

    return {
        "video_id": processed_video["video_id"],
        "frames":   all_results,
    }

    
    