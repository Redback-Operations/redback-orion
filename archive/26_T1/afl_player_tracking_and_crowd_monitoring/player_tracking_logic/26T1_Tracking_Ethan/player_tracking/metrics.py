import csv
from pathlib import Path
from typing import Dict, Iterable, Tuple

from .config import TrackingConfig
from .geometry import euclidean_distance
from .tracker import Track


def _safe_first(items: Iterable):
    items = list(items)
    return items[0] if items else None


def export_player_metrics_csv(
    tracks: Dict[int, Track],
    csv_path: Path,
    fps: float,
    config: TrackingConfig,
):
    """
    Export simple movement metrics for each track.

    Distance and speed are approximate because they are computed from image pixels.
    For more accurate tactical analysis, replace pixel coordinates with field coordinates
    using homography or camera registration.
    """
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "track_id",
        "cluster_id",
        "cluster_team",
        "initial_class_id",
        "initial_class_name",
        "num_observed_frames",
        "jersey_sample_count",
        "first_frame",
        "last_frame",
        "first_time_sec",
        "last_time_sec",
        "total_distance_px",
        "total_distance_m",
        "avg_speed_kmh",
        "max_speed_kmh",
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for track_id, track in sorted(tracks.items(), key=lambda item: item[0]):
            frames = sorted(track.frames, key=lambda item: item["frame_index"])
            if not frames:
                continue

            total_distance_px = 0.0
            max_speed_kmh = 0.0

            for prev, curr in zip(frames[:-1], frames[1:]):
                prev_center = prev.get("center")
                curr_center = curr.get("center")
                if prev_center is None or curr_center is None:
                    continue

                dist_px = euclidean_distance(prev_center, curr_center)
                total_distance_px += dist_px

                dt = float(curr["time_sec"]) - float(prev["time_sec"])
                if dt > 1e-6:
                    speed_mps = (dist_px * config.pixel_to_meter) / dt
                    speed_kmh = speed_mps * 3.6
                    if speed_kmh <= config.max_speed_kmh:
                        max_speed_kmh = max(max_speed_kmh, speed_kmh)

            duration = max(float(frames[-1]["time_sec"]) - float(frames[0]["time_sec"]), 1e-6)
            total_distance_m = total_distance_px * config.pixel_to_meter
            avg_speed_kmh = (total_distance_m / duration) * 3.6

            writer.writerow(
                {
                    "track_id": int(track.track_id),
                    "cluster_id": "" if track.cluster_id is None else int(track.cluster_id),
                    "cluster_team": str(track.cluster_team),
                    "initial_class_id": int(track.initial_class_id),
                    "initial_class_name": str(track.initial_class_name),
                    "num_observed_frames": int(len(frames)),
                    "jersey_sample_count": int(len(track.jersey_features)),
                    "first_frame": int(frames[0]["frame_index"]),
                    "last_frame": int(frames[-1]["frame_index"]),
                    "first_time_sec": round(float(frames[0]["time_sec"]), 3),
                    "last_time_sec": round(float(frames[-1]["time_sec"]), 3),
                    "total_distance_px": round(float(total_distance_px), 3),
                    "total_distance_m": round(float(total_distance_m), 3),
                    "avg_speed_kmh": round(float(avg_speed_kmh), 3),
                    "max_speed_kmh": round(float(max_speed_kmh), 3),
                }
            )
