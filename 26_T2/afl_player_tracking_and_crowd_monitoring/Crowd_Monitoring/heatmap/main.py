"""Heatmap task implementation with validation and stadium-style visualization."""

import json
import math
import os
from typing import Dict, List, Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
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
            raise ValueError(f"Each zone must have a valid 'zone_id'.")

        person_count = zone.get("person_count")
        if not isinstance(person_count, (int, float)):
            raise ValueError(f"Person count for zone '{zone_id}' must be numeric.")

        density = zone.get("density")
        if not isinstance(density, (int, float)):
            raise ValueError(f"Density for zone '{zone_id}' must be numeric.")


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


def build_video_style_input(video_id: str = "match_02") -> Dict:
    """
    Create a higher-grid stadium-style layout that roughly matches the shared frame.
    """
    rows, cols = 8, 12
    zones = []

    for r in range(rows):
        for c in range(cols):
            density = 0.06

            if r <= 1:
                density += 0.02 + 0.01 * c / cols

            if 2 <= r <= 4:
                density += 0.10 + 0.08 * (c / cols)

            if r >= 5:
                density += 0.14 + 0.10 * (c / cols)

            hotspot1 = math.exp(-(((r - 5.6) ** 2) / 2.8 + ((c - 7.0) ** 2) / 5.0))
            density += 0.42 * hotspot1

            hotspot2 = math.exp(-(((r - 3.8) ** 2) / 2.0 + ((c - 3.2) ** 2) / 3.5))
            density += 0.18 * hotspot2

            density = max(0.0, min(1.0, density))
            person_count = int(round(density * 20))

            zones.append(
                {
                    "zone_id": zone_name(r, c),
                    "person_count": person_count,
                    "density": round(density, 2),
                }
            )

    return {"video_id": video_id, "zones": zones}


def compute_grid_shape(num_zones: int) -> Tuple[int, int]:
    cols = max(8, int(math.ceil(math.sqrt(num_zones * 1.6))))
    rows = int(math.ceil(num_zones / cols))
    return rows, cols


def generate_heatmap(input_data: Dict) -> Dict:
    """Generate a stadium-style heatmap image from zone density data."""
    validate_input(input_data)

    video_id = input_data["video_id"]
    zones: List[Dict] = input_data["zones"]

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    num_zones = len(zones)
    rows, cols = compute_grid_shape(num_zones)

    fig = plt.figure(figsize=(14, 10), facecolor="#0b1220")
    ax = plt.axes([0.03, 0.10, 0.94, 0.80])
    ax.set_facecolor("#071224")
    ax.set_xlim(-1.15, 1.15)
    ax.set_ylim(-0.92, 0.92)
    ax.axis("off")

    outer = patches.Ellipse(
        (0, 0),
        width=1.85,
        height=1.42,
        facecolor="#0a1b34",
        edgecolor="#183b69",
        linewidth=2.5,
        zorder=1,
    )
    ax.add_patch(outer)

    pitch = patches.FancyBboxPatch(
        (-0.42, -0.23),
        0.84,
        0.46,
        boxstyle="round,pad=0.01,rounding_size=0.02",
        facecolor="#1f8f43",
        edgecolor="#2c3f66",
        linewidth=6,
        zorder=5,
    )
    ax.add_patch(pitch)

    ax.plot([0, 0], [-0.21, 0.21], color="white", alpha=0.55, lw=1.6, zorder=6)
    center_circle = patches.Circle((0, 0), 0.07, fill=False, ec="white", alpha=0.5, lw=1.3, zorder=6)
    ax.add_patch(center_circle)
    ax.plot(0, 0, "wo", ms=4, alpha=0.5, zorder=6)

    for x0, sign in [(-0.42, 1), (0.33, -1)]:
        ax.add_patch(
            patches.Rectangle(
                (x0, -0.09),
                0.09,
                0.18,
                fill=False,
                ec="white",
                alpha=0.45,
                lw=1.2,
                zorder=6,
            )
        )
        ax.add_patch(
            patches.Rectangle(
                (x0, -0.14),
                0.16 * sign,
                0.28,
                fill=False,
                ec="white",
                alpha=0.45,
                lw=1.2,
                zorder=6,
            )
        )

    ax.text(0, 0.80, "NORTH STAND", ha="center", va="center", fontsize=24, color="#7f94bd", alpha=0.95)
    ax.text(0, -0.82, "SOUTH STAND", ha="center", va="center", fontsize=24, color="#7f94bd", alpha=0.95)
    ax.text(-0.98, 0.00, "WEST", ha="center", va="center", fontsize=20, color="#7f94bd", alpha=0.95)
    ax.text(0.98, 0.00, "EAST", ha="center", va="center", fontsize=20, color="#7f94bd", alpha=0.95)

    a_outer, b_outer = 0.92, 0.70
    a_inner, b_inner = 0.50, 0.33
    cmap = plt.cm.turbo

    for i, zone in enumerate(zones):
        r_idx = i // cols
        c_idx = i % cols

        density = float(zone["density"])
        density = max(0.0, min(1.0, density))

        t_r0 = r_idx / rows
        t_r1 = (r_idx + 1) / rows

        theta0 = math.pi - (c_idx / cols) * 2 * math.pi
        theta1 = math.pi - ((c_idx + 1) / cols) * 2 * math.pi

        n_theta = 18
        n_rad = 3

        xs = []
        ys = []

        for rr in np.linspace(t_r0, t_r1, n_rad):
            a = a_inner + rr * (a_outer - a_inner)
            b = b_inner + rr * (b_outer - b_inner)

            for th in np.linspace(theta0, theta1, n_theta):
                x = a * math.cos(th)
                y = b * math.sin(th)

                if abs(x) < 0.47 and abs(y) < 0.26:
                    continue

                xs.append(x)
                ys.append(y)

        if xs:
            ax.scatter(
                xs,
                ys,
                s=420,
                c=[density] * len(xs),
                cmap=cmap,
                vmin=0,
                vmax=1,
                alpha=0.62,
                linewidths=0,
                zorder=2,
            )

    for rr in np.linspace(0.18, 1.0, 5):
        a = a_inner + rr * (a_outer - a_inner)
        b = b_inner + rr * (b_outer - b_inner)
        t = np.linspace(0, 2 * np.pi, 400)
        x = a * np.cos(t)
        y = b * np.sin(t)
        mask = ~((np.abs(x) < 0.47) & (np.abs(y) < 0.26))
        ax.plot(x[mask], y[mask], color="#2c4b76", lw=1.0, alpha=0.7, zorder=3)

    for cc in range(cols):
        th = math.pi - (cc / cols) * 2 * math.pi
        x1 = a_inner * math.cos(th)
        y1 = b_inner * math.sin(th)
        x2 = a_outer * math.cos(th)
        y2 = b_outer * math.sin(th)
        if not (abs(x1) < 0.47 and abs(y1) < 0.26):
            ax.plot([x1, x2], [y1, y2], color="#29476f", lw=0.9, alpha=0.7, zorder=3)

    ax.text(
        0,
        0.96,
        f"CROWD HEATMAP  •  {video_id.upper()}",
        ha="center",
        va="top",
        fontsize=30,
        color="#f8fafc",
        fontweight="bold",
        zorder=10,
    )

    fig.text(
        0.055,
        0.935,
        "Analytics View • Redback Orion Crowd Monitoring",
        color="#8aa0c8",
        fontsize=11,
        ha="left",
    )

    gradient = np.linspace(0, 1, 256).reshape(1, -1)
    cax = fig.add_axes([0.10, 0.04, 0.80, 0.02])
    cax.imshow(gradient, aspect="auto", cmap=cmap, extent=[0, 1, 0, 1])
    cax.set_xticks([])
    cax.set_yticks([])
    for spine in cax.spines.values():
        spine.set_visible(False)

    fig.text(0.055, 0.05, "Low", color="#f8fafc", fontsize=20, va="center")
    fig.text(0.915, 0.05, "High", color="#f8fafc", fontsize=20, va="center")

    image_path = os.path.join(output_dir, f"heatmap_{video_id}.png")
    plt.savefig(image_path, dpi=240, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)

    return {
        "video_id": video_id,
        "heatmap": {
            "image_path": image_path
        }
    }


if __name__ == "__main__":
    video_based_input = build_video_style_input("match_02")
    result = generate_heatmap(video_based_input)
    print(json.dumps(result, indent=2))