#!/usr/bin/env python3
"""Create a compact visual review sheet from labelled frames and tracker output."""

from __future__ import annotations

import argparse
import csv
import re
import zipfile
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np


FRAME_PATTERN = re.compile(r"_frame_(\d+)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ground-truth", type=Path, required=True)
    parser.add_argument("--tracker-csv", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--tracker-name", default="Tracker")
    parser.add_argument("--frames", type=int, nargs="+", required=True)
    return parser.parse_args()


def frame_from_name(name: str) -> int:
    match = FRAME_PATTERN.search(Path(name).stem)
    if not match:
        raise ValueError(f"Cannot read frame number from {name}")
    return int(match.group(1))


def yolo_box(line: str, width: int, height: int) -> list[float]:
    fields = line.split()
    if len(fields) != 5 or int(float(fields[0])) != 0:
        raise ValueError(f"Invalid BALL annotation: {line!r}")
    cx, cy, box_width, box_height = map(float, fields[1:])
    return [
        (cx - box_width / 2) * width,
        (cy - box_height / 2) * height,
        (cx + box_width / 2) * width,
        (cy + box_height / 2) * height,
    ]


def tracker_box(row: dict[str, str] | None) -> list[float] | None:
    if row is None:
        return None
    return [float(row[key]) for key in ("x1", "y1", "x2", "y2")]


def draw_box(
    image: np.ndarray,
    box: list[float] | None,
    color: tuple[int, int, int],
    label: str,
) -> None:
    if box is None:
        return
    x1, y1, x2, y2 = [int(round(value)) for value in box]
    cv2.rectangle(image, (x1, y1), (x2, y2), color, 4)
    cv2.putText(
        image,
        label,
        (max(2, x1), max(24, y1 - 8)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.72,
        color,
        2,
        cv2.LINE_AA,
    )


def crop_around(
    image: np.ndarray,
    box: list[float] | None,
    minimum_span: int = 180,
) -> np.ndarray:
    if box is None:
        return image
    height, width = image.shape[:2]
    center_x = (box[0] + box[2]) / 2
    center_y = (box[1] + box[3]) / 2
    span = max(minimum_span, int(max(box[2] - box[0], box[3] - box[1]) * 8))
    x1 = max(0, int(center_x - span / 2))
    y1 = max(0, int(center_y - span / 2))
    x2 = min(width, x1 + span)
    y2 = min(height, y1 + span)
    x1 = max(0, x2 - span)
    y1 = max(0, y2 - span)
    return image[y1:y2, x1:x2]


def labelled_panel(image: np.ndarray, title: str, detail: str) -> np.ndarray:
    panel_width, image_height, footer_height = 520, 300, 54
    resized = cv2.resize(image, (panel_width, image_height))
    panel = np.full((image_height + footer_height, panel_width, 3), 255, np.uint8)
    panel[:image_height] = resized
    cv2.putText(panel, title, (8, image_height + 20), cv2.FONT_HERSHEY_SIMPLEX,
                0.56, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(panel, detail, (8, image_height + 44), cv2.FONT_HERSHEY_SIMPLEX,
                0.48, (0, 0, 0), 1, cv2.LINE_AA)
    return panel


def main() -> None:
    args = parse_args()
    if not args.ground_truth.is_file() or not args.tracker_csv.is_file():
        raise SystemExit("Ground-truth ZIP or tracker CSV is missing")

    tracker_rows: dict[int, list[dict[str, str]]] = defaultdict(list)
    with args.tracker_csv.open(newline="") as handle:
        for row in csv.DictReader(handle):
            tracker_rows[int(row["frame"])].append(row)

    requested = set(args.frames)
    examples: dict[int, tuple[np.ndarray, list[float] | None]] = {}
    with zipfile.ZipFile(args.ground_truth) as archive:
        names = set(archive.namelist())
        for image_name in names:
            if not image_name.startswith("images/") or image_name.endswith("/"):
                continue
            frame = frame_from_name(image_name)
            if frame not in requested:
                continue
            encoded = np.frombuffer(archive.read(image_name), np.uint8)
            image = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
            if image is None:
                raise SystemExit(f"Could not decode {image_name}")
            label_name = f"labels/{Path(image_name).stem}.txt"
            lines = [line for line in archive.read(label_name).decode().splitlines() if line.strip()]
            if len(lines) > 1:
                raise SystemExit(f"Multiple ground-truth boxes in {label_name}")
            height, width = image.shape[:2]
            truth = yolo_box(lines[0], width, height) if lines else None
            examples[frame] = (image, truth)

    missing = requested - set(examples)
    if missing:
        raise SystemExit(f"Requested frames are not completed labels: {sorted(missing)}")

    sheet_rows: list[np.ndarray] = []
    for frame in args.frames:
        image, truth = examples[frame]
        rows = tracker_rows.get(frame, [])
        tracker_row = rows[0] if rows else None
        predicted = tracker_box(tracker_row)
        source = tracker_row["source"] if tracker_row else "missing"

        truth_view = image.copy()
        draw_box(truth_view, truth, (0, 255, 0), "GROUND TRUTH")
        truth_view = crop_around(truth_view, truth or predicted)

        tracker_view = image.copy()
        draw_box(tracker_view, predicted, (0, 165, 255), args.tracker_name)
        tracker_view = crop_around(tracker_view, predicted or truth)

        context_view = image.copy()
        draw_box(context_view, truth, (0, 255, 0), "GT")
        draw_box(context_view, predicted, (0, 165, 255), args.tracker_name)

        truth_detail = "BALL" if truth is not None else "EMPTY"
        tracker_detail = source.upper()
        panels = [
            labelled_panel(truth_view, "Manual answer", truth_detail),
            labelled_panel(tracker_view, args.tracker_name, tracker_detail),
            labelled_panel(context_view, "Full-frame context", "green=GT, orange=tracker"),
        ]
        row = cv2.hconcat(panels)
        header = np.full((38, row.shape[1], 3), 242, np.uint8)
        cv2.putText(header, f"Source frame {frame}", (8, 27),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.68, (0, 0, 0), 2, cv2.LINE_AA)
        sheet_rows.append(cv2.vconcat([header, row]))

    sheet = cv2.vconcat(sheet_rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(args.output), sheet):
        raise SystemExit(f"Could not save {args.output}")
    print({"frames": args.frames, "saved": str(args.output),
           "dimensions": [sheet.shape[1], sheet.shape[0]]})


if __name__ == "__main__":
    main()
