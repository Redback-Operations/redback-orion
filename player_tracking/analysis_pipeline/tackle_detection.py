"""Tackle detection: find moments where several players crowd together.

A frame counts as a tackle frame when enough players stand close to each
other. Consecutive tackle frames are grouped into events. This is the logic
player_service's /tackle endpoint has always run (based on Shafqat Ullah's
T1 tackle detection, now in archive/player_tracking_legacy/).

Input is a tracks table with one row per player per frame and the columns
frame_id, player_id, cx, cy, x1, y1, x2, y2, timestamps_s.
"""

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = {"frame_id", "player_id", "cx", "cy", "x1", "y1", "x2", "y2", "timestamps_s"}

DIST_THRESHOLD = 100      # pixels between two players to count as close
MIN_INTERACTIONS = 8      # close pairs needed in a frame
MIN_PLAYERS = 4           # players needed in a frame
DENSITY_THRESHOLD = 1.2   # close pairs per player
MIN_EVENT_LENGTH = 5      # frames an event must last
MAX_FRAME_GAP = 10        # frames allowed between tackle frames in one event


def cluster_score(group: pd.DataFrame) -> int:
    """Count pairs of players closer than DIST_THRESHOLD."""
    players = group[["cx", "cy"]].values
    score = 0
    for i in range(len(players)):
        for j in range(i + 1, len(players)):
            if np.linalg.norm(players[i] - players[j]) < DIST_THRESHOLD:
                score += 1
    return score


def group_frames(frames, max_gap: int = 3):
    """Split sorted frame numbers into runs where gaps are at most max_gap."""
    if not frames:
        return []
    frames = sorted(frames)
    grouped = []
    current = [frames[0]]
    for f in frames[1:]:
        if f <= current[-1] + max_gap:
            current.append(f)
        else:
            grouped.append(current)
            current = [f]
    grouped.append(current)
    return grouped


def detect_tackles(df: pd.DataFrame):
    """Return (tackle frames DataFrame, list of tackle events)."""
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in CSV: {missing}")

    results = []
    for frame_id, group in df.groupby("frame_id"):
        num_players = group["player_id"].nunique()
        if num_players < MIN_PLAYERS:
            continue
        score = cluster_score(group)
        density_ratio = score / (num_players + 1)
        if score >= MIN_INTERACTIONS and density_ratio > DENSITY_THRESHOLD:
            results.append({
                "frame_id": int(frame_id),
                "timestamp_s": float(group["timestamps_s"].mean()),
                "cluster_score": int(score),
                "density_ratio": float(density_ratio),
                "players": int(num_players),
                "x_min": float(group["x1"].min()),
                "y_min": float(group["y1"].min()),
                "x_max": float(group["x2"].max()),
                "y_max": float(group["y2"].max()),
            })

    frame_df = pd.DataFrame(results)
    events = []
    if not frame_df.empty:
        tackle_events = group_frames(frame_df["frame_id"].tolist(), MAX_FRAME_GAP)
        for idx, event_frames in enumerate(tackle_events, start=1):
            if len(event_frames) < MIN_EVENT_LENGTH:
                continue
            eg = df[df["frame_id"].isin(event_frames)]
            fd = frame_df[frame_df["frame_id"].isin(event_frames)]
            avg_score = fd["cluster_score"].mean()
            events.append({
                "event_id": idx,
                "event_type": "multi_player_tackle",
                "start_frame": int(event_frames[0]),
                "end_frame": int(event_frames[-1]),
                "start_time_s": float(eg["timestamps_s"].min()),
                "end_time_s": float(eg["timestamps_s"].max()),
                "duration_frames": int(event_frames[-1] - event_frames[0] + 1),
                "players_involved": int(eg["player_id"].nunique()),
                "cluster_score": float(avg_score),
                "bounding_box": {
                    "x_min": float(eg["x1"].min()),
                    "y_min": float(eg["y1"].min()),
                    "x_max": float(eg["x2"].max()),
                    "y_max": float(eg["y2"].max()),
                },
                "confidence": round(min(avg_score / 15, 1.0), 2),
            })
    return frame_df, events
