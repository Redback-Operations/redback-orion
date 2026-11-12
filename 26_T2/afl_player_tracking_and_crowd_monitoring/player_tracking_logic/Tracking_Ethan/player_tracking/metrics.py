import csv
from pathlib import Path
from typing import Dict, Iterable

from .calibration import compute_homography, transform_point
from .config import TrackingConfig
from .geometry import euclidean_distance
from .tracker import Track


def _safe_first(items: Iterable):
    items = list(items)
    return items[0] if items else None


def _get_homography(config: TrackingConfig):
    """
    Build an image-to-field homography when calibration points are supplied.

    Field calibration points are expected to be in metres.
    A static homography should only be used for footage where the camera view
    remains compatible with the supplied calibration.
    """
    image_points = config.image_calibration_points
    field_points = config.field_calibration_points

    if image_points is None and field_points is None:
        return None

    if image_points is None or field_points is None:
        raise ValueError(
            "Both image_calibration_points and "
            "field_calibration_points are required."
        )

    return compute_homography(
        image_points,
        field_points,
    )


def export_player_metrics_csv(
    tracks: Dict[int, Track],
    csv_path: Path,
    fps: float,
    config: TrackingConfig,
):
    """
    Export movement metrics for each track.

    Without calibration, metre-based distance and speed values use the existing
    approximate pixel-to-metre conversion.

    When valid image-to-field calibration points are supplied, player
    ground-points are transformed into field coordinates and metre-based
    movement metrics are calculated from those coordinates.

    A single static homography is not suitable across broadcast camera cuts,
    pans or zoom changes unless the calibration remains valid.

    Returns a small provenance summary so API consumers can determine whether
    metre-based metrics were field calibrated or estimated from image pixels.
    """
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    homography = _get_homography(config)

    calibration_available = homography is not None
    metric_mode = (
        "field_calibrated"
        if calibration_available
        else "pixel_estimate"
    )

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
        "metric_mode",
        "calibration_available",
    ]

    exported_tracks = 0

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
        )
        writer.writeheader()

        for track_id, track in sorted(
            tracks.items(),
            key=lambda item: item[0],
        ):
            frames = sorted(
                track.frames,
                key=lambda item: item["frame_index"],
            )

            if not frames:
                continue

            total_distance_px = 0.0
            total_distance_m = 0.0
            max_speed_kmh = 0.0

            for prev, curr in zip(
                frames[:-1],
                frames[1:],
            ):
                prev_center = prev.get("center")
                curr_center = curr.get("center")

                if (
                    prev_center is None
                    or curr_center is None
                ):
                    continue

                # Preserve the existing image-space distance metric.
                dist_px = euclidean_distance(
                    prev_center,
                    curr_center,
                )
                total_distance_px += dist_px

                dt = (
                    float(curr["time_sec"])
                    - float(prev["time_sec"])
                )

                if homography is not None:
                    prev_ground = prev.get("ground_point")
                    curr_ground = curr.get("ground_point")

                    if (
                        prev_ground is None
                        or curr_ground is None
                    ):
                        continue

                    prev_field = transform_point(
                        prev_ground,
                        homography,
                    )
                    curr_field = transform_point(
                        curr_ground,
                        homography,
                    )

                    # Field coordinates are supplied in metres,
                    # so this distance is already in metres.
                    dist_m = euclidean_distance(
                        prev_field,
                        curr_field,
                    )

                else:
                    # Existing approximate fallback.
                    dist_m = (
                        dist_px
                        * config.pixel_to_meter
                    )

                total_distance_m += dist_m

                if dt > 1e-6:
                    speed_mps = dist_m / dt
                    speed_kmh = speed_mps * 3.6

                    if speed_kmh <= config.max_speed_kmh:
                        max_speed_kmh = max(
                            max_speed_kmh,
                            speed_kmh,
                        )

            duration = max(
                float(frames[-1]["time_sec"])
                - float(frames[0]["time_sec"]),
                1e-6,
            )

            avg_speed_kmh = (
                total_distance_m
                / duration
            ) * 3.6

            writer.writerow(
                {
                    "track_id": int(track.track_id),
                    "cluster_id": (
                        ""
                        if track.cluster_id is None
                        else int(track.cluster_id)
                    ),
                    "cluster_team": str(
                        track.cluster_team
                    ),
                    "initial_class_id": int(
                        track.initial_class_id
                    ),
                    "initial_class_name": str(
                        track.initial_class_name
                    ),
                    "num_observed_frames": int(
                        len(frames)
                    ),
                    "jersey_sample_count": int(
                        len(track.jersey_features)
                    ),
                    "first_frame": int(
                        frames[0]["frame_index"]
                    ),
                    "last_frame": int(
                        frames[-1]["frame_index"]
                    ),
                    "first_time_sec": round(
                        float(frames[0]["time_sec"]),
                        3,
                    ),
                    "last_time_sec": round(
                        float(frames[-1]["time_sec"]),
                        3,
                    ),
                    "total_distance_px": round(
                        float(total_distance_px),
                        3,
                    ),
                    "total_distance_m": round(
                        float(total_distance_m),
                        3,
                    ),
                    "avg_speed_kmh": round(
                        float(avg_speed_kmh),
                        3,
                    ),
                    "max_speed_kmh": round(
                        float(max_speed_kmh),
                        3,
                    ),
                    "metric_mode": metric_mode,
                    "calibration_available": calibration_available,
                }
            )

            exported_tracks += 1

    return {
        "metric_mode": metric_mode,
        "calibration_available": calibration_available,
        "exported_tracks": exported_tracks,
        "metrics_csv_path": str(csv_path),
    }