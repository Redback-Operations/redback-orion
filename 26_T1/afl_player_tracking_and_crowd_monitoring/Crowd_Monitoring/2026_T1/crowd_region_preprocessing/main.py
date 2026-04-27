"""Prepare crowd-focused frames before crowd detection runs."""

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


def _build_polygon_mask(frame_shape: tuple[int, int, int], points: list[list[float]]) -> np.ndarray:
    height, width = frame_shape[:2]
    polygon = np.array(
        [[int(point[0] * width), int(point[1] * height)] for point in points],
        dtype=np.int32,
    )
    mask = np.zeros((height, width), dtype=np.uint8)
    cv2.fillPoly(mask, [polygon], 255)
    return mask


def _detect_field_mask(frame: np.ndarray, config: dict) -> np.ndarray:
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower = np.array(config["green_hsv_lower"], dtype=np.uint8)
    upper = np.array(config["green_hsv_upper"], dtype=np.uint8)

    mask = cv2.inRange(hsv, lower, upper)
    kernel_size = max(1, int(config["morph_kernel_size"]))
    kernel = np.ones((kernel_size, kernel_size), dtype=np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return np.zeros_like(mask)

    min_ratio = float(config["min_field_area_ratio"])
    min_area = frame.shape[0] * frame.shape[1] * min_ratio

    filtered = np.zeros_like(mask)
    for contour in contours:
        area = cv2.contourArea(contour)
        if area >= min_area:
            cv2.drawContours(filtered, [contour], -1, 255, thickness=cv2.FILLED)

    if not np.any(filtered):
        return np.zeros_like(mask)

    dilation_size = max(1, int(config["field_mask_dilation_kernel"]))
    dilation_kernel = np.ones((dilation_size, dilation_size), dtype=np.uint8)
    return cv2.dilate(filtered, dilation_kernel, iterations=1)


def _prepare_frame(frame: np.ndarray, config: dict) -> tuple[np.ndarray, dict]:
    field_polygon = config.get("field_polygon_normalized", [])
    crowd_polygon = config.get("crowd_polygon_normalized", [])

    if field_polygon:
        field_mask = _build_polygon_mask(frame.shape, field_polygon)
        mask_source = "manual_field_polygon"
    else:
        field_mask = _detect_field_mask(frame, config)
        mask_source = "auto_green_field_mask"

    if crowd_polygon:
        crowd_mask = _build_polygon_mask(frame.shape, crowd_polygon)
        mask_source = f"{mask_source}+manual_crowd_polygon"
    elif np.any(field_mask):
        crowd_mask = cv2.bitwise_not(field_mask)
    else:
        crowd_mask = np.full(frame.shape[:2], 255, dtype=np.uint8)
        mask_source = "no_field_mask_detected"

    focused = cv2.bitwise_and(frame, frame, mask=crowd_mask)
    field_ratio = round(float(np.count_nonzero(field_mask)) / float(field_mask.size), 4) if np.any(field_mask) else 0.0
    crowd_ratio = round(float(np.count_nonzero(crowd_mask)) / float(crowd_mask.size), 4)

    metadata = {
        "mask_source": mask_source,
        "field_visible_ratio": field_ratio,
        "crowd_visible_ratio": crowd_ratio,
    }
    return focused, metadata


def prepare_crowd_frames(processed_video: dict) -> dict:
    config = load_config()
    output_dir = PROJECT_ROOT / config["focused_frames_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)

    focused_video = deepcopy(processed_video)
    focused_frames = []

    for frame_data in processed_video.get("frames", []):
        source_path = _resolve_frame_path(frame_data["frame_path"])
        frame = cv2.imread(str(source_path))

        if frame is None:
            focused_frames.append(frame_data)
            continue

        focused_frame, metadata = _prepare_frame(frame, config)
        output_name = f"frame_{frame_data['frame_id']:04d}.jpg"
        output_path = output_dir / output_name
        cv2.imwrite(str(output_path), focused_frame)

        updated_frame = dict(frame_data)
        updated_frame["source_frame_path"] = frame_data["frame_path"]
        updated_frame["frame_path"] = str(output_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
        updated_frame["crowd_focus_metadata"] = metadata
        focused_frames.append(updated_frame)

    focused_video["frames"] = focused_frames
    return focused_video
