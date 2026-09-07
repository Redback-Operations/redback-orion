import copy

from app.config import (
    CROWD_SERVICE_URL,
    PLAYER_SERVICE_URL,
)


def crowd_with_urls(
    crowd: dict | None,
):
    if not crowd:
        return crowd

    result = copy.deepcopy(crowd)

    base = f"{CROWD_SERVICE_URL}" "/artifacts/"

    for section_name in (
        "heatmap",
        "anomaly_visual",
        "time_series_chart",
    ):
        section = result.get(section_name)

        if not section:
            continue

        path = section.get("image_path")

        if path and not path.startswith("http"):
            section["image_path"] = base + path.replace(
                "\\",
                "/",
            ).lstrip("/")

    peak = result.get("peak_crowd_frame")

    if peak:
        for key in (
            "annotated_frame_path",
            "people_annotated_frame_path",
        ):
            path = peak.get(key)

            if path and not path.startswith("http"):
                peak[key] = base + path.replace(
                    "\\",
                    "/",
                ).lstrip("/")

    return result


def _player_url(
    path: str | None,
):
    if not path or path.startswith("http"):
        return path

    if not path.startswith("/"):
        path = "/" + path

    return PLAYER_SERVICE_URL + path


def player_with_urls(
    player: dict | None,
):
    if not player:
        return player

    result = copy.deepcopy(player)

    tracking = result.get("tracking")

    if tracking:
        tracking["video_url"] = _player_url(tracking.get("video_url"))

    for section_name in (
        "jersey_color",
        "formation",
    ):
        section = result.get(section_name)

        if section:
            for key in (
                "video_url",
                "csv_url",
            ):
                section[key] = _player_url(section.get(key))

    tackle = result.get("tackle")

    if tackle:
        tackle["csv_url"] = _player_url(tackle.get("csv_url"))

    return result
