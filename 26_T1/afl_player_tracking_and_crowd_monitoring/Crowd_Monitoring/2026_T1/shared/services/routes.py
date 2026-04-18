"""API routes for the shared service layer."""

from fastapi import APIRouter

from .crowd_analytics_service import process_analytics
from .crowd_detection_service import process_detection
from .crowd_intelligence_service import process_intelligence
from .models import (
    AnalyticsRequest,
    AnalyticsResponse,
    DetectionRequest,
    DetectionResponse,
    IntelligenceRequest,
    IntelligenceResponse,
)

router = APIRouter()

@router.post("/process-detection", response_model=DetectionResponse)
def process_detection_route(data: DetectionRequest):
    """Run the crowd detection service flow."""
    return process_detection(data.model_dump())


@router.post("/process-analytics", response_model=AnalyticsResponse)
def process_analytics_route(data: AnalyticsRequest):
    """Run the crowd analytics service flow."""
    return process_analytics(data.model_dump())


@router.post("/process-intelligence", response_model=IntelligenceResponse)
def process_intelligence_route(data: IntelligenceRequest):
    """Run the crowd intelligence service flow."""
    return process_intelligence(data.model_dump())
