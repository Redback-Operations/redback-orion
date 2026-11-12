# crowd_detection/main.py
# Runs people detection (and optional face detection) on extracted video
# frames, then writes annotated frames and a per-run detection summary.

import json
import time

import cv2
import numpy as np
from pathlib import Path

# Import config before ultralytics. It sets YOLO_VERBOSE and, on the DirectML
# path, YOLO_AUTOINSTALL, both of which Ultralytics reads at import time.
from .config import (
    DEFAULT_CONF, DEFAULT_IOU, MODEL_NAME, PEOPLE_ANNOTATED_DIR, PEOPLE_CLASS_ID, PEOPLE_MODEL_NAME,
    ANNOTATED_DIR, TILE_BATCH, TILE_IMGSZ, USE_FACE_DETECTION, USE_TILING, SAVE_TILE_DEBUG, TILE_DEBUG_DIR,
    PREDICT_KWARGS, RESOLVED_DEVICE, USE_CUDA, USE_DML,
    DETECT_STRIDE, DETECT_MAX_WIDTH, SKIP_EMPTY_TILES, MIN_TILE_FILL,
)

from ultralytics import YOLO
from ultralytics.cfg import DEFAULT_CFG_DICT

# Newer Ultralytics uses `quantize` for FP16. Older releases reject it as an
# invalid argument, so fall back to half=True there.
if "quantize" in PREDICT_KWARGS and "quantize" not in DEFAULT_CFG_DICT:
    PREDICT_KWARGS["half"] = PREDICT_KWARGS.pop("quantize") == 16

# Output paths in config are relative; anchor them to the project root so
# results land in the same place regardless of the working directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
FACE_OUTPUT_DIR = ANNOTATED_DIR if ANNOTATED_DIR.is_absolute() else PROJECT_ROOT / ANNOTATED_DIR
PEOPLE_OUTPUT_DIR = PEOPLE_ANNOTATED_DIR if PEOPLE_ANNOTATED_DIR.is_absolute() else PROJECT_ROOT / PEOPLE_ANNOTATED_DIR
TILE_DEBUG_OUTPUT_DIR = TILE_DEBUG_DIR if TILE_DEBUG_DIR.is_absolute() else PROJECT_ROOT / TILE_DEBUG_DIR
SUMMARY_OUTPUT_DIR = PEOPLE_OUTPUT_DIR.parent   # crowd_detection_output/


def _model_backend(model_path):
    """Rough inference-backend name from the weight path Ultralytics was given."""
    p = str(model_path).lower().rstrip("/\\")
    if p.endswith("_openvino_model") or "openvino" in p:
        return "openvino"
    if p.endswith(".onnx"):
        return "onnx"
    if p.endswith((".engine", ".plan")):
        return "tensorrt"
    return "pytorch"


def _next_run_number(out_dir):
    """Return the next detection_summary_run_NNN.json index in out_dir.
    Footage is re-run repeatedly, so summaries are numbered per run rather than
    per video. Each file still records its video id.
    """
    highest = 0
    for path in out_dir.glob("detection_summary_run_*.json"):
        tail = path.stem.rsplit("_", 1)[-1]
        if tail.isdigit():
            highest = max(highest, int(tail))
    return highest + 1


def _safe_video_id(video_id):
    value = str(video_id or "unknown_video")
    return "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in value)

def _iou(box, boxes):
    ix1 = np.maximum(box[0], boxes[:, 0]); iy1 = np.maximum(box[1], boxes[:, 1])
    ix2 = np.minimum(box[2], boxes[:, 2]); iy2 = np.minimum(box[3], boxes[:, 3])
    inter = np.clip(ix2 - ix1, 0, None) * np.clip(iy2 - iy1, 0, None)
    area  = (box[2] - box[0]) * (box[3] - box[1])
    areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
    return inter / (area + areas - inter + 1e-9)

def _nms(boxes, scores, iou_thresh):
    """Return indices of boxes kept by greedy non-maximum suppression."""
    order, keep = scores.argsort()[::-1], []
    while order.size:
        i = order[0]; keep.append(int(i))
        if order.size == 1:
            break
        rest = order[1:]
        order = rest[_iou(boxes[i], boxes[rest]) < iou_thresh]
    return keep


def load_models():
    face_model = None
    if USE_FACE_DETECTION:
        face_model = YOLO(MODEL_NAME)

    # Repin ONNX Runtime to DirectML before YOLO builds its inference session -
    # Ultralytics only ever picks CUDA/CoreML/CPU providers on its own.
    if USE_DML:
        from .dml_backend import enable_dml
        enable_dml()

    # task="detect" so an OpenVINO/ONNX export dir loads without the task-guess warning
    people_model = YOLO(PEOPLE_MODEL_NAME, task="detect")

    # Move .pt weights onto the GPU up front so the first frame isn't paying the
    # host->device copy. A TensorRT .engine is already device-bound; skip it.
    if USE_CUDA and str(PEOPLE_MODEL_NAME).lower().endswith(".pt"):
        people_model.to(RESOLVED_DEVICE)

    return face_model, people_model


def _save_tile_debug(tile, m, tile_dets, out_dir, tag, rows, cols, border_pad):
    """Write one tile crop with its detections drawn in tile-local coordinates.
    Green boxes were kept; red boxes were dropped as seam duplicates. Red lines
    mark the border_pad band on each inner seam, where the drop rule applies.
    Only used when SAVE_TILE_DEBUG is enabled.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    img = tile.copy()   # tiles are views into the frame
    th_, tw_ = img.shape[:2]
 
    if m["column"] > 0:
        cv2.line(img, (border_pad, 0), (border_pad, th_), (0, 0, 255), 1)
    if m["column"] < cols - 1:
        cv2.line(img, (tw_ - border_pad, 0), (tw_ - border_pad, th_), (0, 0, 255), 1)
    if m["row"] > 0:
        cv2.line(img, (0, border_pad), (tw_, border_pad), (0, 0, 255), 1)
    if m["row"] < rows - 1:
        cv2.line(img, (0, th_ - border_pad), (tw_, th_ - border_pad), (0, 0, 255), 1)
 
    kept = 0
    for x1, y1, x2, y2, score, is_kept in tile_dets:
        colour = (0, 200, 0) if is_kept else (0, 0, 255)
        kept += is_kept
        cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), colour, 2)
        cv2.putText(img, f"{score:.2f}", (int(x1), max(12, int(y1) - 4)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, colour, 1)
 
    cv2.putText(img, f"r{m['row']}c{m['column']}  kept {kept}/{len(tile_dets)}",
                (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.imwrite(str(out_dir / f"{tag}_tile_r{m['row']}c{m['column']}.jpg"), img)


def detect_tiled(tiles, meta, model, frame, conf, iou, keep_class=None,
                 border_pad=4, imgsz=TILE_IMGSZ, batch=TILE_BATCH,
                 debug_dir=None, debug_tag="frame",
                 skip_empty=SKIP_EMPTY_TILES, tile_keep_mask=None):
    """Detect on tiles and merge the results into full-frame coordinates.
 
    Returns the same [{"bbox", "confidence"}] list as the whole-frame path.
 
    tiles and meta come from the upstream tiler (video_processing), rebuilt by
    tiles_from_meta(). They are index-aligned and meta uses full-frame
    coordinates.
 
    Tiles run in batches of `batch` per forward pass rather than one call per
    tile. This is where GPU acceleration pays off, and it reduces per-call
    overhead on CPU as well.
 
    skip_empty drops tiles that are almost entirely black (field pixels masked
    out upstream). tile_keep_mask, when given, supplies that decision
    precomputed from the crowd mask.
 
    If debug_dir is set, each tile is written there with its detections drawn.
    """
    h0, w0 = frame.shape[:2]
 
    # Take the grid from the metadata, not config, so the seam logic always
    # matches the tiler that produced these tiles.
    rows = max(m["row"] for m in meta) + 1
    cols = max(m["column"] for m in meta) + 1
 
    if skip_empty:
        if tile_keep_mask is not None and len(tile_keep_mask) == len(meta):
            keep = [(t, m) for t, m, k in zip(tiles, meta, tile_keep_mask) if k]
        else:
            # No precomputed mask: measure each tile directly.
            keep = [(t, m) for t, m in zip(tiles, meta)
                    if cv2.countNonZero(cv2.cvtColor(t, cv2.COLOR_BGR2GRAY))
                    > MIN_TILE_FILL * t.shape[0] * t.shape[1]]
        if not keep:
            return []
        tiles = [t for t, _ in keep]
        meta  = [m for _, m in keep]   # filter both lists or they fall out of alignment
 
    boxes, scores = [], []
    for start in range(0, len(tiles), batch):
        chunk_tiles = tiles[start:start + batch]
        chunk_meta  = meta[start:start + batch]
        results = model(chunk_tiles, conf=conf, iou=iou, imgsz=imgsz,
                        verbose=False, **PREDICT_KWARGS)
 
        for tile, m, r in zip(chunk_tiles, chunk_meta, results):
            tw, th = m["width"], m["height"]
            tile_dets = []   # (x1, y1, x2, y2, score, kept) in tile coordinates, for debug output
            for b in r.boxes:
                if keep_class is not None and int(b.cls[0]) != keep_class:
                    continue
                x1, y1, x2, y2 = b.xyxy[0].tolist()
                score = float(b.conf[0])
 
                # Drop a box touching an inner seam. The neighbouring tile's
                # overlap strip holds the whole object and keeps the full box.
                on_seam = ((x1 <= border_pad and m["column"] > 0) or
                           (x2 >= tw - border_pad and m["column"] < cols - 1) or
                           (y1 <= border_pad and m["row"] > 0) or
                           (y2 >= th - border_pad and m["row"] < rows - 1))
                tile_dets.append((x1, y1, x2, y2, score, not on_seam))
                if on_seam:
                    continue
 
                # Offset tile coordinates into full-frame coordinates.
                boxes.append((x1 + m["x"], y1 + m["y"],
                              x2 + m["x"], y2 + m["y"]))
                scores.append(score)
 
            if debug_dir is not None:
                _save_tile_debug(tile, m, tile_dets, Path(debug_dir), debug_tag,
                                 rows, cols, border_pad)
 
    if not boxes:
        return []
 
    boxes  = np.clip(np.array(boxes, float), 0, [w0, h0, w0, h0])
    scores = np.array(scores, float)
    return [
        {"bbox": [int(v) for v in boxes[i]],
         "confidence": round(float(scores[i]), 4)}
        for i in _nms(boxes, scores, iou)   # remove duplicates across tile overlaps
    ]


def detect_faces(tiles, meta, model, frame, conf, iou, use_tiling=False,
                 debug_dir=None, debug_tag="frame", tile_keep_mask=None):
    if use_tiling:
        return detect_tiled(tiles, meta, model, frame, conf, iou,
                            debug_dir=debug_dir, debug_tag=f"{debug_tag}_face",
                            tile_keep_mask=tile_keep_mask)
    results = model(frame, conf=conf, iou=iou, verbose=False, **PREDICT_KWARGS)[0]
    return [{"bbox": list(map(int, b.xyxy[0].tolist())),
             "confidence": round(float(b.conf[0]), 4)} for b in results.boxes]
 
 
def detect_people(tiles, meta, model, frame, conf, iou, use_tiling=False,
                  debug_dir=None, debug_tag="frame", tile_keep_mask=None):
    if use_tiling:
        return detect_tiled(tiles, meta, model, frame, conf, iou, keep_class=PEOPLE_CLASS_ID,
                            debug_dir=debug_dir, debug_tag=f"{debug_tag}_people",
                            tile_keep_mask=tile_keep_mask)
    results = model(frame, conf=conf, iou=iou, verbose=False, **PREDICT_KWARGS)[0]
    return [{"bbox": list(map(int, b.xyxy[0].tolist())),
             "confidence": round(float(b.conf[0]), 4)}
            for b in results.boxes if int(b.cls[0]) == PEOPLE_CLASS_ID]
 
 
def draw_people_boxes(frame, detections):
    output = frame.copy()
    colour = (255, 100, 0)   # blue (BGR)
 
    for d in detections:
        x1, y1, x2, y2 = d["bbox"]
        cv2.rectangle(output, (x1, y1), (x2, y2), colour, 2)
        cv2.putText(output, f"{d['confidence']:.2f}", (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, colour, 1)
 
    cv2.putText(output, f"People: {len(detections)}", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, colour, 2)
    return output
 
 
def draw_boxes(frame, detections):
    output = frame.copy()
    colour = (0, 200, 80)   # green (BGR)
 
    for d in detections:
        x1, y1, x2, y2 = d["bbox"]
        cv2.rectangle(output, (x1, y1), (x2, y2), colour, 2)
        cv2.putText(output, f"{d['confidence']:.2f}", (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, colour, 1)
 
    cv2.putText(output, f"Faces: {len(detections)}", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, colour, 2)
    return output
 
 
def tiles_from_meta(frame, meta):
    return [frame[m["y"]:m["y"] + m["height"],
                  m["x"]:m["x"] + m["width"]] for m in meta]


def _tiles_kept_by_mask(meta, crowd_mask, min_fill):
    """Return, per tile, whether enough of it lies inside the crowd mask.
    Masked pixels come only from crowd_mask, which is fixed for the whole
    video, so this is computed once from the mask instead of measuring every
    tile of every frame.
    """
    mh, mw = crowd_mask.shape[:2]
    keep = []
    for m in meta:
        x, y, w, h = m["x"], m["y"], m["width"], m["height"]
        region = crowd_mask[y:min(y + h, mh), x:min(x + w, mw)]
        keep.append(cv2.countNonZero(region) > min_fill * w * h)
    return keep
 
 
def detect_crowd(processed_video: dict) -> dict:
    load_start = time.perf_counter()
    face_model, people_model = load_models()
    model_load_s = time.perf_counter() - load_start
 
    io_ms_total = 0.0
    all_results = []
    safe_video_id = _safe_video_id(processed_video.get("video_id"))
    people_video_output_dir = PEOPLE_OUTPUT_DIR / safe_video_id
    frame_width = int(processed_video.get("frame_width") or 0)
    frame_height = int(processed_video.get("frame_height") or 0)
 
    if USE_FACE_DETECTION:
        FACE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    people_video_output_dir.mkdir(parents=True, exist_ok=True)
 
    tile_debug_dir = None
    if USE_TILING and SAVE_TILE_DEBUG:
        tile_debug_dir = TILE_DEBUG_OUTPUT_DIR / safe_video_id
 
    detection_ms_total = 0.0
    frames_detected = 0
 
    # Detections carried forward on frames skipped by DETECT_STRIDE.
    last_people = []
    last_face = None
 
    # Keep-mask from crowd_region_preprocessing (field, roof, etc. removed).
    # Applied here in memory rather than written out as a masked JPEG per frame.
    crowd_mask = processed_video.get("crowd_mask")
    mask_shape_warned = False
 
    # Per-tile keep decisions, computed once on the first tiled frame. The tile
    # grid and crowd_mask are both fixed for the video, so every later frame
    # reuses the result.
    tile_keep_mask = None
    tile_keep_mask_ready = False
 
    for frame_index, frame_data in enumerate(processed_video["frames"]):
        frame_path = frame_data["frame_path"]
        resolved_frame_path = Path(frame_path)
        if not resolved_frame_path.is_absolute():
            resolved_frame_path = PROJECT_ROOT / resolved_frame_path
 
        io_start = time.perf_counter()
        frame = cv2.imread(str(resolved_frame_path))
 
        if frame is None:
            print(f"[WARN] Could not read frame {frame_data['frame_id']}, skipping")
            continue
 
        if frame_width <= 0 or frame_height <= 0:
            frame_height, frame_width = frame.shape[:2]
 
        if crowd_mask is not None:
            if crowd_mask.shape[:2] == frame.shape[:2]:
                frame = cv2.bitwise_and(frame, frame, mask=crowd_mask)
            elif not mask_shape_warned:
                print(f"[WARN] crowd_mask {crowd_mask.shape[:2]} != frame {frame.shape[:2]}; not masking")
                mask_shape_warned = True
        io_ms_total += (time.perf_counter() - io_start) * 1000
 
        debug_tag = f"frame_{frame_data['frame_id']:04d}"
 
        # Run the detector on every DETECT_STRIDE-th frame only. Frames in
        # between reuse the previous detections, so the output schema and frame
        # count stay the same for everything downstream.
        run_detect = (frame_index % max(DETECT_STRIDE, 1) == 0)
 
        face_detections = None
        face_count = None
        face_annotated_frame_path = None
 
        meta = frame_data.get("tiles") or []
        tile_this_frame = USE_TILING and bool(meta)
 
        if not tile_keep_mask_ready and tile_this_frame and SKIP_EMPTY_TILES:
            if crowd_mask is not None and crowd_mask.shape[:2] == frame.shape[:2]:
                tile_keep_mask = _tiles_kept_by_mask(meta, crowd_mask, MIN_TILE_FILL)
            tile_keep_mask_ready = True
 
        tiles = tiles_from_meta(frame, meta) if tile_this_frame else []
 
        if run_detect:
            # Times inference, tiling and NMS only; frame I/O is timed separately.
            detect_start = time.perf_counter()
            people_detections = detect_people(
                tiles, meta, people_model, frame, DEFAULT_CONF, DEFAULT_IOU,
                use_tiling=tile_this_frame, debug_dir=tile_debug_dir,
                debug_tag=debug_tag, tile_keep_mask=tile_keep_mask)
 
            # Face detection is an optional separate output. Nothing downstream
            # consumes it, so it is off by default (USE_FACE_DETECTION).
            if USE_FACE_DETECTION:
                face_detections = detect_faces(
                    tiles, meta, face_model, frame, DEFAULT_CONF, DEFAULT_IOU,
                    use_tiling=tile_this_frame, debug_dir=tile_debug_dir,
                    debug_tag=debug_tag, tile_keep_mask=tile_keep_mask)
 
            detection_ms = round((time.perf_counter() - detect_start) * 1000, 1)
            detection_ms_total += detection_ms
            frames_detected += 1
            last_people, last_face = people_detections, face_detections
        else:
            people_detections = last_people
            face_detections = last_face if USE_FACE_DETECTION else None
            detection_ms = 0.0
 
        # Save annotated frames only when the detector ran. Carried-forward
        # frames would redraw stale boxes for no consumer: only the peak-crowd
        # frame is ever served, peak selection always lands on a detected frame,
        # and crowd_behaviour_analytics falls back to frame_path when the
        # annotated path is missing.
        people_annotated_frame_path = None
 
        if run_detect:
            io_start = time.perf_counter()
            if USE_FACE_DETECTION:
                face_count = len(face_detections)
                annotated = draw_boxes(frame, face_detections)
                face_output_path = FACE_OUTPUT_DIR / f"frame_{frame_data['frame_id']:04d}.jpg"
                cv2.imwrite(str(face_output_path), annotated)
                face_annotated_frame_path = str(face_output_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
 
            people_annotated = draw_people_boxes(frame, people_detections)
            people_output_path = people_video_output_dir / f"frame_{frame_data['frame_id']:04d}.jpg"
            cv2.imwrite(str(people_output_path), people_annotated)
            people_annotated_frame_path = str(people_output_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
            io_ms_total += (time.perf_counter() - io_start) * 1000
 
        all_results.append({
            "frame_id": frame_data["frame_id"],
            "timestamp": frame_data["timestamp"],
            "frame_path": frame_path,
            "face_annotated_frame_path": face_annotated_frame_path,
            "people_annotated_frame_path": people_annotated_frame_path,
            "person_count": len(people_detections),
            "face_count": face_count,
            "detection_ms": detection_ms,
            "detected": run_detect,   # False = detections carried from a prior frame
            "face_detections": face_detections if face_detections is not None else [],
            "people_detections": people_detections,
        })
 
    frames_processed = len(all_results)
    peak_people = max((f["person_count"] for f in all_results), default=0)
    backend = _model_backend(PEOPLE_MODEL_NAME)
 
    SUMMARY_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    run_number = _next_run_number(SUMMARY_OUTPUT_DIR)
 
    summary = {
        "run": run_number,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "video_id": processed_video["video_id"],
        "model": Path(str(PEOPLE_MODEL_NAME).rstrip("/\\")).name,
        "backend": backend,
        "device": RESOLVED_DEVICE,
        "openvino": backend == "openvino",
        "tiling": USE_TILING,
        "frames_processed": frames_processed,
        "frames_detected": frames_detected,   # the rest were carried forward (DETECT_STRIDE)
        "detect_stride": DETECT_STRIDE,
        "detect_max_width": DETECT_MAX_WIDTH,
        "skip_empty_tiles": SKIP_EMPTY_TILES,
        "total_detection_seconds": round(detection_ms_total / 1000, 2),
        "ms_per_detected_frame": round(detection_ms_total / frames_detected, 1) if frames_detected else 0.0,
        "model_load_seconds": round(model_load_s, 2),
        "frame_io_seconds": round(io_ms_total / 1000, 2),   # read + mask on every frame; draw + write on detected frames
        "peak_people_per_frame": peak_people,
    }
 
    summary_path = SUMMARY_OUTPUT_DIR / f"detection_summary_run_{run_number:03d}.json"
    with open(summary_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)
    summary["summary_json_path"] = str(summary_path)
 

    return {
        "video_id": processed_video["video_id"],
        "frame_width": frame_width,
        "frame_height": frame_height,
        "detection_summary": summary,
        "frames": all_results,
    }
