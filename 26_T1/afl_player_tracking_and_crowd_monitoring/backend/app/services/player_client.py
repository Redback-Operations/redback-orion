import httpx
from app.config import USE_MOCK_PLAYER, PLAYER_SERVICE_URL


def get_mock_player_data():
    return {
        "status": "success",
        "video_info": {
            "duration": 7.0,
            "fps": 24,
            "total_frames": 168,
            "resolution": [896, 566]
        },
        "tracking_results": [
            {
                "frame_number": 1,
                "timestamp": 0.0,
                "players": [
                    {
                        "player_id": 1,
                        "team_id": 0,
                        "team_name": "CAR",
                        "bbox": {"x1": 100, "y1": 200, "x2": 140, "y2": 300},
                        "center": {"x": 120, "y": 250},
                        "confidence": 0.85,
                        "width": 40,
                        "height": 100
                    }
                ]
            }
        ],
        "video_url": None
    }


async def get_player_data(file_path: str = None):
    if USE_MOCK_PLAYER:
        return get_mock_player_data()

    if not file_path:
        raise ValueError("file_path is required when not using mock")

    async with httpx.AsyncClient(timeout=300.0) as client:
        with open(file_path, "rb") as f:
            response = await client.post(
                f"{PLAYER_SERVICE_URL}/tracking",
                files={"video": (file_path.split("/")[-1].split("\\")[-1], f, "video/mp4")}
            )
        response.raise_for_status()
        return response.json()


async def get_jersey_color_data(video_path: str, tracking_json_path: str):
    async with httpx.AsyncClient(timeout=300.0) as client:
        with open(video_path, "rb") as vf, open(tracking_json_path, "rb") as jf:
            response = await client.post(
                f"{PLAYER_SERVICE_URL}/jersey_color",
                files={
                    "video": (video_path.split("\\")[-1], vf, "video/mp4"),
                    "tracking_json": (tracking_json_path.split("\\")[-1], jf, "application/json")
                }
            )
        response.raise_for_status()
        return response.json()


async def get_tackle_data(csv_path: str):
    async with httpx.AsyncClient(timeout=120.0) as client:
        with open(csv_path, "rb") as f:
            response = await client.post(
                f"{PLAYER_SERVICE_URL}/tackle",
                files={"tracking_csv": (csv_path.split("\\")[-1], f, "text/csv")}
            )
        response.raise_for_status()
        return response.json()


async def get_formation_data(video_path: str, tracking_json_path: str):
    async with httpx.AsyncClient(timeout=600.0) as client:
        with open(video_path, "rb") as vf, open(tracking_json_path, "rb") as jf:
            response = await client.post(
                f"{PLAYER_SERVICE_URL}/formation",
                files={
                    "video": (video_path.split("\\")[-1], vf, "video/mp4"),
                    "tracking_json": (tracking_json_path.split("\\")[-1], jf, "application/json")
                }
            )
        response.raise_for_status()
        return response.json()
