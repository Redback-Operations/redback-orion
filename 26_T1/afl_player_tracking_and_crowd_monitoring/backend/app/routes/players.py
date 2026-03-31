from fastapi import APIRouter
from app.services.player_client import get_player_data

router = APIRouter(prefix="/api", tags=["Players"])


@router.get("/players")
async def get_players():
    data = await get_player_data()
    return {
        "status": "success",
        "message": "Players data retrieved successfully",
        "data": data
    }
