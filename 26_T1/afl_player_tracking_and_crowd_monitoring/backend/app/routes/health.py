from fastapi import APIRouter
from app.schemas.health import HealthResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health_check():
    return {
        "gateway": "ok",
        "player_service": "pending",
        "crowd_service": "pending"
    }
