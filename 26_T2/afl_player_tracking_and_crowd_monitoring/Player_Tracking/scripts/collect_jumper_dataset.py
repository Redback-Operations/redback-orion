import os
import cv2
import numpy as np
from ultralytics import YOLO

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
VIDEO_PATH = "test_match.mp4"
OUTPUT_DIR = "jumper_dataset"
CONF_THRESHOLD = 0.5        # Minimum detection confidence
LAPLACIAN_VAR_THRESH = 80.0  # Sharpness threshold (filters out motion blur)
UPPER_BODY_RATIO = 0.60     # Keep top 60% of player box (torso/jumper area)

os.makedirs(OUTPUT_DIR, exist_ok=True)

def is_sharp(image: np.ndarray, threshold: float) -> bool:
    """Checks image blur using Laplacian variance."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    return variance > threshold

def extract_jumper_crops():
    # Load YOLO detection model (e.g., yolo11n.pt or custom model)
    model = YOLO("yolo11n.pt")
    
    # Run tracking on video feed (using built-in ByteTrack)
    results = model.track(
        source=VIDEO_PATH,
        stream=True,
        conf=CONF_THRESHOLD,
        classes=[0],  # Class 0 is 'person' in standard COCO models
        tracker="bytetrack.yaml"
    )

    saved_count = 0

    for frame_idx, r in enumerate(results):
        frame = r.orig_img
        
        # Ensure tracking IDs exist
        if r.boxes is None or r.boxes.id is None:
            continue

        boxes = r.boxes.xyxy.cpu().numpy()
        track_ids = r.boxes.id.cpu().numpy().astype(int)

        for box, track_id in zip(boxes, track_ids):
            x1, y1, x2, y2 = map(int, box)
            
            # 1. Compute torso/jumper cropping coordinates
            box_height = y2 - y1
            y2_upper = y1 + int(box_height * UPPER_BODY_RATIO)
            
            # Boundary checks
            h, w, _ = frame.shape
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2_upper = min(w, x2), min(h, y2_upper)

            crop = frame[y1:y2_upper, x1:x2]
            if crop.size == 0:
                continue

            # 2. Blur detection filter
            if not is_sharp(crop, LAPLACIAN_VAR_THRESH):
                continue

            # 3. Save crop organized by Track ID
            track_dir = os.path.join(OUTPUT_DIR, f"player_track_{track_id}")
            os.makedirs(track_dir, exist_ok=True)

            filename = f"frame_{frame_idx:06d}_track_{track_id}.jpg"
            cv2.imwrite(os.path.join(track_dir, filename), crop)
            saved_count += 1

    print(f"Dataset extraction complete! Saved {saved_count} sharp jersey crops to '{OUTPUT_DIR}'.")

if __name__ == "__main__":
    extract_jumper_crops()