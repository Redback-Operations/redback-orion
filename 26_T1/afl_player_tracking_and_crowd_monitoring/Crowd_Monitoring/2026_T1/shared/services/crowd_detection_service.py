"""Service flow for video processing and crowd detection."""

from video_processing.main import process_video
from crowd_detection.main import detect_crowd


def process_detection(data: dict):
    """Call task implementations for the detection service."""
    video_id = data.get("video_id")
    video_path = data.get("video_path")

    processed_video = process_video(video_id, video_path)
    detection_result = detect_crowd(processed_video)

    if isinstance(detection_result, dict) and "video_id" not in detection_result:
        detection_result["video_id"] = video_id

    return detection_result
