from fastapi import APIRouter
from app.services.crowd_client import get_crowd_data

router = APIRouter(prefix="/api", tags=["Crowd"])

USE_MOCK_SERVICES = True

@router.get("/crowd")
def get_crowd():
    if USE_MOCK_SERVICES:
        return get_crowd_data()

    return {
        "status": "error",
        "message": "Mock crowd service is disabled"
    }