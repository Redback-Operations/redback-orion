#!/usr/bin/env python3
"""Extract per-player crops from a track_video.py CSV + its source video.

This is step 1 of the jersey number recognition pipeline: it does NOT
detect anything itself. It reads the CSV that track_video.py already
produces (frame, track_id, class, confidence, x1, y1, x2, y2) and uses
those coordinates to crop each player out of the matching video frame.

Output layout:
    outputs/jersey_crops/track_<id>/frame_<n>.jpg

This groups crops by track_id so the next pipeline stage (EasyOCR +
majority-vote across frames) can just loop over each track_<id> folder.

Usage:
    python extract_player_crops.py data/videos/video_1.mp4 outputs/video_1_player_ref_best.csv
    python extract_player_crops.py data/videos/video_1.mp4 outputs/video_1_player_ref_best.csv \
        --out outputs/jersey_crops --classes player --padding 0.08 --every-n-frames 5
"""

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

import cv2


def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("video", type=Path, help="Source video matching the CSV")
    p.add_argument("csv_path", type=Path, help="track_video.py output CSV")
    p.add_argument("--out", type=Path, default=Path("outputs/jersey_crops"),
                   help="Output directory for crops (default: outputs/jersey_crops)")
    p.add_argument("--classes", nargs="+", default=None,
                   help="Only crop these class labels (e.g. --classes player). "
                        "Default: crop every class in the CSV.")
    p.add_argument("--padding", type=float, default=0.08,
                   help="Fractional padding added around each box on every "
                        "side, relative to box width/height (default: 0.08)")
    p.add_argument("--every-n-frames", type=int, default=1,
                   help="Only process every Nth frame present in the CSV "
                        "(default: 1 = every frame)")
    p.add_argument("--min-conf", type=float, default=0.0,
                   help="Skip detections below this confidence (default: 0.0)")
    p.add_argument("--jpeg-quality", type=int, default=95)
    return p.parse_args()


def load_detections(csv_path: Path, classes, min_conf: float):
    """Group CSV rows by frame number. Returns {frame_idx: [row, ...]}."""
    by_frame = defaultdict(list)
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        required = {"frame", "track_id", "class", "confidence", "x1", "y1", "x2", "y2"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            sys.exit(f"CSV is missing expected columns: {sorted(missing)}")

        for row in reader:
            if classes and row["class"] not in classes:
                continue
            if float(row["confidence"]) < min_conf:
                continue
            by_frame[int(row["frame"])].append(row)
    return by_frame


def pad_box(x1, y1, x2, y2, padding, frame_w, frame_h):
    """Expand a box by `padding` fraction of its own width/height, clamped
    to the frame bounds."""
    w = x2 - x1
    h = y2 - y1
    px = w * padding
    py = h * padding
    return (
        max(0, x1 - px),
        max(0, y1 - py),
        min(frame_w, x2 + px),
        min(frame_h, y2 + py),
    )


def main():
    args = parse_args()

    if not args.video.exists():
        sys.exit(f"Video not found: {args.video}")
    if not args.csv_path.exists():
        sys.exit(f"CSV not found: {args.csv_path}")

    by_frame = load_detections(args.csv_path, args.classes, args.min_conf)
    if not by_frame:
        sys.exit("No detections loaded from CSV (check --classes / --min-conf filters)")

    target_frames = sorted(by_frame)[::args.every_n_frames]
    print(f"CSV has detections on {len(by_frame)} frames; "
          f"processing {len(target_frames)} of them (every {args.every_n_frames})")

    cap = cv2.VideoCapture(str(args.video))
    if not cap.isOpened():
        sys.exit(f"Could not open video: {args.video}")
    frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    args.out.mkdir(parents=True, exist_ok=True)
    jpeg_params = [cv2.IMWRITE_JPEG_QUALITY, args.jpeg_quality]

    n_saved = 0
    n_skipped = 0
    current_pos = -1

    for frame_idx in target_frames:
        # Seek only if we're not already positioned right before this frame.
        if frame_idx != current_pos + 1:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ok, frame = cap.read()
        current_pos = frame_idx
        if not ok:
            print(f"  warning: could not read frame {frame_idx}, skipping")
            n_skipped += len(by_frame[frame_idx])
            continue

        for row in by_frame[frame_idx]:
            track_id = int(row["track_id"])
            x1, y1, x2, y2 = (float(row["x1"]), float(row["y1"]),
                              float(row["x2"]), float(row["y2"]))
            x1, y1, x2, y2 = pad_box(x1, y1, x2, y2, args.padding, frame_w, frame_h)
            x1i, y1i, x2i, y2i = int(x1), int(y1), int(x2), int(y2)

            if x2i <= x1i or y2i <= y1i:
                n_skipped += 1
                continue

            crop = frame[y1i:y2i, x1i:x2i]
            if crop.size == 0:
                n_skipped += 1
                continue

            track_dir = args.out / f"track_{track_id}"
            track_dir.mkdir(exist_ok=True)
            out_path = track_dir / f"frame_{frame_idx}.jpg"
            cv2.imwrite(str(out_path), crop, jpeg_params)
            n_saved += 1

        if frame_idx % 100 == 0:
            print(f"  processed frame {frame_idx}...")

    cap.release()
    print(f"Done. Saved {n_saved} crops, skipped {n_skipped}. Output dir: {args.out}")


if __name__ == "__main__":
    main()
