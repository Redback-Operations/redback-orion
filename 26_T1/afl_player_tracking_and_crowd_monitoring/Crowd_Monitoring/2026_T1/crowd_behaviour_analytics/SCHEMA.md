# Crowd Behaviour Analytics Task Schema

## Purpose

This task receives analytics output and determines overall crowd behaviour trends.

## Input JSON

```json
{
  "video_id": "match_01",
  "zones": [
    {
      "zone_id": "A1",
      "person_count": 8,
      "density": 0.72
    },
    {
      "zone_id": "A2",
      "person_count": 5,
      "density": 0.45
    }
  ],
  "heatmap": {
    "image_path": "output/heatmap_match_01.png"
  }
}
```

Optional additional input for AI-vision processing:

```json
{
  "frames": [
    {
      "frame_id": 1,
      "timestamp": 0.04,
      "annotated_frame_path": "crowd_detection/output/annotated_frames/frame_0001.jpg",
      "detections": [
        {
          "bbox": [100, 50, 160, 180],
          "confidence": 0.93
        }
      ]
    }
  ]
}
```

## Output JSON

```json
{
  "video_id": "match_01",
  "crowd_state": "increasing_density",
  "zones": [
    {
      "zone_id": "A1",
      "person_count": 8,
      "density": 0.72
    }
  ],
  "event_flags": [
    "running_detection",
    "crowd_surge",
    "motion_anomaly"
  ],
  "artifact_paths": [
    "output/heatmap_match_01.png",
    "crowd_behaviour_analytics/output/running_frames/motion_frame_0008.jpg"
  ],
  "vision_metrics": {
    "vision_enabled": true,
    "avg_motion_magnitude": 0.84,
    "peak_motion_magnitude": 1.27,
    "reverse_flow_ratio": 0.18,
    "motion_intensity": 1.05,
    "tracking": {
      "track_count": 3,
      "walking_track_count": 1,
      "walking_track_ids": [2],
      "running_track_count": 1,
      "running_track_ids": [1],
      "tracks": [
        {
          "track_id": 1,
          "history_length": 4,
          "avg_speed": 8.4,
          "max_speed": 12.6,
          "is_walking": false,
          "is_running": true,
          "movement_state": "running"
        },
        {
          "track_id": 2,
          "history_length": 4,
          "avg_speed": 5.2,
          "max_speed": 6.4,
          "is_walking": true,
          "is_running": false,
          "movement_state": "walking"
        }
      ]
    },
    "anomaly_model": {
      "model_enabled": true,
      "anomaly_track_ids": [1],
      "running_track_ids": [1],
      "anomaly_count": 1,
      "track_scores": [
        {
          "track_id": 1,
          "history_length": 4,
          "avg_speed": 8.4,
          "max_speed": 12.6,
          "displacement": 34.2,
          "anomaly_score": 0.2174,
          "is_anomaly": true
        }
      ]
    }
  }
}
```

## Notes

- output of this task is used by `crowd_allocation_risk_zone`
- keep `crowd_state` aligned with the intelligence service schema
- behaviour analysis can use zone density patterns, heatmap availability, and sequential annotated frames as input features
- `event_flags` and `artifact_paths` are optional extended outputs for demo and frontend visibility
- optional `frames` should use bbox-annotated frame paths from `crowd_detection` for downstream visual analysis and motion analysis
- `tracking` contains per-person movement-state outputs derived from lightweight tracking
- `anomaly_model` contains IsolationForest-based motion anomaly outputs
- current movement states are `stationary`, `walking`, and `running`
