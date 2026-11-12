"""Service flow for video processing and crowd detection."""

from video_processing.main import process_video
from crowd_region_preprocessing.main import prepare_crowd_frames
from crowd_detection.main import detect_crowd
from shared.timing import timed


def process_detection(data: dict):
    """Call task implementations for the detection service.

    Runs three stages back to back (frame extraction, crowd-region masking,
    then the YOLO detector). Each one's timing is recorded silently and
    attached to the result as "stage_timings_ms", alongside process_video's
    own "timings" and detect_crowd's "detection_summary" - the top-level
    pipeline call folds all of this into one combined report instead of
    each stage printing its own piece as it finishes.
    """
    video_id = data.get("video_id")
    video_path = data.get("video_path")

    stage_timings: dict[str, float] = {}

    with timed("video_processing", stage_timings, prefix="detection", verbose=False):
        processed_video = process_video(video_id, video_path)

    if not isinstance(processed_video, dict):
        raise RuntimeError("Video processing did not return a valid response")

    if processed_video.get("error"):
        raise FileNotFoundError(processed_video["error"])

    if "video_id" not in processed_video or "frames" not in processed_video:
        raise RuntimeError("Video processing returned incomplete output")

    with timed("crowd_preprocessing", stage_timings, prefix="detection", verbose=False):
        focused_video = prepare_crowd_frames(processed_video)

    with timed("crowd_detection", stage_timings, prefix="detection", verbose=False):
        detection_result = detect_crowd(focused_video)

    if isinstance(detection_result, dict) and "video_id" not in detection_result:
        detection_result["video_id"] = video_id

    if isinstance(detection_result, dict):
        detection_result["stage_timings_ms"] = stage_timings
        detection_result["video_processing_timings"] = processed_video.get("timings")

    return detection_result
