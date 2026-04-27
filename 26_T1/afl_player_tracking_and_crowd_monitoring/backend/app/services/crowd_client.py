import os
import httpx
from app.config import USE_MOCK_CROWD, CROWD_SERVICE_URL


def get_mock_crowd_data(video_id: str):
    return {
        "video_id": video_id,
        "summary": {
            "total_frames_processed": 65,
            "peak_person_count": 11,
            "crowd_state": "stable",
            "highest_density_zone": "A1",
            "highest_risk_zone": None
        },
        "peak_crowd_frame": {
            "frame_id": 18,
            "timestamp": 12.4,
            "person_count": 11,
            "annotated_frame_path": None
        },
        "anomaly_visual": {
            "event_type": "walking_detection",
            "image_path": f"output/anomaly_{video_id}.jpg"
        },
        "heatmap": {
            "image_path": f"output/heatmap_{video_id}.png"
        },
        "time_series_chart": {
            "image_path": f"analytics_output/charts/{video_id}_crowd_activity_chart.png"
        },
        "density_extremes": {
            "highest_density_zone": {
                "zone_id": "A1",
                "person_count": 8,
                "density": 0.72,
                "risk_level": "low",
                "flagged": False
            },
            "lowest_density_zone": {
                "zone_id": "A2",
                "person_count": 2,
                "density": 0.18,
                "risk_level": "very_low",
                "flagged": False
            }
        }
    }


async def get_crowd_data(file_path: str = None, video_id: str = None):
    if video_id is None:
        video_id = os.path.splitext(os.path.basename(file_path))[0] if file_path else "unknown"

    if USE_MOCK_CROWD:
        return get_mock_crowd_data(video_id)

    # Send absolute path so the crowd service can locate the file regardless of its CWD
    abs_path = os.path.abspath(file_path) if file_path else None

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{CROWD_SERVICE_URL}/process-crowd-detection",
            json={"video_id": video_id, "video_path": abs_path}
        )
        response.raise_for_status()
        return response.json()
