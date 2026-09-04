import os
import httpx

from app.config import CROWD_SERVICE_URL, USE_MOCK_CROWD
from app.exceptions import ServiceTimeoutError


async def _post_to_crowd_service(url, *, timeout, json_data):
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=json_data)
            response.raise_for_status()
            return response.json()
    except (httpx.ConnectTimeout, httpx.ReadTimeout) as exc:
        raise ServiceTimeoutError(
            f"Crowd service timed out while requesting {url}"
        ) from exc

def get_mock_crowd_data(video_id: str):
    return {
        "video_id": video_id,
        "summary": {
            "peak_person_count": 10,
            "crowd_state": "stable"
        },
        "heatmap": {
            "image_path": None
        }
    }


async def get_crowd_data(file_path: str = None, video_id: str = None):
    if video_id is None:
        if file_path:
            video_id = os.path.splitext(os.path.basename(file_path))[0]
        else:
            video_id = "unknown"

    if USE_MOCK_CROWD:
        return get_mock_crowd_data(video_id)

    if not file_path:
        raise ValueError("file_path is required")

    abs_path = os.path.abspath(file_path)

    return await _post_to_crowd_service(
        f"{CROWD_SERVICE_URL}/process-crowd-detection",
        timeout=120.0,
        json_data={
            "video_id": video_id,
            "video_path": abs_path
        }
    )
