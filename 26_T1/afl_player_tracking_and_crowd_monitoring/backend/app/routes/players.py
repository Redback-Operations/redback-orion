from fastapi import APIRouter, HTTPException
from app.services.player_client import get_player_data

router = APIRouter(prefix="/api", tags=["Players"])


@router.get("/players")
async def get_players():
    try:
        data = await get_player_data()
        
        if not data:
            raise HTTPException(status_code=404, detail="Player data not found")
        
        return {
            "status": "success",
            "message": "Players data retrieved successfully",
            "data": data
        }
    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error while retrieving player data")
