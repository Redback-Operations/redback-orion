from __future__ import annotations

from typing import Iterable, Sequence, Tuple

import cv2
import numpy as np


Point = Tuple[float, float]


def compute_homography(
    image_points: Sequence[Point],
    field_points: Sequence[Point],
) -> np.ndarray:
    """
    Compute a perspective transform from image coordinates to field coordinates.

    At least four matching point pairs are required.
    """
    if len(image_points) < 4 or len(field_points) < 4:
        raise ValueError("At least four point pairs are required.")

    if len(image_points) != len(field_points):
        raise ValueError("Image points and field points must have the same length.")

    image_array = np.asarray(image_points, dtype=np.float32)
    field_array = np.asarray(field_points, dtype=np.float32)

    homography, _ = cv2.findHomography(
        image_array,
        field_array,
        method=0,
    )

    if homography is None:
        raise ValueError("Could not compute homography from the supplied points.")

    return homography


def transform_point(
    point: Iterable[float],
    homography: np.ndarray,
) -> Point:
    """
    Transform one image-space point into field coordinates.
    """
    x, y = [float(v) for v in point]

    source = np.array(
        [[[x, y]]],
        dtype=np.float32,
    )

    transformed = cv2.perspectiveTransform(
        source,
        homography,
    )[0][0]

    return float(transformed[0]), float(transformed[1])