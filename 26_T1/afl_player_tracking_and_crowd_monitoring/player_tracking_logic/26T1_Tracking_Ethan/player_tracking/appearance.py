from typing import Iterable, Optional

import cv2
import numpy as np

from .geometry import bbox_to_int


def extract_appearance_feature(frame: np.ndarray, bbox: Iterable[float]) -> Optional[np.ndarray]:
    """
    Extract a lightweight colour histogram feature from a detection crop.

    This is intentionally simple and dependency-light. It is useful for reducing
    ID switches when two players cross, but it should not be treated as a full ReID model.
    """
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

    crop = frame[y1:y2, x1:x2]
    if crop.size == 0:
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
