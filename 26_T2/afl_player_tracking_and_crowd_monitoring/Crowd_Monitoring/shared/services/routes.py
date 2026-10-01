"""API routes for the shared service layer."""

import traceback

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from .crowd_analytics_service import process_analytics
from .crowd_detection_service import process_detection
from .crowd_intelligence_service import process_intelligence
from .crowd_pipeline_service import (
    process_crowd_detection,
    process_stadium_monitoring,
)
from .models import (
    AnalyticsRequest,
    AnalyticsResponse,
    CrowdPipelineResponse,
    StadiumMonitoringResponse,
    DetectionRequest,
    DetectionResponse,
    IntelligenceRequest,
    IntelligenceResponse,
    ProcessingErrorResponse,
)

router = APIRouter()

@router.post("/process-detection", response_model=DetectionResponse)
def process_detection_route(data: DetectionRequest):
    """Run the crowd detection service flow."""
    return process_detection(data.model_dump())

@router.post(
    "/process-stadium-monitoring",
    response_model=StadiumMonitoringResponse,
    responses={
        500: {
            "model": ProcessingErrorResponse,
            "description": "Internal processing error while running the stadium monitoring pipeline",
        }
    },
)
def process_stadium_monitoring_route(data: DetectionRequest):
    """Run crowd, fire, stampede, and aggregation pipeline."""
    try:
        return process_stadium_monitoring(data.model_dump())
    except Exception as exc:
        tb = traceback.format_exc()
        print(tb)

        message = str(exc).strip() or f"{type(exc).__name__}: {exc!r}"

        return JSONResponse(
            status_code=500,
            content={
                "detail": message,
                "error_type": type(exc).__name__,
                "traceback": tb.splitlines()[-8:],
                "video_id": data.video_id,
                "stage": "stadium_monitoring_pipeline",
            },
        )

@router.post("/process-analytics", response_model=AnalyticsResponse)
def process_analytics_route(data: AnalyticsRequest):
    """Run the crowd analytics service flow."""
    return process_analytics(data.model_dump())


@router.post("/process-intelligence", response_model=IntelligenceResponse)
def process_intelligence_route(data: IntelligenceRequest):
    """Run the crowd intelligence service flow."""
    return process_intelligence(data.model_dump())


@router.post(
    "/process-crowd-detection",
    response_model=CrowdPipelineResponse,
    responses={
        500: {
            "model": ProcessingErrorResponse,
            "description": "Internal processing error while running the crowd monitoring pipeline",
        }
    },
)
def process_crowd_detection_route(data: DetectionRequest):
    """Run the full crowd monitoring pipeline for frontend use."""
    try:
        return process_crowd_detection(data.model_dump())
    except Exception as exc:
        tb = traceback.format_exc()
        print(tb)   # full traceback to the server console
        # str(exc) is empty for a lot of exception types; fall back to the
        # class name and the last traceback line so the UI is never blank.
        message = str(exc).strip() or f"{type(exc).__name__}: {exc!r}"
        return JSONResponse(
            status_code=500,
            content={
                "detail": message,
                "error_type": type(exc).__name__,
                "traceback": tb.splitlines()[-8:],
                "video_id": data.video_id,
                "stage": "crowd_pipeline",
            },
        )
