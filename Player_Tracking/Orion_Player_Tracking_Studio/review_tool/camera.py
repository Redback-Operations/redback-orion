from __future__ import annotations

import math


def analyze_camera(video, max_frames=300, cancel=None, progress=None):
    # Adapted from Yash Talati's camera motion diagnostic in project PR 25.
    import cv2
    import numpy as np

    if max_frames < 2:
        raise ValueError("Choose at least two frames")
    capture = cv2.VideoCapture(str(video))
    try:
        if not capture.isOpened():
            raise ValueError("Could not open the match video")
        total = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = float(capture.get(cv2.CAP_PROP_FPS))
        if not math.isfinite(fps) or fps <= 0:
            raise ValueError("The video has no valid frame rate")
        limit = min(total, max_frames)
        ok, frame = capture.read()
        if not ok:
            raise ValueError("Could not read the first frame")
        previous = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        records = []
        processed = 1
        for number in range(1, limit):
            if cancel is not None and cancel.is_set():
                break
            ok, frame = capture.read()
            if not ok:
                break
            current = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            points = cv2.goodFeaturesToTrack(previous, maxCorners=300, qualityLevel=.01, minDistance=10, blockSize=7)
            if points is not None:
                tracked, status, _ = cv2.calcOpticalFlowPyrLK(previous, current, points, None)
                if tracked is not None and status is not None:
                    valid = status.reshape(-1) == 1
                    old, new = points.reshape(-1, 2)[valid], tracked.reshape(-1, 2)[valid]
                    finite = np.isfinite(old).all(axis=1) & np.isfinite(new).all(axis=1)
                    old, new = old[finite], new[finite]
                    if len(old) >= 8:
                        transform, inliers = cv2.estimateAffinePartial2D(old, new, method=cv2.RANSAC, ransacReprojThreshold=3)
                        count = int(inliers.sum()) if inliers is not None else 0
                        if transform is not None and np.isfinite(transform).all() and count >= 8 and count / len(old) >= .5:
                            dx, dy = float(transform[0, 2]), float(transform[1, 2])
                            records.append(dict(frame=number, dx=dx, dy=dy, motion=math.hypot(dx, dy), inliers=count))
            previous = current
            processed = number + 1
            if progress:
                progress(processed, limit, "Checking camera motion")
        motions = [row["motion"] for row in records]
        return dict(processed_frames=processed, source_frames=total, requested_frames=limit,
                    stopped=processed < limit, fps=fps, records=records,
                    mean=float(np.mean(motions)) if motions else None,
                    p95=float(np.percentile(motions, 95)) if motions else None,
                    maximum=max(motions) if motions else None)
    finally:
        capture.release()
