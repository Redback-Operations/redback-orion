"""Lightweight person tracking for crowd behaviour analytics."""

from math import sqrt
from pathlib import Path
import shutil

import cv2

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_ROOT = PROJECT_ROOT / "crowd_behaviour_analytics" / "output"


def _centroid(bbox):
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)


def _bbox_size(bbox):
    x1, y1, x2, y2 = bbox
    return max(x2 - x1, 1), max(y2 - y1, 1)


def _bbox_iou(box_a, box_b):
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)

    inter_w = max(0, inter_x2 - inter_x1)
    inter_h = max(0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h

    area_a = max(ax2 - ax1, 0) * max(ay2 - ay1, 0)
    area_b = max(bx2 - bx1, 0) * max(by2 - by1, 0)
    union_area = max(area_a + area_b - inter_area, 1)

    return inter_area / union_area


def _distance(point_a, point_b):
    return sqrt((point_a[0] - point_b[0]) ** 2 + (point_a[1] - point_b[1]) ** 2)


def track_people(frames, max_distance=80.0, min_iou=0.1, max_missed_time=3.0):
    """Associate detections across frames using IoU and centroid distance."""
    active_tracks = {}
    track_histories = {}
    frame_tracks = []
    next_track_id = 1

    sorted_frames = sorted(frames or [], key=lambda frame: frame.get("frame_id", 0))

    for frame in sorted_frames:
        timestamp = float(frame.get("timestamp", 0.0))
        detections = frame.get("people_detections", [])
        used_track_ids = set()
        tracked_detections = []

        for detection in detections:
            bbox = detection.get("bbox", [])
            if len(bbox) != 4:
                continue

            centroid = _centroid(bbox)
            best_match = None
            best_score = None

            for track_id, track in active_tracks.items():
                if track_id in used_track_ids:
                    continue

                time_gap = max(timestamp - track["timestamp"], 0.0001)
                if time_gap > max_missed_time:
                    continue

                centroid_distance = _distance(centroid, track["centroid"])
                iou = _bbox_iou(bbox, track["bbox"])

                # Prefer stronger IoU matches; fall back to centroid distance when IoU is weak.
                if iou >= min_iou:
                    score = (2.0 * iou) - (centroid_distance / max(max_distance, 1.0))
                elif centroid_distance <= max_distance:
                    score = 0.05 - (centroid_distance / max(max_distance, 1.0))
                else:
                    continue

                if best_score is None or score > best_score:
                    best_score = score
                    best_match = track_id

            if best_match is None:
                track_id = next_track_id
                next_track_id += 1
                speed = 0.0
                normalized_speed = 0.0
                direction = (0.0, 0.0)
                history = []
            else:
                previous = active_tracks[best_match]
                delta_t = max(timestamp - previous["timestamp"], 0.0001)
                dx = centroid[0] - previous["centroid"][0]
                dy = centroid[1] - previous["centroid"][1]
                pixel_distance = _distance(centroid, previous["centroid"])
                speed = pixel_distance / delta_t
                _, bbox_height = _bbox_size(bbox)
                previous_height = previous["bbox_height"]
                avg_height = max((bbox_height + previous_height) / 2.0, 1.0)
                normalized_speed = pixel_distance / avg_height
                direction = (round(dx, 2), round(dy, 2))
                track_id = best_match
                history = track_histories.get(track_id, [])

            bbox_width, bbox_height = _bbox_size(bbox)
            track_entry = {
                "track_id": track_id,
                "bbox": bbox,
                "centroid": [round(centroid[0], 2), round(centroid[1], 2)],
                "speed": round(speed, 2),
                "normalized_speed": round(normalized_speed, 4),
                "direction": [direction[0], direction[1]],
                "bbox_width": bbox_width,
                "bbox_height": bbox_height,
                "confidence": detection.get("confidence", 0.0),
            }
            tracked_detections.append(track_entry)

            history = history + [
                {
                    "frame_id": frame.get("frame_id"),
                    "timestamp": timestamp,
                    "centroid": track_entry["centroid"],
                    "speed": track_entry["speed"],
                    "normalized_speed": track_entry["normalized_speed"],
                    "bbox_height": bbox_height,
                }
            ]

            track_histories[track_id] = history
            active_tracks[track_id] = {
                "centroid": centroid,
                "timestamp": timestamp,
                "bbox_height": bbox_height,
                "bbox": bbox,
            }
            used_track_ids.add(track_id)

        frame_tracks.append(
            {
                "frame_id": frame.get("frame_id"),
                "timestamp": timestamp,
                "annotated_frame_path": frame.get("annotated_frame_path"),
                "tracked_detections": tracked_detections,
            }
        )

    return frame_tracks, track_histories


def summarise_tracks(
    track_histories,
    stationary_motion_threshold=0.12,
    walking_motion_threshold=0.15,
    running_motion_threshold=0.9,
    min_history_for_motion=4,
):
    """Build tracking summary for anomaly/event logic."""
    track_summaries = []
    stationary_track_ids = []
    walking_track_ids = []
    running_track_ids = []

    for track_id, history in track_histories.items():
        speeds = [entry["speed"] for entry in history]
        normalized_speeds = [entry.get("normalized_speed", 0.0) for entry in history]
        max_speed = max(speeds, default=0.0)
        avg_speed = sum(speeds) / len(speeds) if speeds else 0.0
        max_normalized_speed = max(normalized_speeds, default=0.0)
        avg_normalized_speed = sum(normalized_speeds) / len(normalized_speeds) if normalized_speeds else 0.0
        heights = [entry.get("bbox_height", 1.0) for entry in history]
        avg_height_history = max(sum(heights) / max(len(heights), 1), 1.0)
        height_variation = (
            max(abs(height - avg_height_history) for height in heights) / avg_height_history
            if heights
            else 0.0
        )
        first_centroid = history[0].get("centroid", [0.0, 0.0])
        last_centroid = history[-1].get("centroid", [0.0, 0.0])
        displacement = _distance(first_centroid, last_centroid)
        avg_height = max(
            sum(entry.get("bbox_height", 1.0) for entry in history) / max(len(history), 1),
            1.0,
        )
        normalized_displacement = displacement / avg_height
        history_length = len(history)
        has_motion_history = history_length >= min_history_for_motion
        is_running = (
            has_motion_history
            and avg_normalized_speed >= 0.55
            and max_normalized_speed >= running_motion_threshold
            and normalized_displacement >= 0.9
        )
        sustained_walking_motion = (
            history_length >= 8
            and avg_normalized_speed >= 0.04
            and max_normalized_speed >= 0.12
            and normalized_displacement >= 0.65
            and height_variation <= 0.42
        )
        clear_walking_motion = (
            avg_normalized_speed >= walking_motion_threshold
            and max_normalized_speed >= 0.18
            and normalized_displacement >= 0.26
            and height_variation <= 0.32
        )
        is_walking = (
            has_motion_history
            and not is_running
            and (clear_walking_motion or sustained_walking_motion)
            and max_normalized_speed < running_motion_threshold + 0.55
        )
        is_stationary = (
            (not has_motion_history)
            or (
                avg_normalized_speed <= stationary_motion_threshold
                and max_normalized_speed <= 0.22
                and normalized_displacement <= 0.35
            )
        )

        if is_running:
            running_track_ids.append(track_id)
            movement_state = "running"
        elif is_walking:
            walking_track_ids.append(track_id)
            movement_state = "walking"
        elif is_stationary:
            stationary_track_ids.append(track_id)
            movement_state = "stationary"
        else:
            movement_state = "stationary"
            stationary_track_ids.append(track_id)

        track_summaries.append(
            {
                "track_id": track_id,
                "history_length": history_length,
                "avg_speed": round(avg_speed, 2),
                "max_speed": round(max_speed, 2),
                "avg_normalized_speed": round(avg_normalized_speed, 4),
                "max_normalized_speed": round(max_normalized_speed, 4),
                "normalized_displacement": round(normalized_displacement, 4),
                "height_variation": round(height_variation, 4),
                "is_stationary": is_stationary,
                "is_walking": is_walking,
                "is_running": is_running,
                "movement_state": movement_state,
            }
        )

    return {
        "track_count": len(track_summaries),
        "stationary_track_count": len(stationary_track_ids),
        "stationary_track_ids": stationary_track_ids,
        "walking_track_count": len(walking_track_ids),
        "walking_track_ids": walking_track_ids,
        "running_track_count": len(running_track_ids),
        "running_track_ids": running_track_ids,
        "tracks": track_summaries,
    }


def save_motion_annotations(frame_tracks, tracking_summary, video_id=None):
    """Save annotated frames highlighting stationary/walking/running tracked people."""
    if not frame_tracks or not tracking_summary:
        return []

    safe_video_id = video_id or "unknown_video"
    output_dir = OUTPUT_ROOT / safe_video_id
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact_paths = []
    stationary_track_ids = set(tracking_summary.get("stationary_track_ids", []))
    walking_track_ids = set(tracking_summary.get("walking_track_ids", []))
    running_track_ids = set(tracking_summary.get("running_track_ids", []))
    if not stationary_track_ids and not walking_track_ids and not running_track_ids:
        return []

    for frame in frame_tracks:
        source_path = frame.get("annotated_frame_path")
        if not source_path:
            continue

        resolved_path = Path(source_path)
        if not resolved_path.is_absolute():
            resolved_path = PROJECT_ROOT / resolved_path

        image = cv2.imread(str(resolved_path))
        if image is None:
            continue

        wrote_annotation = False

        for tracked in frame.get("tracked_detections", []):
            if tracked["track_id"] in running_track_ids:
                label = f"RUNNING T{tracked['track_id']}"
                color = (0, 0, 255)
            elif tracked["track_id"] in walking_track_ids:
                label = f"WALKING T{tracked['track_id']}"
                color = (0, 165, 255)
            elif tracked["track_id"] in stationary_track_ids:
                label = f"STATIONARY T{tracked['track_id']}"
                color = (0, 255, 0)
            else:
                continue

            x1, y1, x2, y2 = tracked["bbox"]
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            label_y = min(y2 + 22, image.shape[0] - 10)
            cv2.putText(
                image,
                label,
                (x1, label_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2,
            )
            wrote_annotation = True

        if not wrote_annotation:
            continue

        output_path = output_dir / f"motion_frame_{int(frame.get('frame_id', 0)):04d}.jpg"
        if cv2.imwrite(str(output_path), image):
            artifact_paths.append(str(output_path.relative_to(PROJECT_ROOT)).replace("\\", "/"))

    return artifact_paths
