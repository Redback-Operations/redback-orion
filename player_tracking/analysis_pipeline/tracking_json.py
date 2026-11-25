"""Convert the tracks CSV into the formats the T1 analytics read.

detect_and_track.py writes one tracks CSV. Older stages expect either the
JSON shape /tracking has always returned (to_legacy_json) or a per-player
table with centre points and timestamps (write_player_table).
"""

import csv
from collections import defaultdict

PLAYER_TABLE_COLUMNS = [
    "frame_id", "timestamps_s", "timestamp_s", "player_id", "cx", "cy",
    "x1", "y1", "x2", "y2", "w", "h", "confidence",
]


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


def write_player_table(legacy: dict, path) -> None:
    """Write one row per player per frame from to_legacy_json() output.

    Has the columns tackle detection, workload and heatmaps need. frame_id
    is the 1-based frame_number, matching the CSV the backend builds for
    /tackle. timestamps_s and timestamp_s hold the same value because
    different T1 scripts use different names.
    """
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(PLAYER_TABLE_COLUMNS)
        for frame in legacy["tracking_results"]:
            for p in frame["players"]:
                box = p["bbox"]
                writer.writerow([
                    frame["frame_number"], frame["timestamp"], frame["timestamp"],
                    p["player_id"], p["center"]["x"], p["center"]["y"],
                    box["x1"], box["y1"], box["x2"], box["y2"],
                    p["width"], p["height"], p["confidence"],
                ])
