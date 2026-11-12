"""Shared integration service for fire and stampede detection."""

import os
from typing import Any

from fire_detection.main import process_video as process_fire
from stampede_detection.main import analyze_stampede

# Set CROWD_ENABLE_STAMPEDE=false to skip stampede detection (e.g. on machines
# without CUDA). Zones then report no stampede events.
ENABLE_STAMPEDE = os.environ.get("CROWD_ENABLE_STAMPEDE", "true").strip().lower() in {"1", "true", "yes", "on"}


def _normalize_stampede_event(
    event: dict[str, Any],
    camera_id: str,
    zone_id: str,
) -> dict[str, Any]:
    """
    Normalize a Stampede Detection event into the contract expected
    by Data Aggregation.

    Existing values from Stampede Detection are preserved where available.
    """

    detected = bool(
        event.get(
            "stampede_detected",
            event.get("detected", False),
        )
    )

    return {
        **event,
        "timestamp": event.get("timestamp", 0.0),
        "camera_id": event.get("camera_id", camera_id),
        "zone_id": event.get("zone_id", zone_id),
        "stampede_detected": detected,
        "confidence": event.get("confidence"),
        "severity": event.get(
            "severity",
            "WARNING" if detected else "NONE",
        ),
        "crowd_count": event.get("crowd_count"),
        "movement_direction": event.get("movement_direction"),
        "movement_speed": event.get("movement_speed"),
        "abnormal_movement": bool(
            event.get(
                "abnormal_movement",
                detected,
            )
        ),
    }


def process_safety_detection(
    video_data: dict,
    frame_data: dict,
    camera_id: str = "CAM_02",
    zone_id: str = "ZONE_B",
) -> dict:
    """
    Run Fire and Stampede Detection for the same video.

    Fire Detection uses frames already extracted by the crowd/video
    processing pipeline.

    Stampede Detection uses the original video because its current
    implementation performs its own consecutive-frame extraction.
    """

    video_id = video_data.get("video_id")

    if not video_id:
        raise ValueError("video_id is required for safety detection.")

    if not video_data.get("video_path"):
        raise ValueError("video_path is required for safety detection.")

    frames = frame_data.get("frames", [])

    if not isinstance(frames, list):
        raise TypeError("frame_data.frames must be a list.")

    # --------------------------------------------------
    # FIRE DETECTION
    # --------------------------------------------------

    fire_input = {
        "video_id": video_id,
        "video_path": video_data.get("video_path"),
        "frames": frames,
    }

    fire_result = process_fire(
        frame_metadata=fire_input,
        camera_id=camera_id,
        zone_id=zone_id,
    )

    # --------------------------------------------------
    # STAMPEDE DETECTION
    # --------------------------------------------------

    if ENABLE_STAMPEDE:
        stampede_result = analyze_stampede(
            input_source=video_data,
            video_id=video_id,
            camera_id=camera_id,
            zone_id=zone_id,
        )
    else:
        stampede_result = {"video_id": video_id, "events": []}

    events = stampede_result.get("events", [])

    if not isinstance(events, list):
        raise TypeError("Stampede Detection events must be a list.")

    normalized_events = [
        _normalize_stampede_event(
            event,
            camera_id=camera_id,
            zone_id=zone_id,
        )
        for event in events
        if isinstance(event, dict)
    ]

    normalized_stampede = {
        "video_id": stampede_result.get(
            "video_id",
            video_id,
        ),
        "detections": normalized_events,
    }

    return {
        "video_id": video_id,
        "fire": fire_result,
        "stampede": normalized_stampede,
    }
