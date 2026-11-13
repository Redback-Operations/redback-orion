"""Track players and convert detections into Forward-50 positional data."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

import cv2
from ultralytics import YOLO

from geometry import assign_zone, contains, ground_point, scale_polygon

ZONE_COLOURS = {
    "left_pocket": (45, 90, 220),
    "left_half_forward": (40, 170, 240),
    "central_corridor": (60, 190, 80),
    "right_half_forward": (220, 170, 40),
    "right_pocket": (180, 70, 170),
}

PLAYER_FIELDS = [
    "frame", "time_seconds", "player_id", "confidence",
    "x1", "y1", "x2", "y2", "ground_x", "ground_y",
    "inside_forward50", "zone",
]


def load_config(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        config = json.load(handle)
    required = {"model", "tracker", "forward50_polygon_normalized", "zones_normalized"}
    missing = required - config.keys()
    if missing:
        raise ValueError(f"Missing config keys: {sorted(missing)}")
    return config


def make_writer(path: Path, fps: float, width: int, height: int) -> cv2.VideoWriter:
    writer = cv2.VideoWriter(
        str(path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height)
    )
    if not writer.isOpened():
        raise RuntimeError(f"Could not create output video: {path}")
    return writer


def draw_zones(frame, forward50, zones) -> None:
    overlay = frame.copy()
    for name, polygon in zones.items():
        colour = ZONE_COLOURS.get(name, (160, 160, 160))
        cv2.fillPoly(overlay, [polygon], colour)
        centre = polygon.mean(axis=0).astype(int)
        cv2.putText(overlay, name.replace("_", " "), tuple(centre),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.addWeighted(overlay, 0.18, frame, 0.82, 0, frame)
    cv2.polylines(frame, [forward50], True, (255, 255, 255), 2)


def run(video_path: Path, output_dir: Path, config_path: Path) -> None:
    config = load_config(config_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise FileNotFoundError(f"Could not open video: {video_path}")

    fps = capture.get(cv2.CAP_PROP_FPS)
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if fps <= 0 or width <= 0 or height <= 0:
        raise RuntimeError("Video metadata is invalid")

    forward50 = scale_polygon(config["forward50_polygon_normalized"], width, height)
    zones = {
        name: scale_polygon(points, width, height)
        for name, points in config["zones_normalized"].items()
    }
    model = YOLO(config["model"])
    writer = make_writer(output_dir / "annotated_forward50.mp4", fps, width, height)
    every_n = max(1, int(config.get("process_every_n_frames", 1)))
    confidence_threshold = float(config.get("confidence_threshold", 0.35))
    person_class_id = int(config.get("person_class_id", 0))

    player_file = (output_dir / "player_positions.csv").open("w", newline="", encoding="utf-8")
    occupancy_file = (output_dir / "zone_occupancy.csv").open("w", newline="", encoding="utf-8")
    player_csv = csv.DictWriter(player_file, fieldnames=PLAYER_FIELDS)
    occupancy_fields = [
        "frame", "time_seconds", *zones.keys(), "unassigned_inside",
        "total_inside_forward50",
    ]
    occupancy_csv = csv.DictWriter(occupancy_file, fieldnames=occupancy_fields)
    player_csv.writeheader()
    occupancy_csv.writeheader()

    frame_number = 0
    processed_frames = 0
    total_inside = 0
    located_inside_zones = 0
    start_time = max(0.0, float(config.get("start_time_seconds", 0)))
    end_time_value = config.get("end_time_seconds")
    end_time = float(end_time_value) if end_time_value is not None else None
    if end_time is not None and end_time <= start_time:
        raise ValueError("end_time_seconds must be greater than start_time_seconds")
    capture.set(cv2.CAP_PROP_POS_MSEC, start_time * 1000)
    frame_number = int(round(start_time * fps))

    try:
        while True:
            if end_time is not None and frame_number / fps >= end_time:
                break
            ok, frame = capture.read()
            if not ok:
                break
            if frame_number % every_n != 0:
                writer.write(frame)
                frame_number += 1
                continue

            result = model.track(
                frame,
                persist=True,
                tracker=config["tracker"],
                classes=[person_class_id],
                conf=confidence_threshold,
                verbose=False,
            )[0]
            draw_zones(frame, forward50, zones)
            counts = Counter({name: 0 for name in zones})
            unassigned_inside = 0

            if result.boxes is not None and result.boxes.id is not None:
                boxes = result.boxes.xyxy.cpu().numpy()
                ids = result.boxes.id.int().cpu().tolist()
                confidences = result.boxes.conf.cpu().tolist()
                for bbox, player_id, confidence in zip(boxes, ids, confidences):
                    point = ground_point(bbox)
                    inside = contains(point, forward50)
                    zone = assign_zone(point, zones) if inside else None
                    if inside:
                        total_inside += 1
                        if zone:
                            counts[zone] += 1
                            located_inside_zones += 1
                        else:
                            unassigned_inside += 1

                    x1, y1, x2, y2 = map(float, bbox)
                    player_csv.writerow({
                        "frame": frame_number,
                        "time_seconds": round(frame_number / fps, 3),
                        "player_id": player_id,
                        "confidence": round(float(confidence), 4),
                        "x1": round(x1, 2), "y1": round(y1, 2),
                        "x2": round(x2, 2), "y2": round(y2, 2),
                        "ground_x": round(point[0], 2), "ground_y": round(point[1], 2),
                        "inside_forward50": inside,
                        "zone": zone if zone else ("unassigned" if inside else "outside"),
                    })

                    colour = ZONE_COLOURS.get(zone, (130, 130, 130))
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), colour, 2)
                    cv2.circle(frame, (round(point[0]), round(point[1])), 5, colour, -1)
                    cv2.putText(frame, f"ID {player_id} | {zone or 'outside'}",
                                (int(x1), max(18, int(y1) - 7)), cv2.FONT_HERSHEY_SIMPLEX,
                                0.45, colour, 2, cv2.LINE_AA)

            occupancy_csv.writerow({
                "frame": frame_number,
                "time_seconds": round(frame_number / fps, 3),
                **counts,
                "unassigned_inside": unassigned_inside,
                "total_inside_forward50": sum(counts.values()) + unassigned_inside,
            })
            writer.write(frame)
            processed_frames += 1
            frame_number += 1
    finally:
        capture.release()
        writer.release()
        player_file.close()
        occupancy_file.close()

    summary = {
        "video": str(video_path),
        "frame_width": width,
        "frame_height": height,
        "fps": fps,
        "processed_frames": processed_frames,
        "start_time_seconds": start_time,
        "end_time_seconds": end_time,
        "inside_forward50_detections": total_inside,
        "inside_detections_with_zone": located_inside_zones,
        "zone_assignment_rate": round(located_inside_zones / total_inside, 4) if total_inside else None,
        "limitations": [
            "Locations are image-coordinate estimates, not GPS or real-world measurements.",
            "Fixed polygons are appropriate only while the camera view remains stable.",
            "Tracking IDs may change after occlusion or when a player leaves the frame.",
        ],
    }
    (output_dir / "run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Complete. Outputs written to {output_dir}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument("--config", type=Path, default=Path("config.json"))
    parser.add_argument("--output", type=Path, default=Path("output"))
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(args.video, args.output, args.config)
