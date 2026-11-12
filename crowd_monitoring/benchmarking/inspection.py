from collections import Counter
from pathlib import Path

import cv2

from config import (
    DEFAULT_CONF,
    DEFAULT_IOU,
    DEFAULT_MAX_DET,
    DEFAULT_SHOW_SCALE,
    MODEL_CLASS_OVERRIDES,
    TILE_OVERLAP,
    TILE_SIZE,
)
from core import load_model, model_device, read_frames, target_class
from tiling import detect_tiled, tile_grid

def visualise(label, model_path, video_paths, conf=DEFAULT_CONF, iou=DEFAULT_IOU,
              save=False, max_frames=None, show_scale=DEFAULT_SHOW_SCALE,
              tiled=False):
    """Play each video with detections drawn, and/or save annotated copies.

    Videos play back to back through separate captures. Press q to close the
    current clip's window, which also skips the remaining clips.

    Lower conf (0.10 or so) to see what an under-confident stock model is
    actually perceiving. At 0.35 it may draw nothing at all; that is the
    calibration result, not a bug.

    tiled=True is the quickest way to eyeball whether cross-tile NMS is
    working: look for boxes clustering along tile seams, or objects
    double-boxed in the overlap regions. Playback is very slow, one forward
    pass per tile.
    """
    model = load_model(model_path)
    cid, cname = target_class(model, label)
 
    quit_all = False
    for video_path in video_paths:
        if quit_all:
            break
 
        cap = cv2.VideoCapture(str(Path(video_path)))
        if not cap.isOpened():
            print(f"skipped (cannot open): {video_path}")
            continue
 
        writer = None
        if save:
            fps = cap.get(cv2.CAP_PROP_FPS) or 25
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            # Tag output with both model and clip so multiple videos don't clash.
            out_path = Path(
                f"annotated_{Path(model_path).stem}_{Path(video_path).stem}"
                f"{'_tiled' if tiled else ''}.mp4"
            )
            writer = cv2.VideoWriter(
                str(out_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h)
            )
 
        i = 0
        while True:
            ret, frame = cap.read()
            if not ret or (max_frames and i >= max_frames):
                break
 
            if tiled:
                boxes, _ = detect_tiled(model, frame, cid, conf=conf, iou=iou)
                annotated = frame.copy()
                for x1, y1, x2, y2 in boxes.tolist():
                    cv2.rectangle(annotated, (int(x1), int(y1)),
                                  (int(x2), int(y2)), (0, 0, 255), 2)
                count = len(boxes)
            else:
                r = model(frame, conf=conf, iou=iou,
                          max_det=DEFAULT_MAX_DET, verbose=False)[0]
                # labels off: at crowd density they are unreadable, and drawing
                # them per-box in Python is a real cost on a 4K frame.
                annotated = r.plot(labels=False, conf=False)
                count = sum(1 for b in r.boxes if int(b.cls[0]) == cid)
 
            # Drawn BEFORE the display resize so the text stays readable.
            cv2.putText(
                annotated,
                f"{label}  {Path(video_path).name}  {cname}={count}  "
                f"conf>={conf}{'  TILED' if tiled else ''}",
                (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2,
            )
 
            if writer:
                writer.write(annotated)  # saved output stays full resolution
 
            # Display-only downscale so a 4K frame fits on screen. Does not
            # affect inference or the saved file.
            display = annotated
            if show_scale != 1.0:
                display = cv2.resize(
                    annotated, None, fx=show_scale, fy=show_scale,
                    interpolation=cv2.INTER_AREA,
                )
 
            cv2.imshow("detections (press q to quit)", display)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                quit_all = True
                break
            i += 1
 
        cap.release()
        if writer:
            writer.release()
            print(f"saved: {out_path}")
 
    cv2.destroyAllWindows()

def diagnose(label, model_path, video_paths):
    """Inspect one model: its class map, and what it detects on the first frame
    of each video across a few confidence thresholds. Use this to understand a
    0-count result. It tells you whether the model sees nothing (capability
    gap) or sees things it doesn't class as your target (filter/ordering issue).
 
    Also prints median box height per class. That is how you confirm an unnamed
    class map: on the same footage the taller boxes are bodies, the shorter ones
    are heads or faces (head:body ~1:7.5, face:body ~1:15). Check this before
    committing a MODEL_CLASS_OVERRIDES entry. Wrong index counts the wrong
    thing without erroring.
    """
    model = load_model(model_path)
    print(f"[{label}]")
    print("classes:", model.names)
 
    # Training input size travels with the weights. A model trained at 960 or
    # 1280 quadruples pixel count vs 640; either way a 4K frame is downscaled
    # heavily before it reaches the network, which is the case for tiling.
    args = getattr(model.model, "args", {}) or {}
    if not isinstance(args, dict):
        args = vars(args)
    print("imgsz:", model.overrides.get("imgsz"), "|", args.get("imgsz"))
    print("device:", model_device(model))
 
    if label in MODEL_CLASS_OVERRIDES:
        print(f"override active: {MODEL_CLASS_OVERRIDES[label]} (verify below)")
    try:
        cid, cname = target_class(model, label)
        print(f"would count class: {cid} -> '{cname}'")
    except ValueError as e:
        print("class resolution FAILED:", e)
 
    for video_path in video_paths:
        print(f"\n--- {Path(video_path).name} ---")
        try:
            frames = read_frames(video_path, 1)
        except (FileNotFoundError, RuntimeError) as e:
            print("  skipped:", e)
            continue
        frame = frames[0]
        h, w = frame.shape[:2]
        print("frame read OK, shape:", frame.shape)
        print(f"tiles at {TILE_SIZE}px/{TILE_OVERLAP}px overlap: "
              f"{len(tile_grid(w, h))}")
 
        # warm-up, so the first threshold isn't penalised by setup overhead
        model(frame, conf=0.25, max_det=DEFAULT_MAX_DET, verbose=False)
 
        for c in (0.35, 0.10, 0.01):
            r = model(frame, conf=c, max_det=DEFAULT_MAX_DET, verbose=False)[0]
            cls_ids = [int(x) for x in r.boxes.cls.tolist()]
            tally = Counter(model.names[i] for i in cls_ids)
            print(f"conf={c:<4}  boxes={len(cls_ids):<4}  classes={dict(tally)}")
            if len(cls_ids) >= DEFAULT_MAX_DET:
                print(f"           WARNING: hit max_det={DEFAULT_MAX_DET}."
                      f"This count is a CAP, not a measurement")
            print(f"           speed: {r.speed}")  # preprocess/inference/postprocess ms
            if len(r.boxes):
                bh = r.boxes.xywh[:, 3]
                for i in sorted(set(cls_ids)):
                    mask = r.boxes.cls == i
                    print(f"           class {i} ('{model.names[i]}'): "
                          f"n={int(mask.sum())} median_h={bh[mask].median().item():.0f}px")