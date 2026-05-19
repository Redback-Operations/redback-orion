
from __future__ import annotations

import json
import os
from typing import Any


DENSITY_PRECISION = 2


def get_zone_definitions(
    frame_width: int,
    frame_height: int,
    rows: int = 2,
    cols: int = 2,
) -> list[dict[str, float | str]]:
    """Create grid-based zone definitions."""
    if frame_width <= 0 or frame_height <= 0:
        raise ValueError("Frame width and height must be positive.")
    if rows <= 0 or cols <= 0:
        raise ValueError("Rows and columns must be positive.")

    zone_width = frame_width / cols
    zone_height = frame_height / rows
    zones = []

    for row in range(rows):
        for col in range(cols):
            zone_id = f"{chr(ord('A') + row)}{col + 1}"
            zones.append(
                {
                    "zone_id": zone_id,
                    "x_min": col * zone_width,
                    "y_min": row * zone_height,
                    "x_max": (col + 1) * zone_width,
                    "y_max": (row + 1) * zone_height,
                }
            )

    return zones


def is_valid_bbox(
    bbox: list[float] | None,
    frame_width: int,
    frame_height: int,
) -> bool:
    """Validate bounding box format and frame boundary."""
    if bbox is None or len(bbox) != 4:
        return False

    x1, y1, x2, y2 = bbox

    return (
        x2 > x1
        and y2 > y1
        and 0 <= x1 < frame_width
        and 0 <= y1 < frame_height
        and 0 < x2 <= frame_width
        and 0 < y2 <= frame_height
    )


def bbox_center(bbox: list[float]) -> tuple[float, float]:
    """Return the centre point of a bounding box."""
    x1, y1, x2, y2 = bbox
    return (x1 + x2) / 2, (y1 + y2) / 2


def find_zone(
    center_x: float,
    center_y: float,
    zones: list[dict[str, Any]],
) -> str | None:
    """Find the zone that contains the centre point."""
    for zone in zones:
        if (
            zone["x_min"] <= center_x < zone["x_max"]
            and zone["y_min"] <= center_y < zone["y_max"]
        ):
            return str(zone["zone_id"])

    return None


def calculate_density(zone_counts: dict[str, int]) -> dict[str, float]:
    """Normalize zone counts into density values between 0.0 and 1.0."""
    max_count = max(zone_counts.values()) if zone_counts else 0

    if max_count == 0:
        return {zone_id: 0.0 for zone_id in zone_counts}

    return {
        zone_id: round(count / max_count, DENSITY_PRECISION)
        for zone_id, count in zone_counts.items()
    }


def calculate_average_count(
    zone_counts: dict[str, int],
    total_frames: int,
) -> dict[str, float]:
    """Calculate average person count per zone per frame."""
    if total_frames <= 0:
        return {zone_id: 0.0 for zone_id in zone_counts}

    return {
        zone_id: round(count / total_frames, DENSITY_PRECISION)
        for zone_id, count in zone_counts.items()
    }


def classify_density(density: float) -> str:
    """Convert density value into a readable level."""
    if density <= 0:
        return "Low"
    if density < 0.67:
        return "Medium"
    return "High"


def build_heatmap_data(zones_output: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Create heatmap-ready output from zone density values."""
    return [
        {
            "zone_id": zone["zone_id"],
            "value": zone["density"],
            "person_count": zone["person_count"],
            "density_level": zone["density_level"],
        }
        for zone in zones_output
    ]


def validate_output(result: dict[str, Any]) -> None:
    """Validate output against the density zoning schema."""
    if "video_id" not in result:
        raise ValueError("Output must contain video_id.")

    if "zones" not in result or not isinstance(result["zones"], list):
        raise ValueError("Output must contain a zones list.")

    if "heatmap_data" not in result or not isinstance(result["heatmap_data"], list):
        raise ValueError("Output must contain heatmap_data list.")

    for zone in result["zones"]:
        required_fields = [
            "zone_id",
            "person_count",
            "density",
            "average_count_per_frame",
            "density_level",
        ]

        for field in required_fields:
            if field not in zone:
                raise ValueError(f"Missing required field in zone output: {field}")

        if not isinstance(zone["zone_id"], str):
            raise TypeError("zone_id must be a string.")

        if not isinstance(zone["person_count"], int):
            raise TypeError("person_count must be an integer.")

        if not isinstance(zone["density"], (int, float)):
            raise TypeError("density must be numeric.")

        if not isinstance(zone["average_count_per_frame"], (int, float)):
            raise TypeError("average_count_per_frame must be numeric.")

        if not 0.0 <= zone["density"] <= 1.0:
            raise ValueError("density must be between 0.0 and 1.0.")

        if zone["density_level"] not in ["Low", "Medium", "High"]:
            raise ValueError("density_level must be Low, Medium, or High.")

    for item in result["heatmap_data"]:
        required_fields = ["zone_id", "value", "person_count", "density_level"]

        for field in required_fields:
            if field not in item:
                raise ValueError(f"Missing required field in heatmap_data: {field}")

        if not 0.0 <= item["value"] <= 1.0:
            raise ValueError("heatmap_data value must be between 0.0 and 1.0.")


def analyze_density(input_data: dict[str, Any]) -> dict[str, Any]:
    """Calculate zone-level crowd counts and density values."""
    video_id = input_data.get("video_id", "unknown_video")
    frames = input_data.get("frames", [])

    frame_width = int(input_data.get("frame_width", 1280))
    frame_height = int(input_data.get("frame_height", 720))
    grid_rows = int(input_data.get("grid_rows", 2))
    grid_cols = int(input_data.get("grid_cols", 2))
    confidence_threshold = float(input_data.get("confidence_threshold", 0.5))

    zones = get_zone_definitions(frame_width, frame_height, grid_rows, grid_cols)
    zone_counts = {str(zone["zone_id"]): 0 for zone in zones}

    for frame in frames:
        detections = frame.get("detections", [])

        for detection in detections:
            bbox = detection.get("bbox")
            confidence = float(detection.get("confidence", 1.0))

            if confidence < confidence_threshold:
                continue

            if not is_valid_bbox(bbox, frame_width, frame_height):
                continue

            center_x, center_y = bbox_center(bbox)
            zone_id = find_zone(center_x, center_y, zones)

            if zone_id is not None:
                zone_counts[zone_id] += 1

    densities = calculate_density(zone_counts)
    averages = calculate_average_count(zone_counts, len(frames))

    zones_output = [
        {
            "zone_id": zone_id,
            "person_count": count,
            "density": densities[zone_id],
            "average_count_per_frame": averages[zone_id],
            "density_level": classify_density(densities[zone_id]),
        }
        for zone_id, count in zone_counts.items()
    ]

    result = {
        "video_id": video_id,
        "zones": zones_output,
        "heatmap_data": build_heatmap_data(zones_output),
    }

    validate_output(result)
    return result


if __name__ == "__main__":
    sample_input = {
        "video_id": "match_01",
        "frame_width": 1280,
        "frame_height": 720,
        "grid_rows": 2,
        "grid_cols": 2,
        "confidence_threshold": 0.5,
        "frames": [
            {
                "frame_id": 1,
                "timestamp": 0.04,
                "person_count": 4,
                "detections": [
                    {"bbox": [100, 200, 180, 350], "confidence": 0.92},
                    {"bbox": [300, 220, 380, 370], "confidence": 0.89},
                    {"bbox": [700, 250, 780, 400], "confidence": 0.95},
                    {"bbox": [900, 300, 980, 450], "confidence": 0.87},
                ],
            },
            {
                "frame_id": 2,
                "timestamp": 0.08,
                "person_count": 3,
                "detections": [
                    {"bbox": [120, 240, 190, 360], "confidence": 0.91},
                    {"bbox": [720, 270, 800, 430], "confidence": 0.94},
                    {"bbox": [950, 360, 1040, 520], "confidence": 0.90},
                ],
            },
        ],
    }

    output = analyze_density(sample_input)

    os.makedirs("output", exist_ok=True)
    output_path = os.path.join("output", "density_summary.json")

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(output, file, indent=2)

    print(json.dumps(output, indent=2))
    print(f"\nSaved output to: {output_path}")