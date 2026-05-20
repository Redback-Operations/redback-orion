from fastapi import APIRouter, HTTPException
from app.services.crowd_client import get_crowd_data


router = APIRouter(prefix="/api", tags=["Crowd"])


@router.get("/crowd")
async def get_crowd():
    try:
        data = await get_crowd_data()
        
        if not data:
            raise HTTPException(status_code=404, detail="Crowd data not found")
        
        return {
            "status": "success",
            "message": "Crowd data retrieved successfully",
            "data": data
        }
    
    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error while retrieving crowd data")
