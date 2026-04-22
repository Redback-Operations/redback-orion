import os
import httpx
from app.config import USE_MOCK_SERVICES, CROWD_SERVICE_URL


def get_mock_crowd_data(video_id: str):
    return {
        "video_id": video_id,
        "crowd_detection": {
            "video_id": video_id,
            "frames": [
                {
                    "frame_id": 1,
                    "timestamp": 0.04,
                    "frame_path": None,
                    "annotated_frame_path": None,
                    "face_annotated_frame_path": None,
                    "people_annotated_frame_path": None,
                    "person_count": 2,
                    "face_count": 1,
                    "face_detections": [{"bbox": [120, 60, 155, 100], "confidence": 0.91}],
                    "people_detections": [{"bbox": [100, 50, 160, 180], "confidence": 0.93}]
                }
            ]
        },
        "density_zoning": [
            {"zone_id": "A1", "person_count": 8, "density": 0.72},
            {"zone_id": "A2", "person_count": 5, "density": 0.45}
        ],
        "heatmap": {
            "image_path": f"output/heatmap_{video_id}.png"
        },
        "crowd_behaviour_analytics": {
            "video_id": video_id,
            "crowd_state": "stable",
            "zones": [{"zone_id": "A1", "person_count": 8, "density": 0.72}],
            "event_flags": ["walking_detection"],
            "artifact_paths": [f"output/heatmap_{video_id}.png"],
            "vision_metrics": None
        },
        "crowd_allocation_risk_zone": {
            "video_id": video_id,
            "zones": [{"zone_id": "A1", "risk_level": "very_low", "flagged": False}],
            "recommendations": ["All zones within safe thresholds - continue monitoring"]
        }
    }


async def get_crowd_data(file_path: str = None, video_id: str = None):
    if video_id is None:
        video_id = os.path.splitext(os.path.basename(file_path))[0] if file_path else "unknown"

    if USE_MOCK_SERVICES:
        return get_mock_crowd_data(video_id)

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{CROWD_SERVICE_URL}/process-crowd-detection",
            json={"video_id": video_id, "video_path": file_path}
        )
        response.raise_for_status()
        return response.json()
