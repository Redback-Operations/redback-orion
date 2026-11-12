from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Measure global camera motion in broadcast footage."
    )
    parser.add_argument("video", type=Path)
    parser.add_argument("--max-frames", type=int, default=300)
    parser.add_argument("--feature-limit", type=int, default=300)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    capture = cv2.VideoCapture(str(args.video))

    if not capture.isOpened():
        raise RuntimeError(f"Could not open video: {args.video}")

    fps = capture.get(cv2.CAP_PROP_FPS)
    total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

    ok, previous_frame = capture.read()

    if not ok:
        raise RuntimeError("Could not read first frame.")

    previous_gray = cv2.cvtColor(
        previous_frame,
        cv2.COLOR_BGR2GRAY,
    )

    motion_records = []

    for frame_number in range(1, args.max_frames):
        ok, current_frame = capture.read()

        if not ok:
            break

        current_gray = cv2.cvtColor(
            current_frame,
            cv2.COLOR_BGR2GRAY,
        )

        previous_points = cv2.goodFeaturesToTrack(
            previous_gray,
            maxCorners=args.feature_limit,
            qualityLevel=0.01,
            minDistance=10,
            blockSize=7,
        )

        if previous_points is None:
            previous_gray = current_gray
            continue

        current_points, status, _ = cv2.calcOpticalFlowPyrLK(
            previous_gray,
            current_gray,
            previous_points,
            None,
        )

        if current_points is None or status is None:
            previous_gray = current_gray
            continue

        valid = status.reshape(-1) == 1

        old_points = previous_points.reshape(-1, 2)[valid]
        new_points = current_points.reshape(-1, 2)[valid]

        if len(old_points) < 8:
            previous_gray = current_gray
            continue

        transform, inliers = cv2.estimateAffinePartial2D(
            old_points,
            new_points,
            method=cv2.RANSAC,
            ransacReprojThreshold=3.0,
        )

        if transform is not None:
            dx = float(transform[0, 2])
            dy = float(transform[1, 2])

            motion = float(np.hypot(dx, dy))

            inlier_count = (
                int(inliers.sum())
                if inliers is not None
                else 0
            )

            motion_records.append(
                {
                    "frame": frame_number,
                    "dx": dx,
                    "dy": dy,
                    "motion": motion,
                    "inliers": inlier_count,
                }
            )

        previous_gray = current_gray

    capture.release()

    print(f"Video: {args.video}")
    print(f"FPS: {fps:.3f}")
    print(f"Source frames: {total_frames}")
    print(f"Analysed transitions: {len(motion_records)}")

    if not motion_records:
        print("No reliable motion estimates found.")
        return

    motions = np.array(
        [record["motion"] for record in motion_records]
    )

    print()
    print("Camera motion summary")
    print(
        f"Mean motion: "
        f"{motions.mean():.3f} px/frame"
    )
    print(
        f"95th percentile: "
        f"{np.percentile(motions, 95):.3f} px/frame"
    )
    print(
        f"Maximum motion: "
        f"{motions.max():.3f} px/frame"
    )

    worst = sorted(
        motion_records,
        key=lambda record: record["motion"],
        reverse=True,
    )[:10]

    print()
    print("Largest motion frames")
    print("frame    dx_px    dy_px    motion_px    inliers")

    for record in worst:
        print(
            f"{record['frame']:5d} "
            f"{record['dx']:8.3f} "
            f"{record['dy']:8.3f} "
            f"{record['motion']:12.3f} "
            f"{record['inliers']:8d}"
        )


if __name__ == "__main__":
    main()