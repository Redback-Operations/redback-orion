

from __future__ import annotations

import json
import os
from typing import Any


def get_zone_definitions(
    frame_width: int,
    frame_height: int,
    rows: int = 2,
    cols: int = 2,
) -> list[dict[str, Any]]:
    """
    Create a configurable grid of zones.

    Example for 2x2:
    A1 A2
    B1 B2
    """
    if frame_width <= 0 or frame_height <= 0:
        raise ValueError("Frame width and height must be positive integers.")
    if rows <= 0 or cols <= 0:
        raise ValueError("Rows and cols must be positive integers.")

    zone_width = frame_width / cols
    zone_height = frame_height / rows
    zones: list[dict[str, Any]] = []

    for row in range(rows):
        for col in range(cols):
            row_label = chr(ord("A") + row)
            zone_id = f"{row_label}{col + 1}"

            x_min = col * zone_width
            y_min = row * zone_height
            x_max = (col + 1) * zone_width
            y_max = (row + 1) * zone_height

            zones.append(
                {
                    "zone_id": zone_id,
                    "x_min": x_min,
                    "y_min": y_min,
                    "x_max": x_max,
                    "y_max": y_max,
                }
            )

    return zones


def is_valid_bbox(bbox: list[float] | None) -> bool:
    """Check whether a bounding box is valid."""
    if bbox is None or len(bbox) != 4:
        return False

    x1, y1, x2, y2 = bbox
    return x2 > x1 and y2 > y1


def bbox_center(bbox: list[float]) -> tuple[float, float]:
    """
    Calculate the center point of a bounding box.

    bbox format: [x1, y1, x2, y2]
    """
    if not is_valid_bbox(bbox):
        raise ValueError("Invalid bounding box. Expected [x1, y1, x2, y2] with x2 > x1 and y2 > y1.")

    x1, y1, x2, y2 = bbox
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    return center_x, center_y


def clamp_point(x: float, y: float, frame_width: int, frame_height: int) -> tuple[float, float]:
    """
    Clamp a point so it stays inside the frame.
    Helps handle edge cases near frame boundaries.
    """
    x = min(max(x, 0), frame_width - 1e-6)
    y = min(max(y, 0), frame_height - 1e-6)
    return x, y


def find_zone(
    center_x: float,
    center_y: float,
    zones: list[dict[str, Any]],
    frame_width: int,
    frame_height: int,
) -> str | None:
    """Return the zone_id for a center point."""
    center_x, center_y = clamp_point(center_x, center_y, frame_width, frame_height)

    for zone in zones:
        if (
            zone["x_min"] <= center_x < zone["x_max"]
            and zone["y_min"] <= center_y < zone["y_max"]
        ):
            return zone["zone_id"]

    return None


def normalize_counts(zone_counts: dict[str, int]) -> dict[str, float]:
    """
    Normalize person counts to density values between 0.0 and 1.0.
    Highest count becomes 1.0.
    """
    max_count = max(zone_counts.values()) if zone_counts else 0

    if max_count == 0:
        return {zone_id: 0.0 for zone_id in zone_counts}

    return {
        zone_id: round(count / max_count, 2)
        for zone_id, count in zone_counts.items()
    }


def classify_density(density: float) -> str:
    """Convert normalized density into a label."""
    if density == 0:
        return "Low"
    if density < 0.67:
        return "Medium"
    return "High"


def analyze_density(input_data: dict[str, Any]) -> dict[str, Any]:
    """Calculate zone counts and density values from detection results."""
    video_id = input_data.get("video_id", "unknown_video")
    frames = input_data.get("frames", [])

    frame_width = input_data.get("frame_width", 500)
    frame_height = input_data.get("frame_height", 500)

    grid_rows = input_data.get("grid_rows", 2)
    grid_cols = input_data.get("grid_cols", 2)
    confidence_threshold = input_data.get("confidence_threshold", 0.50)

    zones = get_zone_definitions(frame_width, frame_height, grid_rows, grid_cols)

    zone_counts = {zone["zone_id"]: 0 for zone in zones}
    skipped_invalid_bbox = 0
    skipped_low_confidence = 0

    for frame in frames:
        detections = frame.get("detections", [])

        for detection in detections:
            bbox = detection.get("bbox")
            confidence = detection.get("confidence", 1.0)

            if confidence < confidence_threshold:
                skipped_low_confidence += 1
                continue

            if not is_valid_bbox(bbox):
                skipped_invalid_bbox += 1
                continue

            center_x, center_y = bbox_center(bbox)
            zone_id = find_zone(center_x, center_y, zones, frame_width, frame_height)

            if zone_id is not None:
                zone_counts[zone_id] += 1

    densities = normalize_counts(zone_counts)

    return {
        "video_id": video_id,
        "frame_width": frame_width,
        "frame_height": frame_height,
        "grid_rows": grid_rows,
        "grid_cols": grid_cols,
        "confidence_threshold": confidence_threshold,
        "summary": {
            "total_frames": len(frames),
            "skipped_invalid_bbox": skipped_invalid_bbox,
            "skipped_low_confidence": skipped_low_confidence,
        },
        "zones": [
            {
                "zone_id": zone["zone_id"],
                "person_count": zone_counts[zone["zone_id"]],
                "density": densities[zone["zone_id"]],
                "density_level": classify_density(densities[zone["zone_id"]]),
            }
            for zone in zones
        ],
    }


if __name__ == "__main__":
    sample_input = {
        "video_id": "crowd_video_test",
        "frame_width": 1280,
        "frame_height": 720,
        "grid_rows": 2,
        "grid_cols": 2,
        "confidence_threshold": 0.50,
        "frames": [
            {
                "frame_id": 1,
                "timestamp": 0.03,
                "detections": [
                    {"bbox": [100, 200, 180, 350], "confidence": 0.92},
                    {"bbox": [300, 220, 380, 370], "confidence": 0.89},
                    {"bbox": [700, 250, 780, 400], "confidence": 0.95},
                    {"bbox": [900, 300, 980, 450], "confidence": 0.87},
                    {"bbox": [600, 200, 600, 260], "confidence": 0.91},
                    {"bbox": [500, 300, 560, 390], "confidence": 0.20},
                ],
            }
        ],
    }

    result = analyze_density(sample_input)

    os.makedirs("output", exist_ok=True)
    output_path = os.path.join("output", "density_summary_sprint2.json")

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=2)

    print(json.dumps(result, indent=2))
    print(f"\nSaved output to: {output_path}")