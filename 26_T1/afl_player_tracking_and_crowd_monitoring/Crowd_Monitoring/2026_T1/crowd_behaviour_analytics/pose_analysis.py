"""Optional pose-based validation for crowd movement states."""

from __future__ import annotations

from pathlib import Path

import cv2
from ultralytics import YOLO


PROJECT_ROOT = Path(__file__).resolve().parent.parent
POSE_MODEL_CANDIDATES = [
    PROJECT_ROOT / "crowd_behaviour_analytics" / "yolov8n-pose.pt",
    PROJECT_ROOT / "crowd_behaviour_analytics" / "yolov8s-pose.pt",
    PROJECT_ROOT / "yolov8n-pose.pt",
    PROJECT_ROOT / "yolov8s-pose.pt",
]
LEG_KEYPOINT_IDS = (13, 14, 15, 16)


def _resolve_frame_path(frame_path: str | None) -> Path | None:
    if not frame_path:
        return None
    candidate = Path(frame_path)
    return candidate if candidate.is_absolute() else PROJECT_ROOT / candidate


def _load_pose_model():
    for model_path in POSE_MODEL_CANDIDATES:
        if model_path.exists():
            return YOLO(str(model_path))
    try:
        return YOLO("yolov8n-pose.pt")
    except Exception:
        return None


def _extract_leg_keypoints(model, image, bbox, min_pose_confidence):
    x1, y1, x2, y2 = bbox
    crop = image[max(y1, 0):max(y2, 0), max(x1, 0):max(x2, 0)]
    if crop.size == 0:
        return None

    result = model(crop, verbose=False)[0]
    if result.keypoints is None or len(result.keypoints.data) == 0:
        return None

    keypoint_tensor = result.keypoints.data[0]
    if keypoint_tensor is None:
        return None

    keypoints = keypoint_tensor.tolist()
    visible_keypoints = {}
    for idx in LEG_KEYPOINT_IDS:
        if idx >= len(keypoints):
            continue
        point = keypoints[idx]
        if len(point) < 3 or float(point[2]) < min_pose_confidence:
            continue
        visible_keypoints[idx] = (float(point[0]), float(point[1]))

    if len(visible_keypoints) < 2:
        return None

    return visible_keypoints


def _build_track_pose_sequences(frames, frame_tracks, tracking_summary, pose_model, min_bbox_height, min_pose_confidence):
    frame_entries = {
        frame.get("frame_id"): frame
        for frame in frames or []
    }
    walking_track_ids = set(tracking_summary.get("walking_track_ids", []))
    pose_sequences = {track_id: [] for track_id in walking_track_ids}

    for frame_track in frame_tracks:
        frame_id = frame_track.get("frame_id")
        frame_entry = frame_entries.get(frame_id, {})
        resolved_frame_path = _resolve_frame_path(frame_entry.get("frame_path") or frame_track.get("frame_path"))
        if resolved_frame_path is None:
            resolved_frame_path = _resolve_frame_path(frame_track.get("people_annotated_frame_path"))
        if resolved_frame_path is None or not resolved_frame_path.exists():
            continue

        image = cv2.imread(str(resolved_frame_path))
        if image is None:
            continue

        for tracked in frame_track.get("tracked_detections", []):
            track_id = tracked.get("track_id")
            if track_id not in pose_sequences:
                continue

            bbox = tracked.get("bbox", [])
            if len(bbox) != 4:
                continue

            bbox_height = float(tracked.get("bbox_height", 0.0))
            if bbox_height < min_bbox_height:
                continue

            leg_keypoints = _extract_leg_keypoints(
                pose_model,
                image,
                bbox,
                min_pose_confidence,
            )
            if leg_keypoints is None:
                continue

            pose_sequences[track_id].append(
                {
                    "frame_id": frame_id,
                    "bbox_height": max(bbox_height, 1.0),
                    "leg_keypoints": leg_keypoints,
                }
            )

    return pose_sequences


def _pose_leg_motion_score(sequence):
    if len(sequence) < 3:
        return 0.0

    normalized_steps = []
    for previous, current in zip(sequence, sequence[1:]):
        shared_ids = set(previous["leg_keypoints"]).intersection(current["leg_keypoints"])
        if len(shared_ids) < 2:
            continue

        step_magnitudes = []
        for keypoint_id in shared_ids:
            prev_x, prev_y = previous["leg_keypoints"][keypoint_id]
            curr_x, curr_y = current["leg_keypoints"][keypoint_id]
            dx = curr_x - prev_x
            dy = curr_y - prev_y
            step_magnitudes.append((dx * dx + dy * dy) ** 0.5)

        if not step_magnitudes:
            continue

        avg_height = max((previous["bbox_height"] + current["bbox_height"]) / 2.0, 1.0)
        normalized_steps.append((sum(step_magnitudes) / len(step_magnitudes)) / avg_height)

    if not normalized_steps:
        return 0.0

    return sum(normalized_steps) / len(normalized_steps)


def refine_tracking_summary_with_pose(
    frames,
    frame_tracks,
    tracking_summary,
    min_bbox_height=60.0,
    min_pose_confidence=0.25,
    min_pose_motion_score=0.03,
):
    """Validate walking tracks with leg-keypoint motion when a local pose model is available."""
    pose_model = _load_pose_model()
    if pose_model is None:
        return tracking_summary

    refined_summary = dict(tracking_summary)
    tracks = [dict(track) for track in tracking_summary.get("tracks", [])]
    pose_sequences = _build_track_pose_sequences(
        frames,
        frame_tracks,
        tracking_summary,
        pose_model,
        min_bbox_height,
        min_pose_confidence,
    )

    updated_walking_track_ids = []
    updated_stationary_track_ids = set(tracking_summary.get("stationary_track_ids", []))

    for track in tracks:
        track_id = track.get("track_id")
        if not track.get("is_walking"):
            continue

        pose_motion_score = _pose_leg_motion_score(pose_sequences.get(track_id, []))
        track["pose_used"] = bool(pose_sequences.get(track_id))
        track["pose_motion_score"] = round(pose_motion_score, 4)

        if track["pose_used"] and pose_motion_score < min_pose_motion_score:
            track["is_walking"] = False
            track["is_stationary"] = True
            track["movement_state"] = "stationary"
            updated_stationary_track_ids.add(track_id)
            continue

        updated_walking_track_ids.append(track_id)

    refined_summary["tracks"] = tracks
    refined_summary["walking_track_ids"] = sorted(updated_walking_track_ids)
    refined_summary["walking_track_count"] = len(updated_walking_track_ids)
    refined_summary["stationary_track_ids"] = sorted(updated_stationary_track_ids)
    refined_summary["stationary_track_count"] = len(updated_stationary_track_ids)
    return refined_summary
