"""Minimal entry point for the density and zoning task."""

from __future__ import annotations

import json
import os
from typing import Any


def get_zone_definitions(frame_width: int, frame_height: int) -> list[dict[str, Any]]:
    """
    Create a simple 2x2 grid of zones.

    Zone layout:
    A1 = top-left
    A2 = top-right
    B1 = bottom-left
    B2 = bottom-right
    """
    half_width = frame_width / 2
    half_height = frame_height / 2

    return [
        {"zone_id": "A1", "x_min": 0, "y_min": 0, "x_max": half_width, "y_max": half_height},
        {"zone_id": "A2", "x_min": half_width, "y_min": 0, "x_max": frame_width, "y_max": half_height},
        {"zone_id": "B1", "x_min": 0, "y_min": half_height, "x_max": half_width, "y_max": frame_height},
        {"zone_id": "B2", "x_min": half_width, "y_min": half_height, "x_max": frame_width, "y_max": frame_height},
    ]


def bbox_center(bbox: list[float]) -> tuple[float, float]:
    """
    Calculate the center point of a bounding box.

    bbox format: [x1, y1, x2, y2]
    """
    if len(bbox) != 4:
        raise ValueError("Bounding box must contain exactly 4 values: [x1, y1, x2, y2].")

    x1, y1, x2, y2 = bbox
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    return center_x, center_y


def find_zone(center_x: float, center_y: float, zones: list[dict[str, Any]]) -> str | None:
    """Return the zone_id for a center point."""
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


def analyze_density(input_data: dict[str, Any]) -> dict[str, Any]:
    """Calculate zone counts and density values from detection results."""
    video_id = input_data.get("video_id", "unknown_video")
    frames = input_data.get("frames", [])

    # Configurable frame size for simple first version
    frame_width = input_data.get("frame_width", 500)
    frame_height = input_data.get("frame_height", 500)

    zones = get_zone_definitions(frame_width, frame_height)

    # Initialize counts for all zones
    zone_counts = {zone["zone_id"]: 0 for zone in zones}

    # Process detections frame by frame
    for frame in frames:
        detections = frame.get("detections", [])

        for detection in detections:
            bbox = detection.get("bbox")
            if not bbox:
                continue

            try:
                center_x, center_y = bbox_center(bbox)
            except ValueError:
                continue

            zone_id = find_zone(center_x, center_y, zones)

            if zone_id is not None:
                zone_counts[zone_id] += 1

    densities = normalize_counts(zone_counts)

    return {
        "video_id": video_id,
        "zones": [
            {
                "zone_id": zone["zone_id"],
                "person_count": zone_counts[zone["zone_id"]],
                "density": densities[zone["zone_id"]],
            }
            for zone in zones
        ],
    }


if __name__ == "__main__":
    
    sample_input = {
        "video_id": "match_01",
        "frame_width": 500,
        "frame_height": 500,
        "frames": [
            {
                "frame_id": 1,
                "timestamp": 0.04,
                "person_count": 4,
                "detections": [
                    {"bbox": [80, 80, 120, 120], "confidence": 0.95},    # A1
                    {"bbox": [140, 100, 180, 140], "confidence": 0.92},  # A1
                    {"bbox": [280, 150, 320, 190], "confidence": 0.90},  # A2
                    {"bbox": [400, 350, 440, 390], "confidence": 0.88},  # B2
                ],
            }
        ],
    }

    result = analyze_density(sample_input)

    os.makedirs("output", exist_ok=True)
    output_path = os.path.join("output", "density_summary.json")

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=2)

    print(json.dumps(result, indent=2))
    print(f"\nSaved output to: {output_path}")