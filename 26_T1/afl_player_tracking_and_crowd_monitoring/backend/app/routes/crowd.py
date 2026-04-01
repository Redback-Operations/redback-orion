from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["Crowd"])

@router.get("/crowd")
def get_crowd():
    return {
        "status": "success",
        "message": "Crowd data retrieved successfully",
        "data": {
            "count": 15432,
            "density_level": "medium",
            "sections": [
                {"section_id": "A", "count": 3200},
                {"section_id": "B", "count": 4100},
                {"section_id": "C", "count": 3900},
                {"section_id": "D", "count": 4232}
            ]
        }
    }