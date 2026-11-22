#!/usr/bin/env python3

import argparse
import cv2
from pathlib import Path


def extract_frames(
    video_path,
    output_dir="frames",
    gap_seconds=7,
    max_frames=200,
    jpeg_quality=60,
):
    video_path = Path(video_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        raise FileNotFoundError(f"Could not open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration_seconds = total_frames / fps if fps else 0

    saved = 0
    timestamp = 0

    while saved < max_frames and timestamp <= duration_seconds:
        frame_number = int(timestamp * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

        success, frame = cap.read()
        if not success:
            break

        output_path = output_dir / f"{saved + 1:02d}.jpg"

        cv2.imwrite(
            str(output_path),
            frame,
            [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality],
        )

        print(f"Saved {output_path}")

        saved += 1
        timestamp += gap_seconds

    cap.release()
    print(f"Done. Extracted {saved} frame(s).")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("video", help="Path to the input video file")
    parser.add_argument("--out", default="frames", help="Output folder")
    parser.add_argument("--gap", type=int, default=10, help="Gap between frames in seconds")
    parser.add_argument("--max", type=int, default=200, help="Maximum number of frames")
    parser.add_argument("--quality", type=int, default=60, help="JPEG quality from 1 to 100")

    args = parser.parse_args()

    extract_frames(
        video_path=args.video,
        output_dir=args.out,
        gap_seconds=args.gap,
        max_frames=args.max,
        jpeg_quality=args.quality,
    )


if __name__ == "__main__":
    main()