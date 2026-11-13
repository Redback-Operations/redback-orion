#!/usr/bin/env python3
"""Evaluate the V4 detector and temporal tracker on protected ground truth.

The input annotations are evaluation-only and must never be added to training.
The script reads a Label Studio "YOLO with Images" ZIP, runs the detector on
the completed images, compares detector and tracker boxes with the ground
truth, and writes per-frame CSV and summary JSON evidence.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import zipfile
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "temporal_tracker_evaluation"
FRAME_PATTERN = re.compile(r"_frame_(\d+)_")
IOU_THRESHOLDS = (0.10, 0.30, 0.50)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ground-truth",
        type=Path,
        required=True,
        help="evaluation-only Label Studio 'YOLO with Images' ZIP",
    )
    parser.add_argument(
        "--model",
        type=Path,
        required=True,
        help="trained ball-detection model to evaluate",
    )
    parser.add_argument(
        "--tracker-csv",
        type=Path,
        required=True,
        help="CSV produced by track_ball_temporal.py on the source clip",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--confidence", type=float, default=0.05)
    parser.add_argument("--image-size", type=int, default=1280)
    parser.add_argument("--expected-total-frames", type=int, default=50)
    return parser.parse_args()


def box_iou(first: list[float], second: list[float]) -> float:
    x1 = max(first[0], second[0])
    y1 = max(first[1], second[1])
    x2 = min(first[2], second[2])
    y2 = min(first[3], second[3])
    intersection = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    first_area = max(0.0, first[2] - first[0]) * max(0.0, first[3] - first[1])
    second_area = max(0.0, second[2] - second[0]) * max(0.0, second[3] - second[1])
    union = first_area + second_area - intersection
    return intersection / union if union > 0 else 0.0


def yolo_box_to_xyxy(line: str, width: int, height: int) -> list[float]:
    fields = line.split()
    if len(fields) != 5:
        raise ValueError(f"Expected five YOLO fields, found {len(fields)}: {line!r}")
    class_id = int(float(fields[0]))
    if class_id != 0:
        raise ValueError(f"Expected BALL class 0, found {class_id}")
    center_x, center_y, box_width, box_height = map(float, fields[1:])
    return [
        (center_x - box_width / 2) * width,
        (center_y - box_height / 2) * height,
        (center_x + box_width / 2) * width,
        (center_y + box_height / 2) * height,
    ]


def source_frame_from_name(name: str) -> int:
    match = FRAME_PATTERN.search(Path(name).stem)
    if not match:
        raise ValueError(f"Could not read source frame from filename: {name}")
    return int(match.group(1))


def load_tracker_rows(path: Path) -> dict[int, list[dict[str, str]]]:
    rows: dict[int, list[dict[str, str]]] = defaultdict(list)
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            rows[int(row["frame"])].append(row)
    return dict(rows)


def tracker_box(row: dict[str, str]) -> list[float]:
    return [float(row[key]) for key in ("x1", "y1", "x2", "y2")]


def safe_mean(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 4) if values else None


def threshold_summary(
    records: list[dict[str, object]],
    prefix: str,
    threshold: float,
) -> dict[str, object]:
    positives = [record for record in records if record["ground_truth"] == "BALL"]
    negatives = [record for record in records if record["ground_truth"] == "EMPTY"]
    hits = [record for record in positives if float(record[f"{prefix}_max_iou"]) >= threshold]
    misses = len(positives) - len(hits)
    false_positive_frames = sum(bool(record[f"{prefix}_has_output"]) for record in negatives)
    correct_empty_frames = len(negatives) - false_positive_frames
    return {
        "iou_threshold": threshold,
        "positive_frames": len(positives),
        "true_positive_frames": len(hits),
        "missed_positive_frames": misses,
        "visible_ball_recall": round(len(hits) / len(positives), 4) if positives else None,
        "empty_frames": len(negatives),
        "false_positive_empty_frames": false_positive_frames,
        "correct_empty_frames": correct_empty_frames,
        "empty_frame_specificity": (
            round(correct_empty_frames / len(negatives), 4) if negatives else None
        ),
        "mean_iou_for_hits": safe_mean(
            [float(record[f"{prefix}_max_iou"]) for record in hits]
        ),
    }


def main() -> None:
    args = parse_args()
    for path, description in (
        (args.ground_truth, "ground-truth ZIP"),
        (args.model, "model"),
        (args.tracker_csv, "tracker CSV"),
    ):
        if not path.exists():
            raise SystemExit(f"Missing {description}: {path}")

    tracker_rows = load_tracker_rows(args.tracker_csv)
    model = YOLO(str(args.model))
    records: list[dict[str, object]] = []

    with zipfile.ZipFile(args.ground_truth) as archive:
        image_names = sorted(
            name
            for name in archive.namelist()
            if name.startswith("images/") and not name.endswith("/")
        )
        for image_name in image_names:
            label_name = f"labels/{Path(image_name).stem}.txt"
            if label_name not in archive.namelist():
                raise SystemExit(f"Missing label for {image_name}")

            encoded = np.frombuffer(archive.read(image_name), dtype=np.uint8)
            image = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
            if image is None:
                raise SystemExit(f"Could not decode {image_name}")
            height, width = image.shape[:2]
            label_lines = [
                line
                for line in archive.read(label_name).decode("utf-8").splitlines()
                if line.strip()
            ]
            if len(label_lines) > 1:
                raise SystemExit(f"Expected at most one active ball in {label_name}")
            ground_truth_box = (
                yolo_box_to_xyxy(label_lines[0], width, height) if label_lines else None
            )
            frame = source_frame_from_name(image_name)

            result = model.predict(
                image,
                conf=args.confidence,
                imgsz=args.image_size,
                verbose=False,
            )[0]
            detector_boxes = (
                result.boxes.xyxy.tolist() if result.boxes is not None else []
            )
            detector_confidences = (
                result.boxes.conf.tolist() if result.boxes is not None else []
            )
            detector_ious = (
                [box_iou(box, ground_truth_box) for box in detector_boxes]
                if ground_truth_box is not None
                else []
            )

            frame_tracker_rows = tracker_rows.get(frame, [])
            tracker_ious = (
                [box_iou(tracker_box(row), ground_truth_box) for row in frame_tracker_rows]
                if ground_truth_box is not None
                else []
            )
            best_tracker_row = None
            if frame_tracker_rows:
                if tracker_ious:
                    best_tracker_row = frame_tracker_rows[tracker_ious.index(max(tracker_ious))]
                else:
                    best_tracker_row = frame_tracker_rows[0]

            records.append(
                {
                    "filename": Path(image_name).name,
                    "source_frame": frame,
                    "ground_truth": "BALL" if ground_truth_box else "EMPTY",
                    "detector_prediction_count": len(detector_boxes),
                    "detector_has_output": bool(detector_boxes),
                    "detector_max_confidence": round(max(detector_confidences), 4)
                    if detector_confidences
                    else 0.0,
                    "detector_max_iou": round(max(detector_ious), 4)
                    if detector_ious
                    else 0.0,
                    "tracker_has_output": bool(frame_tracker_rows),
                    "tracker_source": best_tracker_row["source"] if best_tracker_row else "missing",
                    "tracker_track_id": int(best_tracker_row["track_id"])
                    if best_tracker_row
                    else "",
                    "tracker_max_iou": round(max(tracker_ious), 4)
                    if tracker_ious
                    else 0.0,
                }
            )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    detail_path = args.output_dir / "tracker_evaluation_per_frame.csv"
    with detail_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)

    positives = sum(record["ground_truth"] == "BALL" for record in records)
    negatives = sum(record["ground_truth"] == "EMPTY" for record in records)
    primary_threshold = 0.30
    primary_tracker_hits = [
        record
        for record in records
        if record["ground_truth"] == "BALL"
        and float(record["tracker_max_iou"]) >= primary_threshold
    ]
    summary = {
        "evaluation_policy": {
            "protected_evaluation_only": True,
            "may_enter_training": False,
            "completed_frames": len(records),
            "excluded_uncertain_frames": args.expected_total_frames - len(records),
            "positive_frames": positives,
            "empty_frames": negatives,
            "primary_iou_threshold": primary_threshold,
            "other_reported_iou_thresholds": list(IOU_THRESHOLDS),
        },
        "inputs": {
            "ground_truth": str(args.ground_truth),
            "model": str(args.model),
            "tracker_csv": str(args.tracker_csv),
            "confidence": args.confidence,
            "image_size": args.image_size,
        },
        "detector": {
            "total_predictions": sum(
                int(record["detector_prediction_count"]) for record in records
            ),
            "threshold_results": [
                threshold_summary(records, "detector", threshold)
                for threshold in IOU_THRESHOLDS
            ],
        },
        "temporal_tracker": {
            "frames_with_output": sum(bool(record["tracker_has_output"]) for record in records),
            "detected_source_frames": sum(
                record["tracker_source"] == "detected" for record in records
            ),
            "predicted_source_frames": sum(
                record["tracker_source"] == "predicted" for record in records
            ),
            "correct_predicted_bridge_frames_at_primary_iou": sum(
                record["tracker_source"] == "predicted" for record in primary_tracker_hits
            ),
            "correct_detected_frames_at_primary_iou": sum(
                record["tracker_source"] == "detected" for record in primary_tracker_hits
            ),
            "threshold_results": [
                threshold_summary(records, "tracker", threshold)
                for threshold in IOU_THRESHOLDS
            ],
        },
        "outputs": {"per_frame_csv": str(detail_path)},
    }
    summary_path = args.output_dir / "tracker_evaluation_summary.json"
    summary["outputs"]["summary_json"] = str(summary_path)
    summary_path.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
