"""Geometry helpers for image-based player locations and field zones."""

from __future__ import annotations

from typing import Mapping, Sequence

import numpy as np

Point = tuple[float, float]
Polygon = Sequence[Sequence[float]]


def ground_point(bbox: Sequence[float]) -> Point:
    """Return the bottom-centre of an (x1, y1, x2, y2) bounding box."""
    if len(bbox) != 4:
        raise ValueError("bbox must contain x1, y1, x2, y2")
    x1, y1, x2, y2 = map(float, bbox)
    if x2 < x1 or y2 < y1:
        raise ValueError("bbox maximum coordinates must not be below minimums")
    return ((x1 + x2) / 2.0, y2)


def scale_polygon(polygon: Polygon, width: int, height: int) -> np.ndarray:
    """Convert normalized polygon coordinates into integer pixel coordinates."""
    if width <= 0 or height <= 0:
        raise ValueError("frame dimensions must be positive")
    points = np.asarray(polygon, dtype=np.float32)
    if points.ndim != 2 or points.shape[1] != 2 or len(points) < 3:
        raise ValueError("a polygon requires at least three [x, y] points")
    if np.any(points < 0) or np.any(points > 1):
        raise ValueError("normalized polygon coordinates must be between 0 and 1")
    points[:, 0] *= width
    points[:, 1] *= height
    return np.rint(points).astype(np.int32)


def contains(point: Point, polygon_pixels: np.ndarray) -> bool:
    """Return True when a point is inside or on a polygon boundary."""
    x, y = map(float, point)
    polygon = np.asarray(polygon_pixels, dtype=float)
    inside = False
    previous = polygon[-1]
    for current in polygon:
        x1, y1 = previous
        x2, y2 = current

        cross = (x - x1) * (y2 - y1) - (y - y1) * (x2 - x1)
        on_segment = (
            abs(cross) < 1e-7
            and min(x1, x2) - 1e-7 <= x <= max(x1, x2) + 1e-7
            and min(y1, y2) - 1e-7 <= y <= max(y1, y2) + 1e-7
        )
        if on_segment:
            return True

        crosses_ray = (y1 > y) != (y2 > y)
        if crosses_ray:
            intersection_x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < intersection_x:
                inside = not inside
        previous = current
    return inside


def assign_zone(point: Point, zones: Mapping[str, np.ndarray]) -> str | None:
    """Return the first zone containing the point, otherwise None."""
    for name, polygon in zones.items():
        if contains(point, polygon):
            return name
    return None
