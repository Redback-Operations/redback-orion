from typing import Dict

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
    return _PALETTE[track_id % len(_PALETTE)]


def draw_tracks(frame: np.ndarray, tracks: Dict[int, Track], draw_confidence: bool = True) -> np.ndarray:
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
