"""Minimal entry point for the heatmap task."""

import json
import os
from typing import Dict, List

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def validate_input(input_data: Dict) -> None:
    """Validate incoming heatmap input data."""
    if not isinstance(input_data, dict):
        raise ValueError("Input data must be a dictionary.")

    if "video_id" not in input_data or not input_data["video_id"]:
        raise ValueError("Missing or empty 'video_id'.")

    if "zones" not in input_data:
        raise ValueError("Missing 'zones' field.")

    if not isinstance(input_data["zones"], list):
        raise ValueError("'zones' must be a list.")

    if len(input_data["zones"]) == 0:
        raise ValueError("'zones' list cannot be empty.")

    required_zone_fields = {"zone_id", "person_count", "density"}

    for index, zone in enumerate(input_data["zones"]):
        if not isinstance(zone, dict):
            raise ValueError(f"Zone at index {index} must be a dictionary.")

        missing_fields = required_zone_fields - zone.keys()
        if missing_fields:
            raise ValueError(
                f"Zone at index {index} is missing fields: {', '.join(sorted(missing_fields))}"
            )


def generate_heatmap(input_data: Dict) -> Dict:
    """Generate a validated and schema-compliant heatmap image from zone density data."""
    validate_input(input_data)

    video_id = str(input_data["video_id"])
    zones: List[Dict] = input_data["zones"]

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    num_zones = len(zones)
    cols = int(np.ceil(np.sqrt(num_zones)))
    rows = int(np.ceil(num_zones / cols))

    heatmap_array = np.full((rows, cols), np.nan)
    labels = [["" for _ in range(cols)] for _ in range(rows)]

    for index, zone in enumerate(zones):
        row = index // cols
        col = index % cols

        zone_id = str(zone["zone_id"])

        try:
            density = float(zone["density"])
        except (TypeError, ValueError):
            raise ValueError(f"Density for zone '{zone_id}' must be numeric.")

        density = max(0.0, min(1.0, density))

        try:
            person_count = int(zone["person_count"])
        except (TypeError, ValueError):
            raise ValueError(f"Person count for zone '{zone_id}' must be an integer.")

        heatmap_array[row, col] = density
        labels[row][col] = (
            f"{zone_id}\n"
            f"Count: {person_count}\n"
            f"Density: {density:.2f}"
        )

    fig, ax = plt.subplots(figsize=(8, 6))

    cmap = plt.cm.YlOrRd.copy()
    cmap.set_bad(color="lightgrey")

    im = ax.imshow(
        heatmap_array,
        cmap=cmap,
        interpolation="nearest",
        vmin=0,
        vmax=1,
    )

    for row in range(rows):
        for col in range(cols):
            if labels[row][col]:
                cell_value = heatmap_array[row, col]

                if np.isnan(cell_value):
                    text_color = "black"
                else:
                    text_color = "black" if cell_value <= 0.35 or cell_value >= 0.65 else "white"

                ax.text(
                    col,
                    row,
                    labels[row][col],
                    ha="center",
                    va="center",
                    color=text_color,
                    fontsize=10,
                    fontweight="bold",
                )

    ax.set_title(f"Heatmap for {video_id}", fontsize=16, fontweight="bold")
    ax.set_xticks(np.arange(-0.5, cols, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, rows, 1), minor=True)
    ax.grid(which="minor", color="black", linestyle="-", linewidth=1.5)
    ax.tick_params(which="both", bottom=False, left=False, labelbottom=False, labelleft=False)

    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Density", fontsize=12)

    image_path = os.path.join(output_dir, f"heatmap_{video_id}.png")
    plt.tight_layout()
    plt.savefig(image_path, dpi=200, bbox_inches="tight")
    plt.close()

    return {
        "video_id": video_id,
        "heatmap": {
            "image_path": image_path
        }
    }


if __name__ == "__main__":
    sample_input = {
        "video_id": "match_02",
        "zones": [
            {"zone_id": "A1", "person_count": 2, "density": 0.10},
            {"zone_id": "A2", "person_count": 6, "density": 0.55},
            {"zone_id": "A3", "person_count": 12, "density": 0.95},
            {"zone_id": "A4", "person_count": 4, "density": 0.30},
        ],
    }

    result = generate_heatmap(sample_input)
    print(json.dumps(result, indent=2))
