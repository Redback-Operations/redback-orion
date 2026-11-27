from datetime import datetime
from typing import Any,Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

class ResultEnvelope(BaseModel):
    job_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

class PlayerAnalysisResults(BaseModel):
    model_config = ConfigDict(extra="allow")

    tracking: dict[str,Any] | None = None
    movement: dict[str,Any] | None = None
    jersey_color: dict[str,Any] | None = None
    formation: dict[str,Any] | None = None

class AnalysisResponse(ResultEnvelope):
    status: Literal["done","partial"]
    player: PlayerAnalysisResults | None 
    crowd: dict[str,Any] | None 
    error: str | None 

class TrackingSummary(Basemodel):
    frames_with_tracking: int
    unique_player_ids: int
    total_player_detections: int
    average_players_per_frame: float
    peak_players_in_frame: int
    average_detection_confidence: float | None 
    team_detection_counts: dict[str,int]

class EventSummary(BaseModel):
    count: int
    data: list[Any]

class MovementSummary(BaseModel):
    metric_mode: str | None 
    calibration_available: bool | None 
    exported_tracks: Any

class PlayerAnalyticsSummary(BaseModel):
    video:dict[str,Any]
    tracking: TrackingSummary
    formation:EventSummary
    tackles: EventSummary
    movement: MovementSummary

class PeakCrowdFrameSummary(BaseModel):
    frame_id: int | None 
    timestamp: float | None 
    person_count: int | None 

class CrowdAnalyticSummary(BaseModel):
    total_frames_processed: int | None 
    peak_person_count: int | None 
    crowd_state: str | None 
    highest_density_zone: str | None 
    highest_risk_zone: str | None 
    peak_crowd_frame: PeakCrowdFrameSummary
    density_extremes: dict[dict,Any]

class AnalyticsResponse(ResultEnvelope):
    player:PlayerAnalyticsSummary | None 
    crowd:CrowdAnalyticSummary | None 
    error: str | None 

class PlayerTrackingResponse(ResultEnvelope):
    player: dict[str,Any]