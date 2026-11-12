from pathlib import Path

import cv2
from ultralytics import YOLO

from config import COUNT_CLASS_PREFERENCE, DEFAULT_MAX_DET, MODEL_CLASS_OVERRIDES
from tiling import detect_tiled

def load_model(model_path):
    """Load a YOLO model. Accepts a filesystem path or a bare Ultralytics name.
 
    A local path is validated up front so a missing weight fails clearly; a bare
    name is handed to Ultralytics, which resolves/downloads it on first load.
    """
    s = str(model_path)
    is_local = ("/" in s) or ("\\" in s)
    if is_local:
        p = Path(model_path)
        if not p.is_file():
            raise FileNotFoundError(f"Model not found: {p}")
    return YOLO(s)

def target_class(model, label=None, preference=COUNT_CLASS_PREFERENCE):
    """Resolve a countable class by name rather than a hardcoded index.

    Indices differ between weights, so the same integer means 'person' in one
    model and something else in another. Returns (class_id, class_name) so
    callers can report which class was counted: a person count and a head
    count are different quantities and comparing them blind is meaningless.

    label is the MODELS key, used to look up a MODEL_CLASS_OVERRIDES entry.
    Callers that have it should pass it.
    """
    if label in MODEL_CLASS_OVERRIDES:
        cid, cname = MODEL_CLASS_OVERRIDES[label]
        if cid not in model.names:
            raise ValueError(
                f"Override class {cid} for '{label}' not in model classes {model.names}"
            )
        return cid, cname
 
    for name in preference:
        cid = next((i for i, n in model.names.items() if n == name), None)
        if cid is not None:
            return cid, name
    if len(model.names) == 1:
        only_id = next(iter(model.names))
        return only_id, model.names[only_id]
    raise ValueError(
        f"No countable class {preference} found; model classes are {model.names}. "
        f"If this weight has unnamed classes, add a MODEL_CLASS_OVERRIDES entry "
        f"for '{label}' after confirming the mapping with --diagnose."
    )

def read_frames(video_path, n_frames):
    video_path = Path(video_path)
    if not video_path.is_file():
        raise FileNotFoundError(f"Video not found: {video_path}")
    cap = cv2.VideoCapture(str(video_path))
    frames = []
    while len(frames) < n_frames:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()
    if not frames:
        raise RuntimeError(
            f"No frames read from {video_path}. Check the file is a valid, readable video."
        )
    return frames

def count_frame(model, frame, cid, conf, iou, tiled=False):
    """Count target-class detections in one frame, tiled or whole-frame."""
    if tiled:
        boxes, _ = detect_tiled(model, frame, cid, conf=conf, iou=iou)
        return len(boxes)
    r = model(frame, conf=conf, iou=iou, max_det=DEFAULT_MAX_DET, verbose=False)[0]
    return sum(1 for b in r.boxes if int(b.cls[0]) == cid)

def model_device(model):
    """Where the weights actually sit. model.device is unreliable until a
    predictor is attached, so read it from the torch module directly."""
    return str(next(model.model.parameters()).device)