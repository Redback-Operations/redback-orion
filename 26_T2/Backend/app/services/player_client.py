import os

import httpx

from app.config import (
    PLAYER_SERVICE_URL,
)


class PlayerServiceError(RuntimeError):
    pass


async def _post_files(
    endpoint: str,
    files: dict,
    timeout: float,
):
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:

            response = await client.post(
                (f"{PLAYER_SERVICE_URL}" f"{endpoint}"),
                files=files,
            )

            response.raise_for_status()

            return response.json()

    except httpx.ConnectError as exc:
        raise PlayerServiceError(
            "Could not connect to " "player service at " f"{PLAYER_SERVICE_URL}."
        ) from exc

    except httpx.TimeoutException as exc:
        raise PlayerServiceError("Player service timed out " f"on {endpoint}.") from exc

    except httpx.HTTPStatusError as exc:
        raise PlayerServiceError(
            f"Player service {endpoint} "
            "returned HTTP "
            f"{exc.response.status_code}: "
            f"{exc.response.text}"
        ) from exc

    except ValueError as exc:
        raise PlayerServiceError(
            f"Player service {endpoint} " "returned invalid JSON."
        ) from exc


async def get_player_data(
    file_path: str,
):
    if not file_path or not os.path.exists(file_path):
        raise PlayerServiceError("A valid video file path " "is required.")

    with open(
        file_path,
        "rb",
    ) as file:

        return await _post_files(
            "/tracking",
            {
                "video": (
                    os.path.basename(file_path),
                    file,
                    "video/mp4",
                )
            },
            1000.0,
        )


async def get_jersey_color_data(
    video_path: str,
    tracking_json_path: str,
):
    if not os.path.exists(video_path) or not os.path.exists(tracking_json_path):
        raise PlayerServiceError(
            "Video and tracking JSON " "are required for jersey analysis."
        )

    with (
        open(
            video_path,
            "rb",
        ) as video_file,
        open(
            tracking_json_path,
            "rb",
        ) as json_file,
    ):

        return await _post_files(
            "/jersey_color",
            {
                "video": (
                    os.path.basename(video_path),
                    video_file,
                    "video/mp4",
                ),
                "tracking_json": (
                    os.path.basename(tracking_json_path),
                    json_file,
                    "application/json",
                ),
            },
            1000.0,
        )


async def get_tackle_data(
    csv_path: str,
):
    if not os.path.exists(csv_path):
        raise PlayerServiceError("Tracking CSV is required " "for tackle analysis.")

    with open(
        csv_path,
        "rb",
    ) as file:

        return await _post_files(
            "/tackle",
            {
                "tracking_csv": (
                    os.path.basename(csv_path),
                    file,
                    "text/csv",
                )
            },
            1000.0,
        )


async def get_formation_data(
    video_path: str,
    tracking_json_path: str,
):
    if not os.path.exists(video_path) or not os.path.exists(tracking_json_path):
        raise PlayerServiceError(
            "Video and tracking JSON " "are required for formation analysis."
        )

    with (
        open(
            video_path,
            "rb",
        ) as video_file,
        open(
            tracking_json_path,
            "rb",
        ) as json_file,
    ):

        return await _post_files(
            "/formation",
            {
                "video": (
                    os.path.basename(video_path),
                    video_file,
                    "video/mp4",
                ),
                "tracking_json": (
                    os.path.basename(tracking_json_path),
                    json_file,
                    "application/json",
                ),
            },
            1000.0,
        )
