"""Movement metrics from a tracks CSV.

Reads the tracks detect_and_track.py wrote, so no detection model runs here
and the player IDs match the tracking stage. The video is still read for
appearance and jersey-colour features, which drive team clustering.
"""

import csv
import json
from collections import defaultdict
from pathlib import Path

import cv2

from .appearance import extract_appearance_feature, extract_jersey_colour_feature
from .config import TrackingConfig
from .geometry import bbox_bottom_center, bbox_center
from .jersey_cluster import assign_jersey_clusters
from .metrics import export_player_metrics_csv
from .tracker import track_from_detection, tracks_to_json_records
from .visualizer import draw_frame_records

PLAYER_CLASS = "PLAYER"


def validate_paths(config: TrackingConfig, tracks_csv: Path):
    if not config.video_path.exists():
        raise FileNotFoundError(f"Cannot find video: {config.video_path}")

    if not tracks_csv.exists():
        raise FileNotFoundError(f"Cannot find tracks CSV: {tracks_csv}")

    config.output_video_path.parent.mkdir(parents=True, exist_ok=True)
    config.output_json_path.parent.mkdir(parents=True, exist_ok=True)
    config.output_csv_path.parent.mkdir(parents=True, exist_ok=True)


def read_player_rows(tracks_csv: Path):
    """Group the tracks CSV rows for players (not umpires) by frame."""
    by_frame = defaultdict(list)
    with open(tracks_csv, newline="") as f:
        for row in csv.DictReader(f):
            if row["class"] == PLAYER_CLASS:
                by_frame[int(row["frame"])].append(row)
    return by_frame


def _build_frame_record_map(tracks):
    frame_records = defaultdict(list)

    for track in tracks.values():
        for record in track.frames:
            item = dict(record)
            item["track_id"] = int(track.track_id)
            item["cluster_id"] = None if track.cluster_id is None else int(track.cluster_id)
            item["cluster_team"] = str(track.cluster_team)
            frame_records[int(item["frame_index"])].append(item)

    return frame_records


def _render_clustered_video(config: TrackingConfig, tracks, fps: float, width: int, height: int, processed_frames: int):
    cap = cv2.VideoCapture(str(config.video_path))
    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot reopen video for rendering: {config.video_path}")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video_writer = cv2.VideoWriter(str(config.output_video_path), fourcc, fps, (width, height))
    if not video_writer.isOpened():
        cap.release()
        raise RuntimeError(f"Cannot create output video: {config.output_video_path}")

    frame_records = _build_frame_record_map(tracks)
    trails = {}

    try:
        for frame_index in range(processed_frames):
            ok, frame = cap.read()
            if not ok:
                break

            output_frame = draw_frame_records(
                frame,
                frame_records.get(frame_index, []),
                trails=trails,
                trail_length=config.trail_length,
                draw_confidence=config.draw_confidence,
                draw_cluster=config.draw_cluster,
            )
            video_writer.write(output_frame)
    finally:
        cap.release()
        video_writer.release()


def process_tracks(config: TrackingConfig, tracks_csv):
    """Cluster teams, render the trajectory video and export movement metrics."""
    tracks_csv = Path(tracks_csv)
    validate_paths(config, tracks_csv)

    cap = cv2.VideoCapture(str(config.video_path))
    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open video: {config.video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if fps <= 0:
        raise ValueError("Video FPS is invalid. Cannot calculate process duration.")

    max_frames_to_process = min(int(fps * config.process_seconds), total_frames)
    rows_by_frame = read_player_rows(tracks_csv)

    tracks = {}
    processed_frames = 0
    try:
        for frame_index in range(max_frames_to_process):
            ok, frame = cap.read()
            if not ok:
                break

            time_sec = frame_index / fps
            for row in rows_by_frame.get(frame_index, []):
                bbox = [float(row[k]) for k in ("x1", "y1", "x2", "y2")]
                detection = {
                    "bbox": bbox,
                    "center": bbox_center(bbox),
                    "ground_point": bbox_bottom_center(bbox),
                    "conf": float(row["confidence"]),
                    "class_id": 0,
                    "class_name": PLAYER_CLASS,
                    "appearance": extract_appearance_feature(frame, bbox),
                    "jersey_feature": extract_jersey_colour_feature(frame, bbox),
                }
                track_id = int(row["track_id"])
                if track_id in tracks:
                    tracks[track_id].update(detection, frame_index, time_sec, config.appearance_momentum)
                else:
                    tracks[track_id] = track_from_detection(track_id, detection, frame_index, time_sec, config)

            processed_frames += 1
    finally:
        cap.release()

    clustering_summary = assign_jersey_clusters(tracks, config)

    _render_clustered_video(
        config=config,
        tracks=tracks,
        fps=fps,
        width=width,
        height=height,
        processed_frames=processed_frames,
    )

    metrics_summary = export_player_metrics_csv(
        tracks=tracks,
        csv_path=config.output_csv_path,
        fps=fps,
        config=config,
    )

    export_data = {
        "video_path": str(config.video_path),
        "model_path": str(config.model_path),
        "output_video_path": str(config.output_video_path),
        "output_json_path": str(config.output_json_path),
        "output_csv_path": str(config.output_csv_path),
        "fps": float(fps),
        "total_frames": int(total_frames),
        "processed_frames": int(processed_frames),
        "process_seconds": int(config.process_seconds),
        "resolution": {"width": int(width), "height": int(height)},
        "player_classes": [int(c) for c in config.player_classes],
        "jersey_clustering": clustering_summary,
        "movement_metrics": metrics_summary,
        "tracks": tracks_to_json_records(tracks),
    }

    with open(config.output_json_path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)

    return export_data
