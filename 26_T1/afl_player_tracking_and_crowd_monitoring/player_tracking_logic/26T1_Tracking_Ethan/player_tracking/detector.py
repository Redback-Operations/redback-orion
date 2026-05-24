from typing import Dict, List

import numpy as np

from .appearance import extract_appearance_feature, extract_jersey_colour_feature
from .geometry import bbox_center, euclidean_distance, iou_xyxy


def get_class_name_from_model(model, class_id: int) -> str:
    """
    Get class name from YOLO model.names if available.
    """
    try:
        names = model.names

        if isinstance(names, dict):
            return str(names.get(int(class_id), f"class_{class_id}"))

        if isinstance(names, list) and int(class_id) < len(names):
            return str(names[int(class_id)])

    except Exception:
        pass

    return f"class_{class_id}"


def parse_yolo_detections(
    result,
    frame: np.ndarray,
    model,
    player_classes,
    duplicate_center_distance: float,
) -> List[Dict]:
    """
    Convert a YOLO result object into a list of clean detection dictionaries.
    Duplicate centre suppression is applied after filtering by class.
    """
    detections: List[Dict] = []

    if result is None or result.boxes is None:
        return detections

    boxes = result.boxes
    if boxes is None or len(boxes) == 0:
        return detections

    for box in boxes:
        class_id = int(box.cls.item()) if hasattr(box.cls, "item") else int(box.cls)
        if class_id not in player_classes:
            continue

        conf = float(box.conf.item()) if hasattr(box.conf, "item") else float(box.conf)
        xyxy = box.xyxy[0].detach().cpu().numpy().astype(float).tolist()
        center = bbox_center(xyxy)

        detections.append(
            {
                "bbox": xyxy,
                "center": center,
                "conf": conf,
                # "class_id": class_id,
                "class_id": 0,
                # "class_name": get_class_name_from_model(model, class_id),
                "class_name": "PLAYER",
                # Online appearance feature for reducing ID switches.
                "appearance": extract_appearance_feature(frame, xyxy),
                # Offline jersey colour feature for team clustering.
                "jersey_feature": extract_jersey_colour_feature(frame, xyxy),
            }
        )

    return suppress_duplicate_detections(detections, duplicate_center_distance)


def suppress_duplicate_detections(detections: List[Dict], duplicate_center_distance: float) -> List[Dict]:
    """
    Remove likely duplicate detections around the same player.
    Keeps the higher-confidence detection.
    """
    if not detections:
        return []

    sorted_detections = sorted(detections, key=lambda item: item["conf"], reverse=True)
    kept: List[Dict] = []

    for det in sorted_detections:
        duplicate = False
        for existing in kept:
            center_close = euclidean_distance(det["center"], existing["center"]) < duplicate_center_distance
            overlap_high = iou_xyxy(det["bbox"], existing["bbox"]) > 0.60
            if center_close or overlap_high:
                duplicate = True
                break

        if not duplicate:
            kept.append(det)

    return kept
