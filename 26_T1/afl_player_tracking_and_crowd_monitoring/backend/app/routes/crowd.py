from fastapi import APIRouter
from app.services.crowd_client import get_crowd_data

router = APIRouter(prefix="/api", tags=["Crowd"])


@router.get("/crowd")
async def get_crowd():
    data = await get_crowd_data()
    return {
        "status": "success",
        "message": "Crowd data retrieved successfully",
        "data": data
    }
