import os

import httpx

from app.config import (
    CROWD_SERVICE_URL,
)


class CrowdServiceError(RuntimeError):
    pass


async def get_crowd_data(
    file_path: str,
    video_id: str | None = None,
):
    if not file_path or not os.path.exists(file_path):
        raise CrowdServiceError("A valid video file path " "is required.")

    if video_id is None:
        video_id = os.path.splitext(os.path.basename(file_path))[0]

    payload = {
        "video_id": video_id,
        "video_path": os.path.abspath(file_path),
    }

    try:
        async with httpx.AsyncClient(timeout=300.0) as client:

            response = await client.post(
                (f"{CROWD_SERVICE_URL}" "/process-crowd-detection"),
                json=payload,
            )

            response.raise_for_status()

            return response.json()

    except httpx.ConnectError as exc:
        raise CrowdServiceError(
            "Could not connect to crowd " "service at " f"{CROWD_SERVICE_URL}."
        ) from exc

    except httpx.TimeoutException as exc:
        raise CrowdServiceError("Crowd service timed out.") from exc

    except httpx.HTTPStatusError as exc:
        raise CrowdServiceError(
            "Crowd service returned HTTP "
            f"{exc.response.status_code}: "
            f"{exc.response.text}"
        ) from exc

    except ValueError as exc:
        raise CrowdServiceError("Crowd service returned " "invalid JSON.") from exc
