"""Event-detection helpers for crowd behaviour analytics."""


def detect_behaviour_events(
    features,
    vision_features,
    zones,
    tracking_summary=None,
    anomaly_summary=None,
):
    """Generate event flags using density patterns and motion cues."""
    event_flags = []
    tracking_summary = tracking_summary or {}
    anomaly_summary = anomaly_summary or {}

    if features["max_density"] >= 0.80 or features["hotspot_count"] >= 2:
        event_flags.append("overcrowding_spike")

    if features["density_variation"] >= 0.35:
        event_flags.append("sudden_gathering")

    if features["avg_density"] <= 0.20 and zones:
        event_flags.append("crowd_dispersing")

    if anomaly_summary.get("running_track_ids"):
        event_flags.append("running_detection")
    elif tracking_summary.get("running_track_count", 0) > 0:
        event_flags.append("running_detection")

    if tracking_summary.get("walking_track_count", 0) > 0:
        event_flags.append("walking_detection")

    if tracking_summary.get("stationary_track_count", 0) > 0:
        event_flags.append("stationary_detection")

    if vision_features["vision_enabled"] and vision_features["reverse_flow_ratio"] >= 0.30:
        event_flags.append("reverse_flow")

    if (
        features["avg_density"] >= 0.60
        and vision_features["vision_enabled"]
        and vision_features["avg_motion_magnitude"] >= 0.80
    ):
        event_flags.append("crowd_surge")

    if anomaly_summary.get("anomaly_count", 0) > 0:
        event_flags.append("motion_anomaly")

    return event_flags
