from typing import Iterable, Optional, Tuple

import cv2
import numpy as np

from .geometry import bbox_to_int


def _clip_bbox(frame: np.ndarray, bbox: Iterable[float]) -> Optional[Tuple[int, int, int, int]]:
    if frame is None or frame.size == 0:
        return None

    h, w = frame.shape[:2]
    x1, y1, x2, y2 = bbox_to_int(bbox)

    x1 = max(0, min(w - 1, x1))
    x2 = max(0, min(w - 1, x2))
    y1 = max(0, min(h - 1, y1))
    y2 = max(0, min(h - 1, y2))

    if x2 <= x1 or y2 <= y1:
        return None

    return x1, y1, x2, y2


def extract_torso_crop(frame: np.ndarray, bbox: Iterable[float]) -> Optional[np.ndarray]:
    """
    Extract the torso / jersey area from a player bounding box.

    This follows the JerseyColorDetection idea: use the upper-body region rather
    than the full detection box, so the colour feature is less affected by grass,
    socks, shorts, field markings, and background pixels.
    """
    clipped = _clip_bbox(frame, bbox)
    if clipped is None:
        return None

    x1, y1, x2, y2 = clipped
    box_w = x2 - x1
    box_h = y2 - y1

    if box_w <= 2 or box_h <= 2:
        return None

    # AFL broadcast detections often include head and legs.
    # This region keeps the central upper body where jersey colour is strongest.
    torso_x1 = int(round(x1 + 0.15 * box_w))
    torso_x2 = int(round(x1 + 0.85 * box_w))
    torso_y1 = int(round(y1 + 0.18 * box_h))
    torso_y2 = int(round(y1 + 0.62 * box_h))

    torso_x1 = max(0, min(frame.shape[1] - 1, torso_x1))
    torso_x2 = max(0, min(frame.shape[1] - 1, torso_x2))
    torso_y1 = max(0, min(frame.shape[0] - 1, torso_y1))
    torso_y2 = max(0, min(frame.shape[0] - 1, torso_y2))

    if torso_x2 <= torso_x1 or torso_y2 <= torso_y1:
        return None

    crop = frame[torso_y1:torso_y2, torso_x1:torso_x2]
    if crop.size == 0:
        return None

    return crop


def extract_appearance_feature(frame: np.ndarray, bbox: Iterable[float]) -> Optional[np.ndarray]:
    """
    Extract a lightweight HSV histogram feature from the torso crop.

    This is used online for matching IDs across frames. It is intentionally simple
    and should not be treated as a full deep ReID model.
    """
    crop = extract_torso_crop(frame, bbox)
    if crop is None:
        return None

    crop = cv2.resize(crop, (32, 64), interpolation=cv2.INTER_AREA)
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)

    # H/S/V histograms. Small bins keep the vector compact and stable.
    hist_h = cv2.calcHist([hsv], [0], None, [16], [0, 180]).reshape(-1)
    hist_s = cv2.calcHist([hsv], [1], None, [16], [0, 256]).reshape(-1)
    hist_v = cv2.calcHist([hsv], [2], None, [16], [0, 256]).reshape(-1)

    feature = np.concatenate([hist_h, hist_s, hist_v]).astype(np.float32)
    norm = np.linalg.norm(feature)
    if norm <= 1e-12:
        return None

    return feature / norm


def extract_jersey_colour_feature(frame: np.ndarray, bbox: Iterable[float]) -> Optional[np.ndarray]:
    """
    Extract a JerseyColorDetection-style colour vector from the torso region.

    Feature vector:
        [median_h, median_s, median_v,
         red_ratio, yellow_ratio, blue_ratio, white_ratio, dark_ratio]
    """
    crop = extract_torso_crop(frame, bbox)
    if crop is None:
        return None

    crop = cv2.resize(crop, (32, 64), interpolation=cv2.INTER_AREA)
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)

    h = hsv[:, :, 0].astype(np.float32)
    s = hsv[:, :, 1].astype(np.float32)
    v = hsv[:, :, 2].astype(np.float32)

    total = float(h.size)
    if total <= 0:
        return None

    # OpenCV HSV hue range is [0, 179].
    red_mask = (((h <= 10) | (h >= 170)) & (s >= 70) & (v >= 50))
    yellow_mask = ((h >= 18) & (h <= 40) & (s >= 60) & (v >= 60))
    blue_mask = ((h >= 90) & (h <= 135) & (s >= 50) & (v >= 50))
    white_mask = ((s <= 45) & (v >= 165))
    dark_mask = (v <= 75)

    feature = np.array(
        [
            np.median(h),
            np.median(s),
            np.median(v),
            np.count_nonzero(red_mask) / total,
            np.count_nonzero(yellow_mask) / total,
            np.count_nonzero(blue_mask) / total,
            np.count_nonzero(white_mask) / total,
            np.count_nonzero(dark_mask) / total,
        ],
        dtype=np.float32,
    )

    return feature


def update_appearance(old_feature, new_feature, momentum: float):
    if old_feature is None:
        return new_feature
    if new_feature is None:
        return old_feature

    updated = momentum * old_feature + (1.0 - momentum) * new_feature
    norm = np.linalg.norm(updated)
    if norm <= 1e-12:
        return old_feature
    return updated / norm
