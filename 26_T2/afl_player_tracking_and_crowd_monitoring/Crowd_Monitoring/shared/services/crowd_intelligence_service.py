"""Service flow for behaviour analytics and risk assessment."""

from crowd_allocation_risk_zone.main import assess_risk
from crowd_behaviour_analytics.main import analyze_behaviour


def process_intelligence(data: dict):
    """Call task implementations for the intelligence service."""
    behaviour_result = analyze_behaviour(data)
    risk_result = assess_risk(behaviour_result)

    return {
        "video_id": data.get("video_id"),
        "crowd_state": behaviour_result.get("crowd_state"),
        "zones": risk_result.get("zones", []),
        "recommendations": risk_result.get("recommendations", []),
        "event_flags": behaviour_result.get("event_flags", []),
        "artifact_paths": behaviour_result.get("artifact_paths", []),
        "vision_metrics": behaviour_result.get("vision_metrics"),
    }
