"""Aggregate and export Orion stadium-monitoring results."""

from __future__ import annotations

import copy
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _get_detections(
    data: dict[str, Any],
    source_name: str,
) -> list[dict[str, Any]]:
    """Validate and return a service's detection list."""

    detections = data.get("detections", [])

    if not isinstance(detections, list):
        raise TypeError(f"{source_name}.detections must be a list.")

    for detection in detections:
        if not isinstance(detection, dict):
            raise TypeError(
                f"Each {source_name} detection must be an object."
            )

        if not detection.get("zone_id"):
            raise ValueError(
                f"Each {source_name} detection must include zone_id."
            )

    return detections


def _latest_detection_by_zone(
    detections: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Keep the most recent detection for each stadium zone."""

    latest: dict[str, dict[str, Any]] = {}

    for detection in detections:
        zone_id = str(detection["zone_id"])
        timestamp = float(detection.get("timestamp", 0.0))
        previous = latest.get(zone_id)

        if previous is None or timestamp >= float(
            previous.get("timestamp", 0.0)
        ):
            latest[zone_id] = detection

    return latest


def _get_video_id(
    crowd_data: dict[str, Any],
    fire_data: dict[str, Any],
    stampede_data: dict[str, Any],
) -> str:
    """Confirm that all supplied results refer to the same video."""

    video_ids = {
        str(data["video_id"])
        for data in (crowd_data, fire_data, stampede_data)
        if data.get("video_id")
    }

    if not video_ids:
        raise ValueError("At least one input must include video_id.")

    if len(video_ids) > 1:
        raise ValueError("All inputs must refer to the same video_id.")

    return next(iter(video_ids))


def _validate_crowd_result(crowd_data: dict[str, Any]) -> None:
    """Validate the current aggregated Crowd Detection contract."""

    required_sections = (
        "summary",
        "peak_crowd_frame",
        "anomaly_visual",
        "heatmap",
        "time_series_chart",
        "density_extremes",
    )

    for section in required_sections:
        if not isinstance(crowd_data.get(section), dict):
            raise ValueError(
                f"crowd_data.{section} must be an object."
            )


def _calculate_status(
    fire: dict[str, Any],
    stampede: dict[str, Any],
) -> str:
    """Calculate zone status from confirmed safety detections."""

    fire_detected = bool(fire.get("fire_detected", False))
    stampede_detected = bool(
        stampede.get("stampede_detected", False)
    )

    if not fire_detected and not stampede_detected:
        return "NORMAL"

    severities = {
        str(fire.get("severity", "NONE")).upper(),
        str(stampede.get("severity", "NONE")).upper(),
    }

    if severities & {"HIGH", "CRITICAL"}:
        return "CRITICAL"

    return "WARNING"


def _build_zone_data(
    fire: dict[str, Any],
    stampede: dict[str, Any],
) -> dict[str, Any]:
    """Build the frontend-friendly values for one stadium zone."""

    return {
        "fire": bool(fire.get("fire_detected", False)),
        "smoke": bool(fire.get("smoke_detected", False)),
        "fire_confidence": fire.get("confidence"),
        "fire_severity": fire.get("severity", "NONE"),
        "stampede": bool(
            stampede.get("stampede_detected", False)
        ),
        "stampede_confidence": stampede.get("confidence"),
        "stampede_severity": stampede.get("severity", "NONE"),
        "crowd_count": stampede.get("crowd_count"),
        "movement_direction": stampede.get("movement_direction"),
        "movement_speed": stampede.get("movement_speed"),
        "abnormal_movement": bool(
            stampede.get("abnormal_movement", False)
        ),
        "status": _calculate_status(fire, stampede),
    }


def aggregate_stadium_data(
    crowd_data: dict[str, Any],
    fire_data: dict[str, Any],
    stampede_data: dict[str, Any],
    stadium_id: str,
) -> dict[str, Any]:
    """Combine crowd, fire and stampede results into unified JSON."""

    if not stadium_id:
        raise ValueError("stadium_id is required.")

    _validate_crowd_result(crowd_data)

    video_id = _get_video_id(
        crowd_data,
        fire_data,
        stampede_data,
    )

    fire_by_zone = _latest_detection_by_zone(
        _get_detections(fire_data, "fire_data")
    )
    stampede_by_zone = _latest_detection_by_zone(
        _get_detections(stampede_data, "stampede_data")
    )

    zone_ids = sorted(set(fire_by_zone) | set(stampede_by_zone))
    zones = {
        zone_id: _build_zone_data(
            fire_by_zone.get(zone_id, {}),
            stampede_by_zone.get(zone_id, {}),
        )
        for zone_id in zone_ids
    }

    crowd = copy.deepcopy(crowd_data)
    crowd.pop("video_id", None)

    timestamp = (
        datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )

    return {
        "stadium_id": stadium_id,
        "video_id": video_id,
        "timestamp": timestamp,
        "crowd": crowd,
        "zones": zones,
    }


def export_results(
    input_data: dict[str, Any],
    output_dir: str | Path | None = None,
) -> dict[str, str]:
    """Export unified monitoring data as JSON and CSV files."""

    zones = input_data.get("zones")

    if not isinstance(zones, dict):
        raise ValueError("input_data.zones must be an object.")

    destination = (
        Path(output_dir)
        if output_dir is not None
        else Path(__file__).resolve().parent / "output"
    )
    destination.mkdir(parents=True, exist_ok=True)

    video_id = str(input_data.get("video_id", "unknown_video"))
    json_path = destination / f"{video_id}_monitoring.json"
    csv_path = destination / f"{video_id}_zones.csv"

    with json_path.open("w", encoding="utf-8") as json_file:
        json.dump(input_data, json_file, indent=2)

    summary = input_data.get("crowd", {}).get("summary", {})
    zone_fields = [
        "fire",
        "smoke",
        "fire_confidence",
        "fire_severity",
        "stampede",
        "stampede_confidence",
        "stampede_severity",
        "crowd_count",
        "movement_direction",
        "movement_speed",
        "abnormal_movement",
        "status",
    ]
    fieldnames = [
        "stadium_id",
        "video_id",
        "timestamp",
        "total_frames_processed",
        "peak_person_count",
        "crowd_state",
        "highest_density_zone",
        "highest_risk_zone",
        "zone_id",
        *zone_fields,
    ]

    with csv_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        common = {
            "stadium_id": input_data.get("stadium_id"),
            "video_id": video_id,
            "timestamp": input_data.get("timestamp"),
            "total_frames_processed": summary.get(
                "total_frames_processed"
            ),
            "peak_person_count": summary.get("peak_person_count"),
            "crowd_state": summary.get("crowd_state"),
            "highest_density_zone": summary.get(
                "highest_density_zone"
            ),
            "highest_risk_zone": summary.get("highest_risk_zone"),
        }

        if zones:
            for zone_id, zone in zones.items():
                writer.writerow(
                    {
                        **common,
                        "zone_id": zone_id,
                        **{field: zone.get(field) for field in zone_fields},
                    }
                )
        else:
            writer.writerow({**common, "zone_id": ""})

    return {
        "json_path": str(json_path),
        "csv_path": str(csv_path),
    }
