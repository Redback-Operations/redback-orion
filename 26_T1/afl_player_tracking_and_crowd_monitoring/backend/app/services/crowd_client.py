import httpx
from app.config import USE_MOCK_SERVICES, CROWD_SERVICE_URL


def get_mock_crowd_data():
    return {
        "crowd_count": 15432,
        "density": 0.72,
        "movement": "steady",
        "sections": [
            {"section_id": 1, "count": 3200, "density": 0.65},
            {"section_id": 2, "count": 4100, "density": 0.78},
            {"section_id": 3, "count": 3900, "density": 0.74},
            {"section_id": 4, "count": 4232, "density": 0.81}
        ]
    }


async def get_crowd_data(file_path: str = None):
    if USE_MOCK_SERVICES:
        return get_mock_crowd_data()

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{CROWD_SERVICE_URL}/analyze",
            data={"file_path": file_path}
        )
        response.raise_for_status()
        return response.json()
