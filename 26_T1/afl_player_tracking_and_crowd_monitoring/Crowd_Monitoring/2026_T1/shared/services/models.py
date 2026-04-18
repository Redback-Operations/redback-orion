"""Pydantic models for FastAPI request and response schemas."""

from pydantic import BaseModel, Field


class BoundingBoxDetection(BaseModel):
    bbox: list[int] = Field(..., examples=[[100, 50, 160, 180]])
    confidence: float = Field(..., examples=[0.93])


class DetectionFrame(BaseModel):
    frame_id: int = Field(..., examples=[1])
    timestamp: float = Field(..., examples=[0.04])
    person_count: int = Field(..., examples=[2])
    detections: list[BoundingBoxDetection]


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


class IntelligenceResponse(BaseModel):
    video_id: str = Field(..., examples=["match_01"])
    crowd_state: str = Field(..., examples=["increasing_density"])
    zones: list[RiskZone]
    recommendations: list[str] = Field(
        ...,
        examples=[["Monitor zone A1 closely", "Prepare crowd redirection if density increases further"]],
    )
