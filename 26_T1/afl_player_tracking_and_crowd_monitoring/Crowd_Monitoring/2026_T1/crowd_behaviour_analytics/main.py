"""Minimal entry point for the crowd behaviour analytics task."""


def _extract_features(zones, heatmap):
    """Build simple behaviour features from zone density and heatmap availability."""
    if not zones:
        return {
            "avg_density": 0.0,
            "max_density": 0.0,
            "density_variation": 0.0,
            "total_people": 0,
            "hotspot_count": 0,
            "heatmap_available": False,
        }

    densities = [zone.get("density", 0.0) for zone in zones]
    avg_density = sum(densities) / len(densities)
    max_density = max(densities)
    min_density = min(densities)
    total_people = sum(zone.get("person_count", 0) for zone in zones)
    hotspot_count = sum(1 for density in densities if density >= 0.6)

    return {
        "avg_density": avg_density,
        "max_density": max_density,
        "density_variation": max_density - min_density,
        "total_people": total_people,
        "hotspot_count": hotspot_count,
        "heatmap_available": bool(heatmap and heatmap.get("image_path")),
    }


def _classify_crowd_state(features):
    """AI-style scoring scaffold that can later be replaced with a trained model."""
    score = 0.0

    score += features["avg_density"] * 0.35
    score += features["max_density"] * 0.35
    score += features["density_variation"] * 0.15
    score += min(features["hotspot_count"] / 3, 1.0) * 0.10
    score += min(features["total_people"] / 30, 1.0) * 0.05

    if not features["heatmap_available"]:
        score -= 0.05

    if score >= 0.60:
        return "increasing_density"
    if score <= 0.20:
        return "dispersing"
    return "stable"


def analyze_behaviour(input_data):
    """Analyze crowd behaviour over time and produce summary outputs."""
    zones = input_data.get("zones", [])
    heatmap = input_data.get("heatmap", {})
    video_id = input_data.get("video_id")

    features = _extract_features(zones, heatmap)
    crowd_state = _classify_crowd_state(features)

    return {
        "video_id": video_id,
        "crowd_state": crowd_state,
        "zones": zones,
    }


if __name__ == "__main__":
    # Add a simple local test call here when implementation starts.
    pass
