"""Click polygons on a frame and print normalised coordinates for
shared/config/crowd_region_preprocessing_config.json.

    python -m crowd_region_preprocessing.pick_region [IMAGE]

IMAGE defaults to the first extracted frame. Coordinates are printed as
fractions of width/height, so they survive any resolution change.

Controls
    left click     add a point to the current polygon
    right click    close the current polygon, start a new one
    u              undo last point of the current polygon
    d              delete the last completed polygon
    n              start a new polygon
    r              reset - clear every polygon
    s / Enter      finish: print JSON for keep or exclude use
    q / Esc        quit without printing
"""

from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

import cv2
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _default_image() -> str | None:
    # raw extracted frames first - focused_frames are already masked and would
    # show the previous run's black bars
    for pattern in (
        "video_processing/data/extracted_frames/*.jpg",
        "crowd_region_preprocessing/output/focused_frames/*.jpg",
    ):
        hits = sorted(glob.glob(str(PROJECT_ROOT / pattern)))
        if hits:
            return hits[0]
    return None


def main() -> int:
    image_path = sys.argv[1] if len(sys.argv) > 1 else _default_image()
    if not image_path or not Path(image_path).is_file():
        print("No image found. Pass one: python -m crowd_region_preprocessing.pick_region <image>")
        return 1

    frame = cv2.imread(image_path)
    if frame is None:
        print(f"Could not read {image_path}")
        return 1
    h, w = frame.shape[:2]

    view_scale = min(1.0, 1600 / w)
    view_w, view_h = int(w * view_scale), int(h * view_scale)

    polygons: list[list[tuple[int, int]]] = [[]]

    def on_mouse(event, x, y, _flags, _param):
        pt = (int(x / view_scale), int(y / view_scale))
        if event == cv2.EVENT_LBUTTONDOWN:
            polygons[-1].append(pt)
        elif event == cv2.EVENT_RBUTTONDOWN and polygons[-1]:
            polygons.append([])

    window = "pick_region  (Lclick add . Rclick close . u undo pt . d del polygon . n new . r reset all . s print . q quit)"
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window, view_w, view_h)
    cv2.setMouseCallback(window, on_mouse)

    while True:
        canvas = frame.copy()
        for i, poly in enumerate(polygons):
            if not poly:
                continue
            colour = (0, 200, 0) if i % 2 == 0 else (0, 165, 255)
            pts = np.array(poly, dtype=np.int32).reshape(-1, 1, 2)
            for (px, py) in poly:
                cv2.circle(canvas, (px, py), 6, colour, -1)
            is_current = poly is polygons[-1]
            cv2.polylines(canvas, [pts], not is_current, colour, 2)
            if not is_current and len(poly) >= 3:
                overlay = canvas.copy()
                cv2.fillPoly(overlay, [pts], colour)
                canvas = cv2.addWeighted(overlay, 0.25, canvas, 0.75, 0)

        done = sum(1 for p in polygons if len(p) >= 3)
        cv2.putText(canvas, f"{done} polygon(s) | pts in current: {len(polygons[-1])}",
                    (20, 44), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 255, 255), 3)

        view = cv2.resize(canvas, (view_w, view_h), interpolation=cv2.INTER_AREA)
        cv2.imshow(window, view)

        key = cv2.waitKey(20) & 0xFF
        ch = chr(key).lower() if 32 <= key < 127 else ""

        if ch == "q" or key == 27:
            cv2.destroyAllWindows()
            return 0
        if ch == "u" and polygons[-1]:
            polygons[-1].pop()
        elif ch == "d":
            # remove the most recent polygon that has any points
            for i in range(len(polygons) - 1, -1, -1):
                if polygons[i]:
                    polygons.pop(i)
                    break
            if not polygons:
                polygons.append([])
            print(f"[pick_region] deleted a polygon -> {sum(1 for p in polygons if p)} left")
        elif ch == "n" and polygons[-1]:
            polygons.append([])
        elif ch == "r":
            polygons[:] = [[]]           # in-place so the mouse callback sees it
            print("[pick_region] reset - all polygons cleared")
        elif ch == "s" or key == 13:
            break

    cv2.destroyAllWindows()
    result = [
        [[round(x / w, 4), round(y / h, 4)] for (x, y) in poly]
        for poly in polygons
        if len(poly) >= 3
    ]
    if not result:
        print("No complete polygons (need >= 3 points each).")
        return 1

    line = json.dumps(result)
    print(f"\n# from {image_path}  ({w}x{h}) - {len(result)} polygon(s)")
    print("Trace the fixed structures to REMOVE (roof, signage, concourse, foreground rails).")
    print(f'  "exclude_polygons_normalized": {line}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
