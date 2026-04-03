import httpx
from app.config import USE_MOCK_SERVICES, PLAYER_SERVICE_URL


def get_mock_player_data():
    return {
        "players": [
            {
                "player_id": 1,
                "team": "Team A",
                "position": {"x": 120, "y": 340},
                "speed": 6.4,
                "distance_covered": 3.2,
                "sprints": 4
            },
            {
                "player_id": 2,
                "team": "Team B",
                "position": {"x": 210, "y": 280},
                "speed": 5.8,
                "distance_covered": 2.9,
                "sprints": 3
            }
        ],
        "heatmap": None
    }


async def get_player_data(file_path: str = None):
    if USE_MOCK_SERVICES:
        return get_mock_player_data()

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{PLAYER_SERVICE_URL}/analyze",
            data={"file_path": file_path}
        )
        response.raise_for_status()
        return response.json()
