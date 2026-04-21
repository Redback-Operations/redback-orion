"""End-to-end service flow for the full crowd monitoring pipeline."""

from .crowd_analytics_service import process_analytics
from .crowd_detection_service import process_detection
from crowd_allocation_risk_zone.main import assess_risk
from crowd_behaviour_analytics.main import analyze_behaviour


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
        "crowd_detection": detection_result,
        "density_zoning": analytics_result.get("zones", []),
        "heatmap": analytics_result.get("heatmap", {}),
        "crowd_behaviour_analytics": behaviour_result,
        "crowd_allocation_risk_zone": risk_result,
    }
