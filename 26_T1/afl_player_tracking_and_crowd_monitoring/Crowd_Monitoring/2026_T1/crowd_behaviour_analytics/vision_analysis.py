"""Vision-analysis helpers for crowd behaviour analytics."""

from pathlib import Path

import cv2
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def resolve_frame_paths(input_data):
    """Collect annotated frame paths for behaviour analysis."""
    legacy_frame_paths = input_data.get("frame_paths", [])
    if legacy_frame_paths:
        return legacy_frame_paths

    frame_entries = input_data.get("frames", [])
    resolved_paths = []
    for frame in frame_entries:
        annotated_path = frame.get("annotated_frame_path")
        if annotated_path:
            resolved_paths.append(annotated_path)
    return resolved_paths


def load_grayscale_frames(frame_paths):
    """Load a limited sequence of grayscale frames for motion analysis."""
    if not frame_paths:
        return []

    loaded_frames = []

    for path in frame_paths[:8]:
        resolved_path = Path(path)
        if not resolved_path.is_absolute():
            resolved_path = PROJECT_ROOT / resolved_path

        frame = cv2.imread(str(resolved_path), cv2.IMREAD_GRAYSCALE)
        if frame is not None:
            loaded_frames.append(frame)

    return loaded_frames


def extract_motion_features(frames):
    """Estimate motion-related features from consecutive frames using optical flow."""
    if len(frames) < 2:
        return {
            "vision_enabled": False,
            "avg_motion_magnitude": 0.0,
            "peak_motion_magnitude": 0.0,
            "reverse_flow_ratio": 0.0,
            "motion_intensity": 0.0,
        }

    magnitudes = []
    reverse_flow_ratios = []

    for idx in range(len(frames) - 1):
        prev_frame = frames[idx]
        next_frame = frames[idx + 1]

        flow = cv2.calcOpticalFlowFarneback(
            prev_frame,
            next_frame,
            None,
            0.5,
            3,
            15,
            3,
            5,
            1.2,
            0,
        )

        mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1], angleInDegrees=True)
        magnitudes.append(float(np.mean(mag)))

        angle_bins = ((ang % 360) // 90).astype(int)
        bin_counts = np.bincount(angle_bins.ravel(), minlength=4)
        dominant_bin = int(np.argmax(bin_counts))
        opposite_bin = (dominant_bin + 2) % 4
        reverse_ratio = float(bin_counts[opposite_bin] / max(bin_counts.sum(), 1))
        reverse_flow_ratios.append(reverse_ratio)

    avg_motion = float(np.mean(magnitudes))
    peak_motion = float(np.max(magnitudes))
    reverse_ratio = float(np.mean(reverse_flow_ratios))

    return {
        "vision_enabled": True,
        "avg_motion_magnitude": round(avg_motion, 4),
        "peak_motion_magnitude": round(peak_motion, 4),
        "reverse_flow_ratio": round(reverse_ratio, 4),
        "motion_intensity": round((avg_motion + peak_motion) / 2, 4),
    }
