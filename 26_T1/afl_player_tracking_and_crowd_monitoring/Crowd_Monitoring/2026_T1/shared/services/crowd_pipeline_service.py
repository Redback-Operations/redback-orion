"""End-to-end service flow for the full crowd monitoring pipeline."""

from pathlib import Path

import matplotlib.pyplot as plt

from .crowd_analytics_service import process_analytics
from .crowd_detection_service import process_detection
from crowd_allocation_risk_zone.main import assess_risk
from crowd_behaviour_analytics.main import analyze_behaviour

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _safe_round(value, digits=2):
    if value is None:
        return None
    return round(float(value), digits)


def _build_summary(detection_result: dict, behaviour_result: dict, risk_result: dict, analytics_result: dict) -> dict:
    frames = detection_result.get("frames", [])
    counts = [frame.get("person_count", 0) for frame in frames]
    zone_densities = analytics_result.get("zones", [])
    flagged_zones = [zone for zone in risk_result.get("zones", []) if zone.get("flagged")]

    highest_density_zone = max(zone_densities, key=lambda zone: zone.get("density", 0), default=None)
    highest_risk_zone = flagged_zones[0] if flagged_zones else None

    return {
        "total_frames_processed": len(frames),
        "peak_person_count": max(counts, default=0),
        "crowd_state": behaviour_result.get("crowd_state", "unknown"),
        "highest_density_zone": highest_density_zone.get("zone_id") if highest_density_zone else None,
        "highest_risk_zone": highest_risk_zone.get("zone_id") if highest_risk_zone else None,
    }


def _build_peak_crowd_frame(detection_result: dict) -> dict:
    frames = detection_result.get("frames", [])
    peak_frame = max(frames, key=lambda frame: frame.get("person_count", 0), default=None)
    if not peak_frame:
        return {}

    return {
        "frame_id": peak_frame.get("frame_id"),
        "timestamp": peak_frame.get("timestamp"),
        "person_count": peak_frame.get("person_count", 0),
        "people_annotated_frame_path": peak_frame.get("people_annotated_frame_path"),
    }


def _build_anomaly_visual(behaviour_result: dict) -> dict:
    artifact_paths = behaviour_result.get("artifact_paths") or []
    event_flags = behaviour_result.get("event_flags") or []
    activity_series = behaviour_result.get("frame_movement_summary") or behaviour_result.get("frame_activity_series", [])
    motion_artifacts = [
        path for path in artifact_paths
        if "motion_frame_" in path.replace("\\", "/")
    ]
    artifact_by_frame = {}
    for path in motion_artifacts:
        normalized_path = path.replace("\\", "/")
        frame_name = normalized_path.rsplit("/", 1)[-1]
        frame_token = frame_name.replace("motion_frame_", "").replace(".jpg", "")
        try:
            artifact_by_frame[int(frame_token)] = path
        except ValueError:
            continue

    preferred_frame = max(
        activity_series,
        key=lambda entry: (
            entry.get("walking_count", 0),
            entry.get("running_count", 0),
            entry.get("active_count", 0),
        ),
        default=None,
    )
    selected_path = None
    if preferred_frame:
        selected_path = artifact_by_frame.get(preferred_frame.get("frame_id"))
    if not selected_path:
        selected_path = motion_artifacts[0] if motion_artifacts else (artifact_paths[-1] if artifact_paths else None)
    if not selected_path:
        return {}

    if preferred_frame and preferred_frame.get("running_count", 0) > 0:
        event_type = "running_activity"
    elif preferred_frame and preferred_frame.get("walking_count", 0) > 0:
        event_type = "walking_or_running_activity"
    else:
        event_type = event_flags[0] if event_flags else "movement_alert"

    return {
        "event_type": event_type,
        "image_path": selected_path,
    }


def _build_time_series_chart(detection_result: dict, behaviour_result: dict, video_id: str | None) -> dict:
    frames = detection_result.get("frames", [])
    if not frames:
        return {}

    person_timestamps = [frame.get("timestamp", 0.0) for frame in frames]
    person_counts = [frame.get("person_count", 0) for frame in frames]

    output_dir = PROJECT_ROOT / "analytics_output" / "charts"
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_video_id = video_id or detection_result.get("video_id") or "unknown_video"
    output_path = output_dir / f"{safe_video_id}_crowd_activity_chart.png"

    figure, axis = plt.subplots(figsize=(10, 4.5))
    axis.plot(person_timestamps, person_counts, color="#1f77b4", linewidth=2.4)
    axis.set_xlabel("Time (s)")
    axis.set_ylabel("Person count")
    axis.grid(True, linestyle="--", alpha=0.35)

    figure.suptitle("Person Count Over Time")
    figure.tight_layout()
    figure.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(figure)

    return {
        "image_path": str(output_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    }


def _build_density_extremes(analytics_result: dict, risk_result: dict) -> dict:
    risk_by_zone = {
        zone.get("zone_id"): zone
        for zone in risk_result.get("zones", [])
    }

    zone_insights = []
    for zone in analytics_result.get("zones", []):
        risk = risk_by_zone.get(zone.get("zone_id"), {})
        zone_insights.append({
            "zone_id": zone.get("zone_id"),
            "person_count": zone.get("person_count", 0),
            "density": _safe_round(zone.get("density", 0.0), 4),
            "risk_level": risk.get("risk_level", "unknown"),
            "flagged": risk.get("flagged", False),
        })

    if not zone_insights:
        return {
            "highest_density_zone": {},
            "lowest_density_zone": {},
        }

    highest_density_zone = max(zone_insights, key=lambda zone: zone.get("density", 0.0))
    lowest_density_zone = min(zone_insights, key=lambda zone: zone.get("density", 0.0))
    return {
        "highest_density_zone": highest_density_zone,
        "lowest_density_zone": lowest_density_zone,
    }


def process_crowd_detection(data: dict):
    """Run detection, analytics, and intelligence as one frontend-facing flow."""
    detection_result = process_detection(data)
    analytics_result = process_analytics(detection_result)

    intelligence_input = {
        "video_id": data.get("video_id"),
        "zones": analytics_result.get("zones", []),
        "heatmap": analytics_result.get("heatmap", {}),
        "frames": detection_result.get("frames", []),
    }
    behaviour_result = analyze_behaviour(intelligence_input)
    risk_result = assess_risk(behaviour_result)

    return {
        "video_id": data.get("video_id"),
        "summary": _build_summary(detection_result, behaviour_result, risk_result, analytics_result),
        "peak_crowd_frame": _build_peak_crowd_frame(detection_result),
        "anomaly_visual": _build_anomaly_visual(behaviour_result),
        "heatmap": analytics_result.get("heatmap", {}),
        "time_series_chart": _build_time_series_chart(detection_result, behaviour_result, data.get("video_id")),
        "density_extremes": _build_density_extremes(analytics_result, risk_result),
    }
