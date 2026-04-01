from fastapi import APIRouter
from app.services.crowd_client import get_crowd_data

router = APIRouter(prefix="/api", tags=["Crowd"])

USE_MOCK_SERVICES = True

@router.get("/crowd")
async def get_crowd():
    if USE_MOCK_SERVICES:
        data = await get_crowd_data()
        return {
            "status": "success",
            "message": "Crowd data retrieved successfully",
            "data": data
        }

    return {
        "status": "error",
        "message": "Mock crowd service is disabled"
    }