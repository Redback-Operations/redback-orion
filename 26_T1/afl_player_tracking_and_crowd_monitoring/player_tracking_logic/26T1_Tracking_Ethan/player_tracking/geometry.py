import math
from typing import Iterable, Tuple

import numpy as np


BBox = Tuple[float, float, float, float]
Point = Tuple[float, float]


def bbox_center(bbox: Iterable[float]) -> Point:
    x1, y1, x2, y2 = [float(v) for v in bbox]
    return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)


def bbox_area(bbox: Iterable[float]) -> float:
    x1, y1, x2, y2 = [float(v) for v in bbox]
    return max(0.0, x2 - x1) * max(0.0, y2 - y1)


def euclidean_distance(p1: Iterable[float], p2: Iterable[float]) -> float:
    a = np.asarray(list(p1), dtype=np.float32)
    b = np.asarray(list(p2), dtype=np.float32)
    return float(np.linalg.norm(a - b))


def iou_xyxy(box_a: Iterable[float], box_b: Iterable[float]) -> float:
    ax1, ay1, ax2, ay2 = [float(v) for v in box_a]
    bx1, by1, bx2, by2 = [float(v) for v in box_b]

    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)

    inter_w = max(0.0, inter_x2 - inter_x1)
    inter_h = max(0.0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h

    union = bbox_area(box_a) + bbox_area(box_b) - inter_area
    if union <= 0:
        return 0.0
    return float(inter_area / union)


def cosine_similarity(vec_a, vec_b) -> float:
    if vec_a is None or vec_b is None:
        return 0.0

    a = np.asarray(vec_a, dtype=np.float32).reshape(-1)
    b = np.asarray(vec_b, dtype=np.float32).reshape(-1)

    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom <= 1e-12:
        return 0.0

    return float(np.dot(a, b) / denom)


def direction_cost(previous_center, current_center, detection_center) -> float:
    """
    Cost based on whether the detection continues the recent motion direction.
    The output is in [0, 1]. Lower means more consistent.
    """
    if previous_center is None or current_center is None or detection_center is None:
        return 0.5

    motion = np.asarray(current_center, dtype=np.float32) - np.asarray(previous_center, dtype=np.float32)
    candidate = np.asarray(detection_center, dtype=np.float32) - np.asarray(current_center, dtype=np.float32)

    motion_norm = float(np.linalg.norm(motion))
    candidate_norm = float(np.linalg.norm(candidate))

    if motion_norm < 1e-6 or candidate_norm < 1e-6:
        return 0.5

    cos_val = float(np.dot(motion, candidate) / (motion_norm * candidate_norm))
    cos_val = max(-1.0, min(1.0, cos_val))

    # cos=1 -> cost=0, cos=-1 -> cost=1
    return float((1.0 - cos_val) / 2.0)


def clip_bbox_to_frame(bbox: Iterable[float], width: int, height: int) -> BBox:
    x1, y1, x2, y2 = [float(v) for v in bbox]
    x1 = max(0.0, min(float(width - 1), x1))
    y1 = max(0.0, min(float(height - 1), y1))
    x2 = max(0.0, min(float(width - 1), x2))
    y2 = max(0.0, min(float(height - 1), y2))
    return x1, y1, x2, y2


def bbox_to_int(bbox: Iterable[float]) -> Tuple[int, int, int, int]:
    x1, y1, x2, y2 = [float(v) for v in bbox]
    return int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2))
