"""Demonstrate data aggregation with the agreed dummy contracts."""

import json

try:
    from .main import aggregate_stadium_data, export_results
except ImportError:
    from main import aggregate_stadium_data, export_results


CROWD_DATA = {
    "video_id": "VID_001",
    "summary": {
        "total_frames_processed": 65,
        "peak_person_count": 11,
        "crowd_state": "increasing_density",
        "highest_density_zone": "B2",
        "highest_risk_zone": "B2",
    },
    "peak_crowd_frame": {
        "frame_id": 49,
        "timestamp": 8.0,
        "person_count": 11,
        "people_annotated_frame_path": (
            "crowd_detection_output/people_detection_results/"
            "frame_0049.jpg"
        ),
    },
    "anomaly_visual": {
        "event_type": "walking_or_running_activity",
        "image_path": (
            "crowd_behaviour_analytics/output/VID_001/"
            "motion_frame_0009.jpg"
        ),
    },
    "heatmap": {
        "image_path": "output/heatmap_VID_001.png",
    },
    "time_series_chart": {
        "image_path": (
            "analytics_output/charts/"
            "VID_001_crowd_activity_chart.png"
        ),
    },
    "density_extremes": {
        "highest_density_zone": {
            "zone_id": "B2",
            "person_count": 6,
            "density": 1.0,
            "risk_level": "critical",
            "flagged": True,
        },
        "lowest_density_zone": {
            "zone_id": "A1",
            "person_count": 0,
            "density": 0.0,
            "risk_level": "very_low",
            "flagged": False,
        },
    },
    "stage_timings_ms": {
        "detection": 1320.5,
        "analytics": 244.8,
        "behaviour": 381.2,
        "risk": 18.6,
        "assemble": 205.4,
    },
}

FIRE_DATA = {
    "video_id": "VID_001",
    "detections": [
        {
            "frame_id": 25,
            "timestamp": 1.0,
            "camera_id": "CAM_02",
            "zone_id": "ZONE_B",
            "fire_detected": True,
            "smoke_detected": True,
            "confidence": 0.94,
            "severity": "HIGH",
            "bounding_box": {
                "x": 850,
                "y": 320,
                "width": 180,
                "height": 200,
            },
        }
    ],
}

STAMPEDE_DATA = {
    "video_id": "VID_001",
    "detections": [
        {
            "frame_id": 50,
            "timestamp": 2.0,
            "camera_id": "CAM_03",
            "zone_id": "ZONE_D",
            "stampede_detected": True,
            "confidence": 0.89,
            "severity": "CRITICAL",
            "crowd_count": 350,
            "movement_direction": "NORTH",
            "movement_speed": 4.8,
            "abnormal_movement": True,
        }
    ],
}


def main() -> None:
    unified_data = aggregate_stadium_data(
        crowd_data=CROWD_DATA,
        fire_data=FIRE_DATA,
        stampede_data=STAMPEDE_DATA,
        stadium_id="STADIUM_001",
    )
    exported_files = export_results(unified_data)

    print("\nUNIFIED STADIUM DATA\n")
    print(json.dumps(unified_data, indent=2))
    print("\nGENERATED FILES")
    print(f"JSON: {exported_files['json_path']}")
    print(f"CSV: {exported_files['csv_path']}")


if __name__ == "__main__":
    main()
