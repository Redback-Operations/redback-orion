"""Pydantic models for FastAPI request and response schemas."""

from pydantic import BaseModel, Field
from typing import Optional


class BoundingBoxDetection(BaseModel):
    bbox: list[int] = Field(..., examples=[[100, 50, 160, 180]])
    confidence: float = Field(..., examples=[0.93])


class DetectionFrame(BaseModel):
    frame_id: int = Field(..., examples=[1])
    timestamp: float = Field(..., examples=[0.04])
    frame_path: Optional[str] = Field(default=None, examples=["video_processing/output/frames/frame_0001.jpg"])
    annotated_frame_path: Optional[str] = Field(
        default=None,
        examples=["crowd_detection_output/people_detection_results/frame_0001.jpg"],
    )
    face_annotated_frame_path: Optional[str] = Field(
        default=None,
        examples=["crowd_detection_output/face_detection_results/frame_0001.jpg"],
    )
    people_annotated_frame_path: Optional[str] = Field(
        default=None,
        examples=["crowd_detection_output/people_detection_results/frame_0001.jpg"],
    )
    person_count: int = Field(..., examples=[2])
    face_count: Optional[int] = Field(default=None, examples=[1])
    face_detections: list[BoundingBoxDetection] = Field(default_factory=list)
    people_detections: list[BoundingBoxDetection] = Field(default_factory=list)


class BehaviourFrameInput(BaseModel):
    frame_id: int = Field(..., examples=[1])
    timestamp: float = Field(..., examples=[0.04])
    annotated_frame_path: str = Field(
        ...,
        examples=["crowd_detection/output/annotated_frames/frame_0001.jpg"],
    )
    face_detections: list[BoundingBoxDetection] = Field(default_factory=list)
    people_detections: list[BoundingBoxDetection] = Field(default_factory=list)


class ZoneDensity(BaseModel):
    zone_id: str = Field(..., examples=["A1"])
    person_count: int = Field(..., examples=[8])
    density: float = Field(..., examples=[0.72])


class HeatmapResult(BaseModel):
    image_path: str = Field(..., examples=["output/heatmap_match_01.png"])


class RiskZone(BaseModel):
    zone_id: str = Field(..., examples=["A1"])
    risk_level: str = Field(..., examples=["high"])
    flagged: bool = Field(..., examples=[True])


class TrackSummary(BaseModel):
    track_id: int = Field(..., examples=[1])
    history_length: int = Field(..., examples=[4])
    avg_speed: float = Field(..., examples=[8.4])
    max_speed: float = Field(..., examples=[12.6])
    avg_normalized_speed: float = Field(..., examples=[0.42])
    max_normalized_speed: float = Field(..., examples=[0.88])
    normalized_displacement: float = Field(default=0.0, examples=[1.24])
    height_variation: float = Field(default=0.0, examples=[0.08])
    is_stationary: bool = Field(..., examples=[False])
    is_walking: bool = Field(..., examples=[True])
    is_running: bool = Field(..., examples=[False])
    movement_state: str = Field(..., examples=["walking"])


class TrackingSummary(BaseModel):
    track_count: int = Field(..., examples=[3])
    stationary_track_count: int = Field(..., examples=[1])
    stationary_track_ids: list[int] = Field(default_factory=list, examples=[[3]])
    walking_track_count: int = Field(..., examples=[1])
    walking_track_ids: list[int] = Field(default_factory=list, examples=[[2]])
    running_track_count: int = Field(..., examples=[1])
    running_track_ids: list[int] = Field(default_factory=list, examples=[[1]])
    tracks: list[TrackSummary] = Field(default_factory=list)


class AnomalyTrackScore(BaseModel):
    track_id: int = Field(..., examples=[1])
    history_length: int = Field(..., examples=[4])
    avg_speed: float = Field(..., examples=[8.4])
    avg_normalized_speed: float = Field(..., examples=[0.42])
    max_normalized_speed: float = Field(..., examples=[0.88])
    normalized_displacement: float = Field(..., examples=[1.24])
    anomaly_score: float = Field(..., examples=[0.2174])
    is_anomaly: bool = Field(..., examples=[True])


class AnomalyModelSummary(BaseModel):
    model_enabled: bool = Field(..., examples=[True])
    anomaly_track_ids: list[int] = Field(default_factory=list, examples=[[1]])
    running_track_ids: list[int] = Field(default_factory=list, examples=[[1]])
    anomaly_count: int = Field(..., examples=[1])
    track_scores: list[AnomalyTrackScore] = Field(default_factory=list)


class VisionMetrics(BaseModel):
    vision_enabled: bool = Field(..., examples=[True])
    avg_motion_magnitude: float = Field(..., examples=[0.84])
    peak_motion_magnitude: float = Field(..., examples=[1.27])
    reverse_flow_ratio: float = Field(..., examples=[0.18])
    motion_intensity: float = Field(..., examples=[1.05])
    tracking: TrackingSummary
    anomaly_model: AnomalyModelSummary


class DetectionRequest(BaseModel):
    video_id: str = Field(..., examples=["match_01"])
    video_path: str = Field(..., examples=["data/raw/match_01.mp4"])


class DetectionResponse(BaseModel):
    video_id: str = Field(..., examples=["match_01"])
    frames: list[DetectionFrame]


class AnalyticsRequest(BaseModel):
    video_id: str = Field(..., examples=["match_01"])
    frames: list[DetectionFrame]


class AnalyticsResponse(BaseModel):
    video_id: str = Field(..., examples=["match_01"])
    zones: list[ZoneDensity]
    heatmap: HeatmapResult


class IntelligenceRequest(BaseModel):
    video_id: str = Field(..., examples=["match_01"])
    zones: list[ZoneDensity]
    heatmap: HeatmapResult
    frames: Optional[list[BehaviourFrameInput]] = None


class IntelligenceResponse(BaseModel):
    video_id: str = Field(..., examples=["match_01"])
    crowd_state: str = Field(..., examples=["increasing_density"])
    zones: list[RiskZone]
    recommendations: list[str] = Field(
        ...,
        examples=[["Monitor zone A1 closely", "Prepare crowd redirection if density increases further"]],
    )
    event_flags: Optional[list[str]] = Field(
        default=None,
        examples=[["overcrowding_spike", "sudden_gathering"]],
    )
    artifact_paths: Optional[list[str]] = Field(
        default=None,
        examples=[["output/heatmap_match_01.png", "crowd_behaviour_analytics/output/running_frames/motion_frame_0008.jpg"]],
    )
    vision_metrics: Optional[VisionMetrics] = Field(
        default=None,
        examples=[{
            "vision_enabled": True,
            "avg_motion_magnitude": 0.84,
            "peak_motion_magnitude": 1.27,
            "reverse_flow_ratio": 0.18,
            "motion_intensity": 1.05,
            "tracking": {
                "track_count": 3,
                "stationary_track_count": 1,
                "stationary_track_ids": [3],
                "walking_track_count": 1,
                "walking_track_ids": [2],
                "running_track_count": 1,
                "running_track_ids": [1],
                "tracks": [
                    {
                        "track_id": 1,
                        "history_length": 4,
                        "avg_speed": 8.4,
                        "max_speed": 12.6,
                        "avg_normalized_speed": 0.42,
                        "max_normalized_speed": 0.88,
                        "is_stationary": False,
                        "is_walking": False,
                        "is_running": True,
                        "movement_state": "running"
                    }
                ]
            },
            "anomaly_model": {
                "model_enabled": True,
                "anomaly_track_ids": [1],
                "running_track_ids": [1],
                "anomaly_count": 1,
                "track_scores": [
                    {
                        "track_id": 1,
                        "history_length": 4,
                        "avg_speed": 8.4,
                        "avg_normalized_speed": 0.42,
                        "max_normalized_speed": 0.88,
                        "normalized_displacement": 1.24,
                        "anomaly_score": 0.2174,
                        "is_anomaly": True
                    }
                ]
            }
        }],
    )
