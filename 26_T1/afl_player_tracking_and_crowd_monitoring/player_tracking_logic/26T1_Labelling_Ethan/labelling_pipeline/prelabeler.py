"""YOLO pre-labelling with simple jersey-colour class estimation."""

from pathlib import Path
import cv2
import numpy as np
from labelling_pipeline.utils import list_image_files


def _as_np_range(hsv_range):
    """Convert a config HSV range into OpenCV-compatible numpy arrays."""
    lower, upper = hsv_range
    return np.array(lower, dtype=np.uint8), np.array(upper, dtype=np.uint8)


def classify_by_jersey_color(config, image, x1, y1, x2, y2):
    """
    Estimate the class id from the upper-body colour inside a detected person box.

    The method is intentionally lightweight. It is used only to create initial
    labels that can be corrected later with the manual annotation tool.
    """
    h, w = image.shape[:2]

    x1 = max(0, min(int(x1), w - 1))
    y1 = max(0, min(int(y1), h - 1))
    x2 = max(0, min(int(x2), w - 1))
    y2 = max(0, min(int(y2), h - 1))

    if x2 <= x1 or y2 <= y1:
        return config.TEAM_A_ID

    crop = image[y1:y2, x1:x2]
    if crop.size == 0:
        return config.TEAM_A_ID

    crop_h, _ = crop.shape[:2]
    upper_y1 = int(crop_h * float(config.UPPER_BODY_Y1_RATIO))
    upper_y2 = int(crop_h * float(config.UPPER_BODY_Y2_RATIO))
    body = crop[upper_y1:upper_y2, :]

    if body.size == 0:
        body = crop

    hsv = cv2.cvtColor(body, cv2.COLOR_BGR2HSV)

    red_lower_1, red_upper_1 = _as_np_range(config.RED_HSV_RANGE_1)
    red_lower_2, red_upper_2 = _as_np_range(config.RED_HSV_RANGE_2)
    ref_lower, ref_upper = _as_np_range(config.REFEREE_YELLOW_HSV_RANGE)
    black_lower, black_upper = _as_np_range(config.BLACK_HSV_RANGE)

    red_mask_1 = cv2.inRange(hsv, red_lower_1, red_upper_1)
    red_mask_2 = cv2.inRange(hsv, red_lower_2, red_upper_2)
    red_mask = cv2.bitwise_or(red_mask_1, red_mask_2)
    referee_yellow_mask = cv2.inRange(hsv, ref_lower, ref_upper)
    black_mask = cv2.inRange(hsv, black_lower, black_upper)

    red_score = int(np.count_nonzero(red_mask))
    referee_score = int(np.count_nonzero(referee_yellow_mask))
    black_score = int(np.count_nonzero(black_mask))

    total = body.shape[0] * body.shape[1]
    if total <= 0:
        return config.TEAM_A_ID

    red_ratio = red_score / total
    referee_ratio = referee_score / total
    black_ratio = black_score / total

    if referee_ratio > float(config.REFEREE_YELLOW_RATIO_THRES):
        return config.REFEREE_ID

    if red_ratio > float(config.RED_RATIO_THRES) and red_ratio >= black_ratio:
        return config.TEAM_A_ID

    if black_ratio > float(config.BLACK_RATIO_THRES):
        return config.TEAM_B_ID

    mean_h = float(np.mean(hsv[:, :, 0]))
    mean_s = float(np.mean(hsv[:, :, 1]))
    mean_v = float(np.mean(hsv[:, :, 2]))

    if 20 <= mean_h <= 40 and mean_s > 100 and mean_v > 120:
        return config.REFEREE_ID

    if (mean_h <= 10 or mean_h >= 170) and mean_s > 70:
        return config.TEAM_A_ID

    if mean_v < 75:
        return config.TEAM_B_ID

    return config.TEAM_A_ID


def xyxy_to_yolo(x1, y1, x2, y2, img_w, img_h):
    """Convert absolute xyxy box coordinates into YOLO-normalised format."""
    x_min = min(x1, x2)
    x_max = max(x1, x2)
    y_min = min(y1, y2)
    y_max = max(y1, y2)

    box_w = x_max - x_min
    box_h = y_max - y_min
    x_center = x_min + box_w / 2.0
    y_center = y_min + box_h / 2.0

    return x_center / img_w, y_center / img_h, box_w / img_w, box_h / img_h


def _resolve_model(config):
    """Return the local model path if provided; otherwise return the YOLO model name."""
    if config.YOLO_MODEL_PATH is not None:
        return str(Path(config.YOLO_MODEL_PATH))
    return str(config.YOLO_MODEL_NAME)


def run_prelabeler(config) -> None:
    """Run YOLO person detection and write YOLO-format label files."""
    image_dir = Path(config.FRAME_DIR)
    label_dir = Path(config.LABEL_DIR)
    label_dir.mkdir(parents=True, exist_ok=True)

    image_files = list_image_files(image_dir, config.VALID_IMAGE_EXTS)
    if not image_files:
        print(f"No images found in {image_dir}")
        print("Run extract_frames first or put images into data/frames/.")
        return

    model_source = _resolve_model(config)

    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise ImportError(
            "Ultralytics is required for pre-labelling. Install it with: "
            "pip install ultralytics"
        ) from exc

    model = YOLO(model_source)

    print(f"Found {len(image_files)} image(s).")
    print(f"Using model: {model_source}")
    print("Pre-labelling started...")

    for idx, img_path in enumerate(image_files, start=1):
        image = cv2.imread(str(img_path))
        if image is None:
            print(f"[{idx}/{len(image_files)}] Failed to read: {img_path.name}")
            continue

        img_h, img_w = image.shape[:2]
        label_path = label_dir / f"{img_path.stem}.txt"

        if label_path.exists() and not config.OVERWRITE_EXISTING_LABELS:
            print(f"[{idx}/{len(image_files)}] Skipped existing label: {label_path.name}")
            continue

        results = model.predict(
            source=str(img_path),
            imgsz=int(config.YOLO_IMAGE_SIZE),
            conf=float(config.YOLO_CONF_THRES),
            iou=float(config.YOLO_IOU_THRES),
            classes=[int(config.YOLO_PERSON_CLASS_ID)],
            verbose=False,
        )

        lines = []

        if results and len(results) > 0:
            result = results[0]
            if result.boxes is not None and len(result.boxes) > 0:
                xyxy_boxes = result.boxes.xyxy.cpu().numpy()

                for box in xyxy_boxes:
                    x1, y1, x2, y2 = box.tolist()

                    box_w = x2 - x1
                    box_h = y2 - y1
                    if box_w < int(config.MIN_BOX_WIDTH) or box_h < int(config.MIN_BOX_HEIGHT):
                        continue

                    class_id = classify_by_jersey_color(config, image, x1, y1, x2, y2)
                    x_center, y_center, w_norm, h_norm = xyxy_to_yolo(x1, y1, x2, y2, img_w, img_h)

                    if w_norm <= 0 or h_norm <= 0:
                        continue

                    lines.append(
                        f"{class_id} {x_center:.6f} {y_center:.6f} {w_norm:.6f} {h_norm:.6f}"
                    )

        with open(label_path, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")

        if idx % 50 == 0 or idx == len(image_files):
            print(f"[{idx}/{len(image_files)}] Saved: {label_path.name}")

    print("Done. Pre-labels written to:")
    print(label_dir)
    print("Next step: set OPERATION_MODE = 'manual_annotate' in config.py and run python main.py.")
