import os
from pathlib import Path
import cv2
import numpy as np
from ultralytics import YOLO

# =========================================================
# Config
# =========================================================
IMAGE_DIR = Path("data/frames")
LABEL_DIR = Path("data/labels")

MODEL_NAME = "yolo11x.pt"   # More stable for person detection; will auto-download on first run
IMG_SIZE = 1280
CONF_THRES = 0.20
IOU_THRES = 0.50

# COCO person class = 0
PERSON_CLASS_ID = 0

# Your custom three classes
TEAM_A_ID = 0
TEAM_B_ID = 1
REFEREE_ID = 2

VALID_EXTS = {".jpg", ".jpeg", ".png", ".bmp"}

LABEL_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# Color rules
# You may need to fine-tune these thresholds based on your video colors
# =========================================================
# Assumptions here:
# team_A: reddish jersey
# team_B: black jersey
# referee: fluorescent yellow jersey
#
# You can run a batch first, inspect the results, and then adjust thresholds

def classify_by_jersey_color(image, x1, y1, x2, y2):
    """
    Perform rough classification using the upper-body region inside a person box:
    - team_A: red jersey
    - team_B: black jersey
    - referee: fluorescent yellow jersey

    Returns: class_id
    """
    h, w = image.shape[:2]

    x1 = max(0, min(int(x1), w - 1))
    y1 = max(0, min(int(y1), h - 1))
    x2 = max(0, min(int(x2), w - 1))
    y2 = max(0, min(int(y2), h - 1))

    if x2 <= x1 or y2 <= y1:
        return TEAM_A_ID

    crop = image[y1:y2, x1:x2]
    if crop.size == 0:
        return TEAM_A_ID

    # Only use the upper body to reduce interference from grass, shorts, and shoes
    ch, cw = crop.shape[:2]
    upper_y1 = int(ch * 0.10)
    upper_y2 = int(ch * 0.55)
    body = crop[upper_y1:upper_y2, :]

    if body.size == 0:
        body = crop

    hsv = cv2.cvtColor(body, cv2.COLOR_BGR2HSV)

    # =========================
    # Color masks
    # =========================

    # Red (team_A)
    red_mask1 = cv2.inRange(hsv, np.array([0, 70, 50]), np.array([10, 255, 255]))
    red_mask2 = cv2.inRange(hsv, np.array([170, 70, 50]), np.array([180, 255, 255]))
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)

    # Fluorescent yellow (referee)
    # Use higher brightness and saturation to avoid confusion with normal yellow or grass
    ref_yellow_mask = cv2.inRange(hsv, np.array([20, 120, 140]), np.array([40, 255, 255]))

    # Black (team_B)
    # Black is usually low brightness with low to medium saturation
    black_mask = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 120, 70]))

    red_score = int(np.count_nonzero(red_mask))
    ref_score = int(np.count_nonzero(ref_yellow_mask))
    black_score = int(np.count_nonzero(black_mask))

    total = body.shape[0] * body.shape[1]
    if total <= 0:
        return TEAM_A_ID

    red_ratio = red_score / total
    ref_ratio = ref_score / total
    black_ratio = black_score / total

    # =========================
    # Decision order
    # =========================
    # Detect referee first (fluorescent yellow is the most distinctive)
    if ref_ratio > 0.08:
        return REFEREE_ID

    # Then detect red team
    if red_ratio > 0.06 and red_ratio >= black_ratio:
        return TEAM_A_ID

    # Then detect black team
    if black_ratio > 0.12:
        return TEAM_B_ID

    # =========================
    # Fallback strategy
    # =========================
    mean_h = np.mean(hsv[:, :, 0])
    mean_s = np.mean(hsv[:, :, 1])
    mean_v = np.mean(hsv[:, :, 2])

    # Bright yellow tendency
    if 20 <= mean_h <= 40 and mean_s > 100 and mean_v > 120:
        return REFEREE_ID

    # Red tendency
    if (mean_h <= 10 or mean_h >= 170) and mean_s > 70:
        return TEAM_A_ID

    # Dark tendency
    if mean_v < 75:
        return TEAM_B_ID

    # Default to red team; fix manually later if needed
    return TEAM_A_ID


def xyxy_to_yolo(x1, y1, x2, y2, img_w, img_h):
    x_min = min(x1, x2)
    x_max = max(x1, x2)
    y_min = min(y1, y2)
    y_max = max(y1, y2)

    bw = x_max - x_min
    bh = y_max - y_min
    xc = x_min + bw / 2.0
    yc = y_min + bh / 2.0

    return xc / img_w, yc / img_h, bw / img_w, bh / img_h


def main():
    image_files = sorted([p for p in IMAGE_DIR.iterdir() if p.suffix.lower() in VALID_EXTS])
    if not image_files:
        print(f"No images found in {IMAGE_DIR}")
        return

    model = YOLO(MODEL_NAME)

    print(f"Found {len(image_files)} images.")
    print(f"Using model: {MODEL_NAME}")
    print("Prelabeling started...")

    for idx, img_path in enumerate(image_files, start=1):
        image = cv2.imread(str(img_path))
        if image is None:
            print(f"[{idx}/{len(image_files)}] Failed to read: {img_path.name}")
            continue

        img_h, img_w = image.shape[:2]
        label_path = LABEL_DIR / f"{img_path.stem}.txt"

        results = model.predict(
            source=str(img_path),
            imgsz=IMG_SIZE,
            conf=CONF_THRES,
            iou=IOU_THRES,
            classes=[PERSON_CLASS_ID],   # Detect person only
            verbose=False
        )

        lines = []

        if results and len(results) > 0:
            r = results[0]
            if r.boxes is not None and len(r.boxes) > 0:
                xyxy = r.boxes.xyxy.cpu().numpy()

                for box in xyxy:
                    x1, y1, x2, y2 = box.tolist()

                    # Filter out boxes that are too small
                    bw = x2 - x1
                    bh = y2 - y1
                    if bw < 8 or bh < 15:
                        continue

                    class_id = classify_by_jersey_color(image, x1, y1, x2, y2)
                    xc, yc, w, h = xyxy_to_yolo(x1, y1, x2, y2, img_w, img_h)

                    if w <= 0 or h <= 0:
                        continue

                    lines.append(f"{class_id} {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}")

        with open(label_path, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")

        if idx % 50 == 0 or idx == len(image_files):
            print(f"[{idx}/{len(image_files)}] Saved: {label_path.name}")

    print("Done. Prelabels written to:")
    print(LABEL_DIR)
    print("\nNext step: open yolo_manual_annotator.py and manually fix classes / boxes.")


if __name__ == "__main__":
    main()