#!/usr/bin/env python3
"""Render reviewed frames with numbered boxes for crowd-box auditing.

Draws every box from the label file; boxes whose center-y < --suspect-below
are drawn red with a big index, the rest green/dim. Tiled into contact sheets
so they can be visually audited in batches.

Usage:
    python scripts/audit_labels.py \
        --images data/raw/broadcast_stkilda_northmelbourne/reviewed/images \
        --labels data/raw/broadcast_stkilda_northmelbourne/reviewed/labels \
        --out /tmp/audit
"""

import argparse
import math
from pathlib import Path

import cv2
import numpy as np

TILE_W, TILE_H = 960, 540
COLS, ROWS = 3, 2
SHEET_W, SHEET_H = COLS * TILE_W, ROWS * (TILE_H + 30)


def load_boxes(label_path: Path):
    boxes = []
    if label_path.exists():
        for line in label_path.read_text().splitlines():
            parts = line.split()
            if len(parts) < 5:
                continue
            cls, xc, yc, w, h = map(float, parts[:5])
            boxes.append((int(cls), xc, yc, w, h))
    return boxes


def render_tile(img_path: Path, boxes, suspect_below: float):
    img = cv2.imread(str(img_path))
    if img is None:
        return np.full((TILE_H, TILE_W, 3), 40, np.uint8)
    H, W = img.shape[:2]
    scale = min(TILE_W / W, TILE_H / H)
    disp = cv2.resize(img, (int(W * scale), int(H * scale)))
    canvas = np.full((TILE_H, TILE_W, 3), 30, np.uint8)
    y0 = (TILE_H - disp.shape[0]) // 2
    x0 = (TILE_W - disp.shape[1]) // 2
    canvas[y0:y0 + disp.shape[0], x0:x0 + disp.shape[1]] = disp

    for i, (cls, xc, yc, w, h) in enumerate(boxes):
        x1 = int(x0 + (xc - w / 2) * W * scale)
        y1 = int(y0 + (yc - h / 2) * H * scale)
        x2 = int(x0 + (xc + w / 2) * W * scale)
        y2 = int(y0 + (yc + h / 2) * H * scale)
        suspect = yc < suspect_below
        color = (60, 60, 230) if suspect else (60, 180, 60)
        thick = 2 if suspect else 1
        cv2.rectangle(canvas, (x1, y1), (x2, y2), color, thick)
        if suspect:
            cv2.putText(canvas, str(i), (x1, max(20, y1 - 4)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (60, 60, 230), 2)
    return canvas


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--images", type=Path, required=True)
    p.add_argument("--labels", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--suspect-below", type=float, default=0.55,
                   help="boxes with center-y below this are drawn red+indexed")
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    img_files = sorted(args.images.glob("*.jpg"))
    tiles = []
    for img_path in img_files:
        boxes = load_boxes(args.labels / (img_path.stem + ".txt"))
        if not any(yc < args.suspect_below for _, _, yc, _, _ in boxes):
            continue  # no suspects -> nothing to audit
        tile = render_tile(img_path, boxes, args.suspect_below)
        header = np.full((30, TILE_W, 3), 15, np.uint8)
        cv2.putText(header, img_path.stem, (5, 22), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (200, 200, 200), 1)
        tiles.append(np.vstack([header, tile]))

    per_sheet = COLS * ROWS
    for s in range(math.ceil(len(tiles) / per_sheet)):
        sheet = np.full((SHEET_H, SHEET_W, 3), 20, np.uint8)
        for j, tile in enumerate(tiles[s * per_sheet:(s + 1) * per_sheet]):
            r, c = divmod(j, COLS)
            sheet[r * (TILE_H + 30):(r + 1) * (TILE_H + 30),
                  c * TILE_W:(c + 1) * TILE_W] = tile
        out = args.out / f"sheet_{s:02d}.jpg"
        cv2.imwrite(str(out), sheet, [cv2.IMWRITE_JPEG_QUALITY, 90])
        print(out)


if __name__ == "__main__":
    main()
