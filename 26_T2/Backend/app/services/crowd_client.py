import os
import httpx

from app.config import CROWD_SERVICE_URL, USE_MOCK_CROWD


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

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{CROWD_SERVICE_URL}/process-crowd-detection",
                json={
                    "video_id": video_id,
                    "video_path": abs_path
                }
            )

            response.raise_for_status()
            return response.json()

    except httpx.TimeoutException:
        raise RuntimeError("Crowd service request timed out")

    except httpx.ConnectError:
        raise RuntimeError("Crowd service is unavailable")

    except httpx.HTTPStatusError as e:
        raise RuntimeError(
            f"Crowd service returned HTTP {e.response.status_code}"
        )

    except httpx.RequestError as e:
        raise RuntimeError(
            f"Crowd service request failed: {e}"
        )