"""Service flow for density zoning and heatmap generation."""

from density_zoning.main import analyze_density
from heatmap.main import generate_heatmap


def process_analytics(data: dict):
    """Call task implementations for the analytics service."""
    density_result = analyze_density(data)
    heatmap_result = generate_heatmap(density_result)

    return {
        "video_id": data.get("video_id"),
        "zones": density_result.get("zones", []),
        "heatmap": heatmap_result.get("heatmap", heatmap_result),
    }
