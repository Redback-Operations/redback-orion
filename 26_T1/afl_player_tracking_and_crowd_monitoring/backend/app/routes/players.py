from fastapi import APIRouter, UploadFile, File
from app.services.player_client import get_player_data

router = APIRouter(prefix="/api", tags=["Players"])


@router.post("/players")
async def get_players(file: UploadFile = File(...)):
    data = await get_player_data(file)
    return {
        "status": "success",
        "message": "Players data retrieved successfully",
        "data": data
    }