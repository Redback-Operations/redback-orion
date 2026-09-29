"""Feature extraction helpers for crowd behaviour analytics."""

import os

# Trend classifier tuning (env-overridable).
_TREND_WARMUP = int(os.environ.get("CROWD_TREND_WARMUP", "3"))          # drop the first N detected frames (detector under-counts cold)
_TREND_THRESHOLD = float(os.environ.get("CROWD_TREND_THRESHOLD", "0.15"))  # relative change to call it increasing/dispersing
_TREND_MIN_SAMPLES = int(os.environ.get("CROWD_TREND_MIN_SAMPLES", "6"))   # fewer real detections than this -> "stable"


def extract_density_features(zones, heatmap):
    """Build behaviour features from zone density and heatmap availability."""
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


def classify_density_trend(
    frames,
    warmup_frames=_TREND_WARMUP,
    change_threshold=_TREND_THRESHOLD,
    min_samples=_TREND_MIN_SAMPLES,
):
    """Classify crowd state from the trajectory of per-frame person counts.

    Uses only frames where the detector actually ran (detected != False) so
    carried-forward counts don't flatten the signal, drops the first
    `warmup_frames` of those (the detector under-counts before it warms up),
    then compares the mean of the first third against the last third.

    Returns (state, delta) where state is one of "increasing_density",
    "dispersing", "stable" and delta is the relative change (last vs first).
    """
    counts = [f.get("person_count", 0) for f in frames if f.get("detected", True)]
    counts = counts[warmup_frames:]
    if len(counts) < max(min_samples, 2):
        return "stable", 0.0

    third = max(len(counts) // 3, 1)
    first_mean = sum(counts[:third]) / third
    last_mean = sum(counts[-third:]) / third
    delta = (last_mean - first_mean) / max(first_mean, 1.0)

    if delta >= change_threshold:
        return "increasing_density", round(delta, 4)
    if delta <= -change_threshold:
        return "dispersing", round(delta, 4)
    return "stable", round(delta, 4)


def classify_crowd_state(features):
    """Static score of *current* density level (not a trend). Kept as a
    secondary signal - classify_density_trend is what drives crowd_state now."""
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
