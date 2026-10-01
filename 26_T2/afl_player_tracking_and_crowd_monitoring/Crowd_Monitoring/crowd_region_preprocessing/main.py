"""Black out fixed non-crowd regions before crowd detection runs.

Exclude-only. Mark the static structures to remove (roof, signage, concourse,
foreground rails) as polygons in `exclude_polygons_normalized`; everything else
is kept. There is deliberately no "keep" polygon and no auto field detector -
an include region around a moving crowd clips real people the moment they drift
past its edge, and the green-field HSV detector clips crowd pixels that happen
to be green-ish.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import cv2
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "shared" / "config" / "crowd_region_preprocessing_config.json"


def load_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as config_file:
        return json.load(config_file)


def _resolve_frame_path(frame_path: str) -> Path:
    candidate = Path(frame_path)
    return candidate if candidate.is_absolute() else PROJECT_ROOT / candidate


def _normalize_polygons(raw) -> list[list[list[float]]]:
    """Accept one polygon ([[x, y], ...]) or a list of them; normalised (0-1)."""
    if not raw:
        return []
    first = raw[0]
    if first and isinstance(first[0], (int, float)):
        return [raw]
    return [poly for poly in raw if poly]


def _build_keep_mask(height: int, width: int, exclude_polygons) -> np.ndarray:
    """255 everywhere except inside the exclude polygons (which become 0). Pure
    geometry - depends only on frame size, so it's built once per video."""
    mask = np.full((height, width), 255, dtype=np.uint8)
    for poly in _normalize_polygons(exclude_polygons):
        pts = np.array([[int(px * width), int(py * height)] for px, py in poly], dtype=np.int32)
        cv2.fillPoly(mask, [pts], 0)
    return mask


def _prepare_frame(frame: np.ndarray, config: dict) -> tuple[np.ndarray, dict]:
    """Mask one frame. Standalone/debug helper; the pipeline builds the mask
    once in prepare_crowd_frames and applies it in detect_crowd."""
    height, width = frame.shape[:2]
    keep_mask = _build_keep_mask(height, width, config.get("exclude_polygons_normalized"))
    focused = cv2.bitwise_and(frame, frame, mask=keep_mask)
    ratio = round(float(cv2.countNonZero(keep_mask)) / float(keep_mask.size), 4)
    return focused, {"crowd_visible_ratio": ratio}


def prepare_crowd_frames(processed_video: dict) -> dict:
    """Attach ONE reusable keep-mask to the video dict. detect_crowd applies it
    to each frame it already reads. write_focused_frames=true also dumps the
    masked JPEGs (debug / UI)."""
    config = load_config()
    exclude_polygons = config.get("exclude_polygons_normalized")
    write_focused = bool(config.get("write_focused_frames", False))

    result = deepcopy(processed_video)
    frames = result.get("frames", [])

    height = int(processed_video.get("frame_height") or 0)
    width = int(processed_video.get("frame_width") or 0)
    if (height <= 0 or width <= 0) and frames:
        probe = cv2.imread(str(_resolve_frame_path(frames[0]["frame_path"])))
        if probe is not None:
            height, width = probe.shape[:2]
    if height <= 0 or width <= 0:
        return result  # unknown frame size - pass through unmasked

    keep_mask = _build_keep_mask(height, width, exclude_polygons)
    n_excl = len(_normalize_polygons(exclude_polygons))
    mask_source = f"exclude x{n_excl}" if n_excl else "keep_all"
    result["crowd_mask"] = keep_mask
    result["crowd_mask_source"] = mask_source

    if not np.any(keep_mask):
        print("[WARN] crowd_region_preprocessing: exclude polygons cover the whole frame.")

    out_dir = None
    if write_focused:
        out_dir = PROJECT_ROOT / config["focused_frames_dir"]
        out_dir.mkdir(parents=True, exist_ok=True)

    for frame_data in frames:
        frame_data["source_frame_path"] = frame_data["frame_path"]
        frame_data["crowd_focus_metadata"] = {"mask_source": mask_source}
        if write_focused:
            img = cv2.imread(str(_resolve_frame_path(frame_data["frame_path"])))
            if img is None:
                continue
            if keep_mask.shape[:2] == img.shape[:2]:
                img = cv2.bitwise_and(img, img, mask=keep_mask)
            dst = out_dir / f"frame_{frame_data['frame_id']:04d}.jpg"
            cv2.imwrite(str(dst), img)
            frame_data["frame_path"] = str(dst.relative_to(PROJECT_ROOT)).replace("\\", "/")

    return result
