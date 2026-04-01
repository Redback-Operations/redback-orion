from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    return {
        "gateway": "ok",
        "player_service": "pending",
        "crowd_service": "pending"
    }
