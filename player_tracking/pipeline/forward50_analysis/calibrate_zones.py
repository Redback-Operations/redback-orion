"""Interactively calibrate the Forward-50 boundary and five zones."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import numpy as np

SHAPES = [
    "forward50",
    "left_pocket",
    "left_half_forward",
    "central_corridor",
    "right_half_forward",
    "right_pocket",
]


def normalized(points, width: int, height: int) -> list[list[float]]:
    return [[round(x / width, 6), round(y / height, 6)] for x, y in points]


def calibrate(video_path: Path, config_path: Path, time_seconds: float) -> None:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise FileNotFoundError(f"Could not open video: {video_path}")
    capture.set(cv2.CAP_PROP_POS_MSEC, time_seconds * 1000)
    ok, frame = capture.read()
    capture.release()
    if not ok:
        raise RuntimeError("Could not read the calibration frame")

    height, width = frame.shape[:2]
    completed: dict[str, list[tuple[int, int]]] = {}
    current: list[tuple[int, int]] = []
    shape_index = 0
    window = "Forward-50 calibration"

    def on_mouse(event, x, y, _flags, _data):
        if event == cv2.EVENT_LBUTTONDOWN:
            current.append((x, y))

    cv2.namedWindow(window, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(window, on_mouse)

    while shape_index < len(SHAPES):
        display = frame.copy()
        for name, points in completed.items():
            polygon = np.asarray(points, dtype=np.int32)
            cv2.polylines(display, [polygon], True, (90, 220, 90), 2)
            centre = polygon.mean(axis=0).astype(int)
            cv2.putText(display, name.replace("_", " "), tuple(centre),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (90, 220, 90), 2)
        if current:
            polygon = np.asarray(current, dtype=np.int32)
            cv2.polylines(display, [polygon], False, (0, 220, 255), 2)
            for point in current:
                cv2.circle(display, point, 5, (0, 220, 255), -1)

        name = SHAPES[shape_index]
        instruction = f"Click {name} clockwise | Enter: save | U: undo | Esc: cancel"
        cv2.rectangle(display, (0, 0), (width, 45), (0, 0, 0), -1)
        cv2.putText(display, instruction, (15, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.75, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.imshow(window, display)
        key = cv2.waitKey(25) & 0xFF
        if key in (13, 10):
            if len(current) < 3:
                print("A polygon needs at least three points.")
                continue
            completed[name] = current.copy()
            current.clear()
            shape_index += 1
        elif key in (ord("u"), 8):
            if current:
                current.pop()
        elif key == 27:
            cv2.destroyAllWindows()
            print("Calibration cancelled; configuration was not changed.")
            return

    cv2.destroyAllWindows()
    config["forward50_polygon_normalized"] = normalized(completed["forward50"], width, height)
    config["zones_normalized"] = {
        name: normalized(completed[name], width, height) for name in SHAPES[1:]
    }
    config["calibration"] = {
        "video": video_path.name,
        "frame_width": width,
        "frame_height": height,
        "time_seconds": time_seconds,
        "method": "manual polygons drawn clockwise on a stable-camera frame",
    }
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    print(f"Saved calibrated polygons to {config_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument("--config", type=Path, default=Path("config.json"))
    parser.add_argument("--time", type=float, default=0.0)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    calibrate(args.video, args.config, args.time)

