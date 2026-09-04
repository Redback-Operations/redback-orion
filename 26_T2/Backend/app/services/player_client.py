import httpx
from app.config import USE_MOCK_PLAYER, PLAYER_SERVICE_URL
from app.exceptions import ServiceTimeoutError


async def _post_to_player_service(url, *, timeout, files):
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, files=files)
            response.raise_for_status()
            return response.json()
    except (httpx.ConnectTimeout, httpx.ReadTimeout) as exc:
        raise ServiceTimeoutError(
            f"Player service timed out while requesting {url}"
        ) from exc

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


def get_mock_jersey_color_data():
    return {
        "status": "success",
        "teams": [
            {"team_id": 0, "team_name": "CAR", "jersey_color": [255, 0, 0]},
            {"team_id": 1, "team_name": "OPP", "jersey_color": [0, 0, 255]}
        ]
    }


def get_mock_tackle_data():
    return {
        "status": "success",
        "tackles": [],
        "csv_url": None
    }


def get_mock_formation_data():
    return {
        "status": "success",
        "formations": [
            {"frame_number": 1, "team_id": 0, "formation": "4-3-3"},
            {"frame_number": 1, "team_id": 1, "formation": "4-4-2"}
        ],
        "video_url": None,
        "csv_url": None
    }


async def get_player_data(file_path: str = None):
    if USE_MOCK_PLAYER:
        return get_mock_player_data()

    if not file_path:
        raise ValueError("file_path is required when not using mock")

    with open(file_path, "rb") as f:
        return await _post_to_player_service(
            f"{PLAYER_SERVICE_URL}/tracking",
            timeout=300.0,
            files={
                "video": (
                    file_path.split("/")[-1].split("\\")[-1],
                    f,
                    "video/mp4"
                )
            }
    )


async def get_jersey_color_data(video_path: str, tracking_json_path: str):
    if USE_MOCK_PLAYER:
        return get_mock_jersey_color_data()

    with open(video_path, "rb") as vf, open(tracking_json_path, "rb") as jf:
        return await _post_to_player_service(
            f"{PLAYER_SERVICE_URL}/jersey_color",
            timeout=300.0,
            files={
                "video": (video_path.split("\\")[-1], vf, "video/mp4"),
                "tracking_json": (
                    tracking_json_path.split("\\")[-1],
                    jf,
                    "application/json"
                )
            }
        )

async def get_tackle_data(csv_path: str):
    if USE_MOCK_PLAYER:
        return get_mock_tackle_data()

    with open(csv_path, "rb") as f:
        return await _post_to_player_service(
            f"{PLAYER_SERVICE_URL}/tackle",
            timeout=120.0,
            files={
                "tracking_csv": (
                    csv_path.split("\\")[-1],
                    f,
                    "text/csv"
                )
            }
        )


async def get_formation_data(video_path: str, tracking_json_path: str):
    if USE_MOCK_PLAYER:
        return get_mock_formation_data()

    with open(video_path, "rb") as vf, open(tracking_json_path, "rb") as jf:
        return await _post_to_player_service(
            f"{PLAYER_SERVICE_URL}/formation",
            timeout=600.0,
            files={
                "video": (video_path.split("\\")[-1], vf, "video/mp4"),
                "tracking_json": (
                    tracking_json_path.split("\\")[-1],
                    jf,
                    "application/json"
                )
            }
        )
