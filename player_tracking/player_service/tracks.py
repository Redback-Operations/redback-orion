"""Tracking results for an uploaded video, reused by file hash.

/tracking stores its result here. Any endpoint that needs tracks calls
get_tracks() with the same video: if tracking already ran on that file the
saved result is reused, otherwise tracking runs first. Calling an endpoint
on its own is slower but never fails for lack of tracks.
"""

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Callable


def file_hash(path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def get_tracks(video_path, tracks_dir: Path, run_tracking: Callable[[Path, Path, str], dict]) -> dict:
    """Return the tracking result for this video, running tracking if needed.

    run_tracking(video_path, tracks_dir, key) must write its files into
    tracks_dir and return a JSON-serialisable result.
    """
    key = file_hash(video_path)
    saved = Path(tracks_dir) / f"{key}.json"
    if saved.exists():
        return json.loads(saved.read_text())

    # ponytail: two requests for the same new video at the same moment both run
    # tracking. The result is identical, just wasted work. Add a lock per key
    # if that becomes common.
    result = run_tracking(Path(video_path), Path(tracks_dir), key)
    part = saved.with_name(saved.name + ".part")
    part.write_text(json.dumps(result))
    part.replace(saved)  # never leave a half-written result for the next request
    return result


def to_legacy_json(csv_path, info: dict) -> dict:
    """Convert a tracks CSV to the JSON shape /tracking has always returned.

    The backend and the T1 analytics read this shape: video_info plus one
    entry per processed frame, each with a list of players.
    """
    fps = info["fps"]
    name_to_id = {name: int(i) for i, name in info["class_names"].items()}
    by_frame = defaultdict(list)
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            x1, y1, x2, y2 = (float(row[k]) for k in ("x1", "y1", "x2", "y2"))
            by_frame[int(row["frame"])].append({
                "player_id": int(row["track_id"]),
                "team_id": name_to_id.get(row["class"], -1),
                "team_name": row["class"],
                "bbox": {"x1": int(x1), "y1": int(y1), "x2": int(x2), "y2": int(y2)},
                "center": {"x": int((x1 + x2) / 2), "y": int((y1 + y2) / 2)},
                "confidence": round(float(row["confidence"]), 2),
                "width": int(x2 - x1),
                "height": int(y2 - y1),
            })

    start = info.get("start_frame", 0)
    frames = range(start, start + info["processed_frames"])
    return {
        "video_info": {
            "duration": info["total_frames"] / fps if fps else 0,
            "fps": int(fps),
            "total_frames": info["total_frames"],
            "resolution": [info["width"], info["height"]],
        },
        "tracking_results": [
            {
                "frame_number": frame + 1,
                "timestamp": round(frame / fps, 3) if fps else 0,
                "players": by_frame.get(frame, []),
            }
            for frame in frames
        ],
    }
