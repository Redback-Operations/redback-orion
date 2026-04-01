from fastapi import APIRouter
from app.services.player_client import get_player_data

router = APIRouter(prefix="/api", tags=["Players"])

USE_MOCK_SERVICES = True

@router.get("/players")
def get_players():
    if USE_MOCK_SERVICES:
        return get_player_data()

    return {
        "status": "error",
        "message": "Mock player service is disabled"
    }
