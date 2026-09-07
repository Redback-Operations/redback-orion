import json
from collections import defaultdict

import cv2
from ultralytics import YOLO

from .config import TrackingConfig
from .detector import parse_yolo_detections
from .jersey_cluster import assign_jersey_clusters
from .metrics import export_player_metrics_csv
from .tracker import RobustPlayerTracker
from .visualizer import draw_frame_records


def validate_paths(config: TrackingConfig):
    if not config.video_path.exists():
        raise FileNotFoundError(f"Cannot find video: {config.video_path}")

    if not config.model_path.exists():
        raise FileNotFoundError(f"Cannot find model: {config.model_path}")

    config.output_video_path.parent.mkdir(parents=True, exist_ok=True)
    config.output_json_path.parent.mkdir(parents=True, exist_ok=True)
    config.output_csv_path.parent.mkdir(parents=True, exist_ok=True)


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


def process_video(config: TrackingConfig):
    print("===== YOLO tracking + JerseyColorDetection-style KMeans clustering =====")
    validate_paths(config)

    model = YOLO(str(config.model_path))

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

    print(f"Video: {config.video_path}")
    print(f"Model: {config.model_path}")
    print(f"FPS: {fps:.2f}")
    print(f"Total frames: {total_frames}")
    print(f"Frames to process: {max_frames_to_process}")
    print(f"Resolution: {width} x {height}")

    tracker = RobustPlayerTracker(config)
    processed_frames = 0

    try:
        for frame_index in range(max_frames_to_process):
            ok, frame = cap.read()
            if not ok:
                break

            results = model.predict(
                frame,
                conf=config.conf_threshold,
                imgsz=config.imgsz,
                verbose=False,
            )

            result = results[0] if results else None
            detections = parse_yolo_detections(
                result=result,
                frame=frame,
                model=model,
                player_classes=config.player_classes,
                duplicate_center_distance=config.duplicate_center_distance,
            )

            time_sec = frame_index / fps
            active_tracks = tracker.update(detections, frame_index=frame_index, time_sec=time_sec)

            processed_frames += 1
            if config.print_every_n_frames > 0 and processed_frames % config.print_every_n_frames == 0:
                print(
                    f"Processed {processed_frames}/{max_frames_to_process} frames | "
                    f"detections={len(detections)} | active_tracks={len(active_tracks)}"
                )

    finally:
        cap.release()

    all_tracks = tracker.all_tracks()

    clustering_summary = assign_jersey_clusters(all_tracks, config)

    _render_clustered_video(
        config=config,
        tracks=all_tracks,
        fps=fps,
        width=width,
        height=height,
        processed_frames=processed_frames,
    )

    export_player_metrics_csv(
        tracks=all_tracks,
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
        "tracks": tracker.to_json_records(),
    }

    with open(config.output_json_path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)

    print("Done.")
    print(f"Output video: {config.output_video_path}")
    print(f"Output JSON: {config.output_json_path}")
    print(f"Output CSV: {config.output_csv_path}")
    print(f"Total tracks: {len(export_data['tracks'])}")
    print(f"Jersey clustering: {clustering_summary}")

    return export_data
