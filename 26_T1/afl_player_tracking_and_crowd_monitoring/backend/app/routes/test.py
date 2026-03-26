from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["Test"])

@router.get("/test")
def test_route():
    return {
        "status": "success",
        "message": "API is working",
        "data": {
            "service": "backend",
            "endpoint": "/api/test"
        }
    }