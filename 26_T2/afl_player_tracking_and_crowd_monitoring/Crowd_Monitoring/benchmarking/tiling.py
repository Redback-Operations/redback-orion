import math

import torch
from torchvision.ops import nms

from config import (
    DEFAULT_CONF,
    DEFAULT_IOU,
    DEFAULT_MAX_DET,
    TILE_OVERLAP,
    TILE_SIZE,
    TILE_BATCH,
)

def tile_grid(w, h, tile=TILE_SIZE, overlap=TILE_OVERLAP):
    """Top-left origins of tiles covering a w x h frame.

    Tiles are a fixed size and slide by stride = tile - overlap. Origins are
    distributed evenly across the frame rather than stepping by exact stride and
    clamping the last one, so overlap stays uniform instead of concentrating at
    the right and bottom edges.
    """
    if overlap >= tile:
        raise ValueError(f"TILE_OVERLAP ({overlap}) must be < TILE_SIZE ({tile})")
    stride = tile - overlap
    n_x = max(math.ceil((w - overlap) / stride), 1)
    n_y = max(math.ceil((h - overlap) / stride), 1)
    xs = [round(i * max(w - tile, 0) / max(n_x - 1, 1)) for i in range(n_x)]
    ys = [round(i * max(h - tile, 0) / max(n_y - 1, 1)) for i in range(n_y)]
    return [(x, y) for y in ys for x in xs]

def detect_tiled(model, frame, cid, conf=DEFAULT_CONF, iou=DEFAULT_IOU,
                 tile=TILE_SIZE, overlap=TILE_OVERLAP, batch=TILE_BATCH):
    """Run inference per tile, reproject boxes to full-frame coordinates, then
    NMS globally to collapse detections duplicated in the overlap regions.
 
    Returns (boxes_xyxy, scores) for the target class ONLY. Tiles are batched to
    amortise per-call overhead; on CPU the win is modest since the forward pass
    dominates.
 
    WARNING: this will always find MORE boxes than untiled inference. More boxes
    is not automatically more accurate. The extra detections may be genuine
    small heads recovered from full resolution, or seam duplicates and false
    positives. Those two cases are indistinguishable from the count alone.
    Validate against hand-labelled frames (--truth) before concluding anything.
    """
    h, w = frame.shape[:2]
    if w <= tile and h <= tile:
        print(f"  NOTE: frame is {w}x{h}, not larger than tile ({tile})."
              f" Tiling is a no-op here and adds nothing over untiled inference.")
    origins = tile_grid(w, h, tile, overlap)
    boxes, scores = [], []
 
    for i in range(0, len(origins), batch):
        chunk = origins[i:i + batch]
        crops = [frame[y:y + tile, x:x + tile] for x, y in chunk]
        results = model(crops, conf=conf, iou=iou,
                        max_det=DEFAULT_MAX_DET, verbose=False)
        for (x, y), r in zip(chunk, results):
            if not len(r.boxes):
                continue
            m = r.boxes.cls == cid
            if not m.any():
                continue
            b = r.boxes.xyxy[m].clone()
            b[:, [0, 2]] += x
            b[:, [1, 3]] += y
            boxes.append(b)
            scores.append(r.boxes.conf[m])
 
    if not boxes:
        return torch.zeros((0, 4)), torch.zeros((0,))
    boxes, scores = torch.cat(boxes), torch.cat(scores)
    keep = nms(boxes, scores, iou)  # cross-tile dedupe in the overlap regions
    return boxes[keep], scores[keep]