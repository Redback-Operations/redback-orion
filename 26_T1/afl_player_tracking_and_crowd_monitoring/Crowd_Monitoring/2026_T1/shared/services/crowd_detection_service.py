"""Service flow for video processing and crowd detection."""

from video_processing.main import process_video
from crowd_region_preprocessing.main import prepare_crowd_frames
from crowd_detection.main import detect_crowd


def process_detection(data: dict):
    """Call task implementations for the detection service."""
    video_id = data.get("video_id")
    video_path = data.get("video_path")

    processed_video = process_video(video_id, video_path)
    if not isinstance(processed_video, dict):
        raise RuntimeError("Video processing did not return a valid response")

    if processed_video.get("error"):
        raise FileNotFoundError(processed_video["error"])

    if "video_id" not in processed_video or "frames" not in processed_video:
        raise RuntimeError("Video processing returned incomplete output")

    focused_video = prepare_crowd_frames(processed_video)
    detection_result = detect_crowd(focused_video)

    if isinstance(detection_result, dict) and "video_id" not in detection_result:
        detection_result["video_id"] = video_id

    return detection_result
