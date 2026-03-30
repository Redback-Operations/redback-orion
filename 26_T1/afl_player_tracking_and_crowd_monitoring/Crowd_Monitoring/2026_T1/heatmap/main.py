"""Minimal entry point for the heatmap task."""

import json
import os
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np


def generate_heatmap(input_data: Dict) -> Dict:
    """Generate a basic heatmap image from zone density data."""

    video_id = input_data["video_id"]
    zones: List[Dict] = input_data["zones"]

    if not zones:
        raise ValueError("Zones list is empty.")

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    densities = [zone["density"] for zone in zones]
    zone_ids = [zone["zone_id"] for zone in zones]

    num_zones = len(zones)
    cols = int(np.ceil(np.sqrt(num_zones)))
    rows = int(np.ceil(num_zones / cols))

    heatmap_array = np.zeros((rows, cols))
    labels = [["" for _ in range(cols)] for _ in range(rows)]

    for index, zone in enumerate(zones):
        row = index // cols
        col = index % cols
        heatmap_array[row, col] = zone["density"]
        labels[row][col] = f"{zone['zone_id']}\nCount: {zone['person_count']}\nDensity: {zone['density']:.2f}"

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(heatmap_array, cmap="hot", interpolation="nearest")

    for row in range(rows):
        for col in range(cols):
            if labels[row][col]:
                ax.text(
                    col,
                    row,
                    labels[row][col],
                    ha="center",
                    va="center",
                    color="white",
                    fontsize=9,
                )

    ax.set_title(f"Heatmap for {video_id}")
    ax.set_xticks([])
    ax.set_yticks([])

    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Density")

    image_path = os.path.join(output_dir, f"heatmap_{video_id}.png")
    plt.tight_layout()
    plt.savefig(image_path, dpi=200)
    plt.close()

    return {
        "video_id": video_id,
        "heatmap": {
            "image_path": image_path
        }
    }


if __name__ == "__main__":
    sample_input = {
        "video_id": "match_01",
        "zones": [
            {"zone_id": "A1", "person_count": 8, "density": 0.72},
            {"zone_id": "A2", "person_count": 5, "density": 0.45},
            {"zone_id": "A3", "person_count": 10, "density": 0.88},
            {"zone_id": "A4", "person_count": 3, "density": 0.20},
        ],
    }

    result = generate_heatmap(sample_input)
    print(json.dumps(result, indent=2))