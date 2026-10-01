import json
import math
import random
from typing import Dict, List


def zone_name(row_index: int, col_index: int) -> str:
    """Convert row/col index into zone names like A1, B3, AA10."""
    letters = ""
    n = row_index
    while True:
        letters = chr(ord("A") + (n % 26)) + letters
        n = n // 26 - 1
        if n < 0:
            break
    return f"{letters}{col_index + 1}"


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def gaussian_hotspot(row: int, col: int, center_row: float, center_col: float, spread: float, amplitude: float) -> float:
    """Create a hotspot effect for density."""
    distance_sq = (row - center_row) ** 2 + (col - center_col) ** 2
    return amplitude * math.exp(-distance_sq / (2 * spread ** 2))


def generate_average_heatmap_data(
    video_id: str = "match_avg_01",
    rows: int = 10,
    cols: int = 10,
    num_frames: int = 30,
    base_density: float = 0.10,
    noise_level: float = 0.05,
    hotspots: List[Dict] = None,
    seed: int = 42
) -> Dict:
    """
    Generate realistic zone data where person_count is the average count per zone across frames.
    """
    random.seed(seed)

    if hotspots is None:
        hotspots = [
            {
                "center_row": rows / 2,
                "center_col": cols / 2,
                "spread": max(rows, cols) / 5,
                "amplitude": 0.75
            }
        ]

    zones = []

    for r in range(rows):
        for c in range(cols):
            base_zone_density = base_density

            for hotspot in hotspots:
                base_zone_density += gaussian_hotspot(
                    r,
                    c,
                    hotspot["center_row"],
                    hotspot["center_col"],
                    hotspot["spread"],
                    hotspot["amplitude"]
                )

            base_zone_density = clamp(base_zone_density)

            frame_counts = []
            for _ in range(num_frames):
                noisy_density = clamp(base_zone_density + random.uniform(-noise_level, noise_level))
                frame_count = max(0, round(noisy_density * 20 + random.uniform(-2, 2)))
                frame_counts.append(frame_count)

            avg_count = round(sum(frame_counts) / len(frame_counts))
            final_density = round(sum(frame_counts) / (len(frame_counts) * 20), 2)
            final_density = clamp(final_density)

            zones.append(
                {
                    "zone_id": zone_name(r, c),
                    "person_count": avg_count,
                    "density": round(final_density, 2)
                }
            )

    return {
        "video_id": video_id,
        "zones": zones
    }


def save_json(data: Dict, filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Saved: {filename}")


if __name__ == "__main__":
    data_10x10 = generate_average_heatmap_data(
        video_id="match_avg_10x10",
        rows=10,
        cols=10,
        num_frames=40,
        base_density=0.08,
        noise_level=0.04,
        hotspots=[
            {"center_row": 4, "center_col": 4, "spread": 2.0, "amplitude": 0.65},
            {"center_row": 7, "center_col": 7, "spread": 2.5, "amplitude": 0.55},
        ],
        seed=42
    )
    save_json(data_10x10, "heatmap_avg_10x10.json")

    data_20x20 = generate_average_heatmap_data(
        video_id="match_avg_20x20",
        rows=20,
        cols=20,
        num_frames=50,
        base_density=0.05,
        noise_level=0.03,
        hotspots=[
            {"center_row": 6, "center_col": 8, "spread": 3.5, "amplitude": 0.60},
            {"center_row": 14, "center_col": 12, "spread": 4.0, "amplitude": 0.75},
        ],
        seed=123
    )
    save_json(data_20x20, "heatmap_avg_20x20.json")