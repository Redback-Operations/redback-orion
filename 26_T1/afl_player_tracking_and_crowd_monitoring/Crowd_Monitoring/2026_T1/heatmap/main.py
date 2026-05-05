"""Heatmap task implementation with validation and adaptive visualization."""

import json
import os
from typing import Dict, List

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def validate_input(input_data: Dict) -> None:
    """Validate the input JSON structure."""
    if not isinstance(input_data, dict):
        raise ValueError("Input must be a dictionary.")

    video_id = input_data.get("video_id")
    if not video_id or not isinstance(video_id, str):
        raise ValueError("Missing or empty 'video_id'.")

    zones = input_data.get("zones")
    if not isinstance(zones, list) or len(zones) == 0:
        raise ValueError("Missing or empty 'zones' list.")

    for zone in zones:
        if not isinstance(zone, dict):
            raise ValueError("Each zone must be a dictionary.")

        zone_id = zone.get("zone_id")
        if not zone_id or not isinstance(zone_id, str):
            raise ValueError("Each zone must have a valid 'zone_id'.")

        person_count = zone.get("person_count")
        if not isinstance(person_count, (int, float)):
            raise ValueError(f"Person count for zone '{zone_id}' must be numeric.")

        density = zone.get("density")
        if not isinstance(density, (int, float)):
            raise ValueError(f"Density for zone '{zone_id}' must be numeric.")


def get_text_label(zone_id: str, person_count: int, density: float, num_zones: int) -> str:
    """Return adaptive label text based on heatmap size."""
    if num_zones <= 25:
        return f"{zone_id}\nCount: {person_count}\nDensity: {density:.2f}"
    elif num_zones <= 100:
        return f"{zone_id}\n{density:.2f}"
    elif num_zones <= 225:
        return f"{zone_id}"
    else:
        return ""


def get_font_size(num_zones: int) -> int:
    """Return adaptive font size based on heatmap size."""
    if num_zones <= 25:
        return 10
    elif num_zones <= 100:
        return 7
    elif num_zones <= 225:
        return 5
    else:
        return 0


def generate_heatmap(input_data: Dict) -> Dict:
    """Generate a readable heatmap image from zone density data."""

    validate_input(input_data)

    video_id = input_data["video_id"]
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

        density = float(zone.get("density", 0.0))
        density = max(0.0, min(1.0, density))

        person_count = int(zone.get("person_count", 0))
        zone_id = zone.get("zone_id", f"Z{index + 1}")

        heatmap_array[row, col] = density
        labels[row][col] = get_text_label(zone_id, person_count, density, num_zones)

    # Dynamic figure size
    fig_width = max(8, cols * 1.2)
    fig_height = max(6, rows * 1.0)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    cmap = plt.cm.YlOrRd.copy()
    cmap.set_bad(color="lightgrey")

    im = ax.imshow(
        heatmap_array,
        cmap=cmap,
        interpolation="nearest",
        vmin=0,
        vmax=1
    )

    font_size = get_font_size(num_zones)

    for row in range(rows):
        for col in range(cols):
            if labels[row][col] and font_size > 0:
                cell_value = heatmap_array[row, col]

                if np.isnan(cell_value):
                    text_color = "black"
                else:
                    text_color = "black" if cell_value <= 0.35 else "white"

                ax.text(
                    col,
                    row,
                    labels[row][col],
                    ha="center",
                    va="center",
                    color=text_color,
                    fontsize=font_size,
                    fontweight="bold",
                )

    ax.set_title(f"Heatmap for {video_id}", fontsize=18, fontweight="bold")
    ax.set_xticks(np.arange(-0.5, cols, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, rows, 1), minor=True)
    ax.grid(which="minor", color="black", linestyle="-", linewidth=1.0)
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


def run_test_case(name: str, input_data: Dict) -> None:
    print(f"\nRunning: {name}")
    try:
        result = generate_heatmap(input_data)
        print("PASS")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print("FAIL")
        print(str(e))


if __name__ == "__main__":
    small_valid = {
        "video_id": "match_small",
        "zones": [
            {"zone_id": "A1", "person_count": 5, "density": 0.25},
            {"zone_id": "A2", "person_count": 7, "density": 0.45},
            {"zone_id": "A3", "person_count": 10, "density": 0.70},
            {"zone_id": "A4", "person_count": 4, "density": 0.20},
        ],
    }

    with open("heatmap_avg_10x10.json", "r", encoding="utf-8") as f:
        medium_valid = json.load(f)

    with open("heatmap_avg_20x20.json", "r", encoding="utf-8") as f:
        large_valid = json.load(f)

    invalid_missing_video = {
        "zones": [
            {"zone_id": "A1", "person_count": 5, "density": 0.4}
        ]
    }

    invalid_bad_density = {
        "video_id": "bad_match",
        "zones": [
            {"zone_id": "A1", "person_count": 5, "density": "wrong"}
        ]
    }

    run_test_case("Small valid input", small_valid)
    run_test_case("Medium valid input", medium_valid)
    run_test_case("Large valid input", large_valid)
    run_test_case("Invalid input - missing video_id", invalid_missing_video)
    run_test_case("Invalid input - bad density", invalid_bad_density)