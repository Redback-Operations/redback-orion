from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Callable

from .core import TrackRow


def extract_track_crops(
    video_path: str | Path,
    rows: list[TrackRow],
    output_folder: str | Path,
    samples_per_track: int = 5,
    progress: Callable[[str], None] | None = None,
) -> dict[str, list[Path]]:
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("OpenCV is not installed") from exc

    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    grouped: defaultdict[str, list[TrackRow]] = defaultdict(list)
    for row in rows:
        if row.x2 > row.x1 and row.y2 > row.y1:
            grouped[row.track_id].append(row)

    chosen: defaultdict[int, list[TrackRow]] = defaultdict(list)
    for track_rows in grouped.values():
        ordered = sorted(track_rows, key=lambda item: item.frame)
        count = min(samples_per_track, len(ordered))
        indices = {round(index * (len(ordered) - 1) / max(count - 1, 1)) for index in range(count)}
        for index in sorted(indices):
            chosen[ordered[index].frame].append(ordered[index])

    cap = cv2.VideoCapture(str(video_path))
    results: defaultdict[str, list[Path]] = defaultdict(list)
    try:
        for frame_number in sorted(chosen):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ok, frame = cap.read()
            if not ok:
                continue
            height, width = frame.shape[:2]
            for row in chosen[frame_number]:
                x1 = max(0, min(width - 1, int(row.x1)))
                y1 = max(0, min(height - 1, int(row.y1)))
                x2 = max(x1 + 1, min(width, int(row.x2)))
                y2 = max(y1 + 1, min(height, int(row.y2)))
                crop = frame[y1:y2, x1:x2]
                if crop.size == 0:
                    continue
                track_folder = output_folder / f"track_{row.track_id}"
                track_folder.mkdir(exist_ok=True)
                path = track_folder / f"frame_{frame_number}.jpg"
                cv2.imwrite(str(path), crop)
                results[row.track_id].append(path)
            if progress:
                progress(f"Extracting player crops at frame {frame_number}")
    finally:
        cap.release()
    return dict(results)


def suggest_teams(
    crop_paths: dict[str, list[Path]],
    class_names: dict[str, str],
) -> dict[str, str]:
    try:
        import cv2
        import numpy as np
        from sklearn.cluster import KMeans
    except ImportError as exc:
        raise RuntimeError("Install OpenCV and scikit learn to sort teams") from exc

    direct: dict[str, str] = {}
    features: list[list[float]] = []
    track_ids: list[str] = []
    ignored = {"PLAYER", "PERSON", "REF", "REFEREE", "UMPIRE"}
    for track_id, class_name in class_names.items():
        if class_name.upper() not in ignored:
            direct[track_id] = class_name

    for track_id, paths in crop_paths.items():
        if track_id in direct or class_names.get(track_id, "").upper() in {"REF", "REFEREE", "UMPIRE"}:
            continue
        samples = []
        for path in paths:
            image = cv2.imread(str(path))
            if image is None:
                continue
            height, width = image.shape[:2]
            torso = image[int(height * 0.12):int(height * 0.58), int(width * 0.15):int(width * 0.85)]
            if torso.size == 0:
                continue
            hsv = cv2.cvtColor(torso, cv2.COLOR_BGR2HSV)
            samples.append(np.median(hsv.reshape(-1, 3), axis=0))
        if samples:
            features.append(np.median(np.array(samples), axis=0).tolist())
            track_ids.append(track_id)

    if len(features) >= 2:
        labels = KMeans(n_clusters=2, random_state=42, n_init=10).fit_predict(features)
        for track_id, label in zip(track_ids, labels):
            direct[track_id] = f"Team {int(label) + 1}"
    elif len(features) == 1:
        direct[track_ids[0]] = "Team 1"
    return direct
