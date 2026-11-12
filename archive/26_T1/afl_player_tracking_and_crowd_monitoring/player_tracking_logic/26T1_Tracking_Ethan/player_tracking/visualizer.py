from typing import Dict, List

import cv2
import numpy as np

from .geometry import bbox_to_int
from .tracker import Track


_PALETTE = [
    (255, 120, 80),
    (80, 180, 255),
    (120, 220, 120),
    (220, 160, 255),
    (255, 210, 80),
    (120, 255, 220),
    (255, 120, 180),
    (180, 180, 255),
]


def colour_for_id(track_id: int):
    return _PALETTE[int(track_id) % len(_PALETTE)]


def colour_for_cluster(cluster_id, fallback_id: int):
    if cluster_id is None:
        return colour_for_id(fallback_id)
    return _PALETTE[int(cluster_id) % len(_PALETTE)]


def draw_tracks(frame: np.ndarray, tracks: Dict[int, Track], draw_confidence: bool = True) -> np.ndarray:
    """
    Online visualisation for active tracks. The final output video uses draw_frame_records
    after jersey clusters are assigned.
    """
    output = frame.copy()

    for track_id, track in tracks.items():
        if track.missing > 0:
            continue

        colour = colour_for_id(track_id)
        x1, y1, x2, y2 = bbox_to_int(track.bbox)

        cv2.rectangle(output, (x1, y1), (x2, y2), colour, 2)

        label = f"ID {track_id} | {track.initial_class_name}"
        if draw_confidence:
            label += f" | {track.current_conf:.2f}"

        label_y = max(20, y1 - 8)
        cv2.putText(
            output,
            label,
            (x1, label_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            colour,
            2,
            cv2.LINE_AA,
        )

        if len(track.trail) >= 2:
            points = [(int(round(x)), int(round(y))) for x, y in track.trail]
            for p1, p2 in zip(points[:-1], points[1:]):
                cv2.line(output, p1, p2, colour, 2)

        cx, cy = int(round(track.center[0])), int(round(track.center[1]))
        cv2.circle(output, (cx, cy), 3, colour, -1)

    return output


def draw_frame_records(
    frame: np.ndarray,
    records: List[Dict],
    trails: Dict[int, List],
    trail_length: int,
    draw_confidence: bool = True,
    draw_cluster: bool = True,
) -> np.ndarray:
    """
    Draw final frame annotations using saved per-frame track records.
    This allows the output video to show the final KMeans cluster labels.
    """
    output = frame.copy()

    for record in records:
        track_id = int(record["track_id"])
        cluster_id = record.get("cluster_id")
        colour = colour_for_cluster(cluster_id, track_id)

        x1, y1, x2, y2 = bbox_to_int(record["bbox"])
        cv2.rectangle(output, (x1, y1), (x2, y2), colour, 2)

        if draw_cluster:
            label = f"ID {track_id} | {record.get('cluster_team', 'Unknown')}"
        else:
            label = f"ID {track_id}"

        fixed_class = record.get("fixed_initial_class_name")
        if fixed_class:
            label += f" | {fixed_class}"

        if draw_confidence:
            label += f" | {float(record.get('confidence', 0.0)):.2f}"

        label_y = max(20, y1 - 8)
        cv2.putText(
            output,
            label,
            (x1, label_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            colour,
            2,
            cv2.LINE_AA,
        )

        center = record.get("center")
        if center is not None:
            cx, cy = int(round(center[0])), int(round(center[1]))
            trails.setdefault(track_id, []).append((cx, cy))
            if len(trails[track_id]) > trail_length:
                trails[track_id] = trails[track_id][-trail_length:]

            if len(trails[track_id]) >= 2:
                for p1, p2 in zip(trails[track_id][:-1], trails[track_id][1:]):
                    cv2.line(output, p1, p2, colour, 2)

            cv2.circle(output, (cx, cy), 3, colour, -1)

    return output
