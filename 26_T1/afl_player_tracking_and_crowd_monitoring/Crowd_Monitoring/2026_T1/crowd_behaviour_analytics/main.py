"""Crowd behaviour analytics task orchestration."""

from crowd_behaviour_analytics.anomaly_model import detect_track_anomalies
from crowd_behaviour_analytics.event_detection import detect_behaviour_events
from crowd_behaviour_analytics.feature_extraction import (
    classify_crowd_state,
    extract_density_features,
)
from crowd_behaviour_analytics.pose_analysis import refine_tracking_summary_with_pose
from crowd_behaviour_analytics.tracking import (
    build_frame_activity_series,
    save_motion_annotations,
    summarise_tracks,
    track_people,
)
from crowd_behaviour_analytics.vision_analysis import (
    extract_motion_features,
    load_grayscale_frames,
    resolve_frame_paths,
)


def analyze_behaviour(input_data):
    """Analyze crowd behaviour over time and produce summary outputs."""
    zones = input_data.get("zones", [])
    heatmap = input_data.get("heatmap", {})
    video_id = input_data.get("video_id")
    frames = input_data.get("frames", [])
    frame_paths = resolve_frame_paths(input_data)

    features = extract_density_features(zones, heatmap)
    vision_features = extract_motion_features(load_grayscale_frames(frame_paths))
    frame_tracks, track_histories = track_people(frames)
    tracking_summary = summarise_tracks(track_histories)
    tracking_summary = refine_tracking_summary_with_pose(frames, frame_tracks, tracking_summary)
    anomaly_summary = detect_track_anomalies(track_histories)
    crowd_state = classify_crowd_state(features)
    event_flags = detect_behaviour_events(
        features,
        vision_features,
        zones,
        tracking_summary,
        anomaly_summary,
    )

    artifact_paths = []
    if heatmap and heatmap.get("image_path"):
        artifact_paths.append(heatmap["image_path"])
    merged_tracking_summary = dict(tracking_summary)
    merged_running_ids = set(tracking_summary.get("running_track_ids", []))
    merged_running_ids.update(anomaly_summary.get("running_track_ids", []))
    merged_tracking_summary["running_track_ids"] = sorted(merged_running_ids)
    merged_tracking_summary["running_track_count"] = len(merged_running_ids)
    frame_activity_series = build_frame_activity_series(frame_tracks, merged_tracking_summary)
    artifact_paths.extend(save_motion_annotations(frame_tracks, merged_tracking_summary, video_id))

    vision_metrics = dict(vision_features)
    vision_metrics["tracking"] = tracking_summary
    vision_metrics["anomaly_model"] = anomaly_summary

    return {
        "video_id": video_id,
        "crowd_state": crowd_state,
        "zones": zones,
        "event_flags": event_flags,
        "artifact_paths": artifact_paths,
        "frame_movement_summary": frame_activity_series,
        "frame_activity_series": frame_activity_series,
        "vision_metrics": vision_metrics,
    }


if __name__ == "__main__":
    pass
