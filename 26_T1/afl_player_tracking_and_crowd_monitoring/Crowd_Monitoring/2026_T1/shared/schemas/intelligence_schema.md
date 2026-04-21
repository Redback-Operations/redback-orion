# Intelligence Service Schema

## Endpoint

`POST /process-intelligence`

## Purpose

This service receives analytics output, analyses crowd behaviour, and returns risk-related insights.

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
  },
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
    },
    {
      "frame_id": 2,
      "timestamp": 0.08,
      "annotated_frame_path": "crowd_detection/output/annotated_frames/frame_0002.jpg",
      "detections": [
        {
          "bbox": [104, 52, 164, 182],
          "confidence": 0.91
        }
      ]
    }
  ]
}
```

## Input Fields

- `video_id` - string - unique identifier for the video
- `zones` - list - zone-level density summary from the analytics service
- `zone_id` - string - zone identifier
- `person_count` - integer - people counted in the zone
- `density` - number - calculated density value
- `heatmap` - object - generated heatmap result
- `image_path` - string - saved output path for the heatmap image
- `frames` - optional list of sequential detection-aware frame records for motion-based analysis
- `frame_id` - integer - frame number in the sequence
- `timestamp` - number - timestamp of the frame in seconds
- `annotated_frame_path` - string - bbox-annotated frame path from `crowd_detection`
- `detections` - list - detection records available on that annotated frame

## Output JSON

```json
{
  "video_id": "match_01",
  "crowd_state": "increasing_density",
  "zones": [
    {
      "zone_id": "A1",
      "risk_level": "high",
      "flagged": true
    },
    {
      "zone_id": "A2",
      "risk_level": "medium",
      "flagged": false
    }
  ],
  "recommendations": [
    "Monitor zone A1 closely",
    "Prepare crowd redirection if density increases further"
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

## Output Fields

- `video_id` - string - same video identifier from the request
- `crowd_state` - string - overall crowd condition such as `stable`, `increasing_density`, or `dispersing`
- `zones` - list - zone-level risk results
- `zone_id` - string - zone identifier
- `risk_level` - string - risk classification such as `low`, `medium`, `high`
- `flagged` - boolean - whether the zone requires attention
- `recommendations` - list of strings - suggested actions or notes
- `event_flags` - optional list of behaviour or anomaly labels from the behaviour analysis module
- `artifact_paths` - optional list of saved output paths for demo or frontend visualisation
- `vision_metrics` - optional summary of motion-analysis outputs from the behaviour-analysis module
- `tracking` - tracking summary generated inside `crowd_behaviour_analytics`
- `walking_track_ids` - tracked people classified as walking-like motion
- `running_track_ids` - tracked people classified as running-like motion
- `movement_state` - per-track label such as `stationary`, `walking`, or `running`
- `anomaly_model` - IsolationForest-based anomaly summary for tracked motion
- `anomaly_track_ids` - tracked people flagged as anomalous motion
- `track_scores` - per-track anomaly details including speed, displacement, and anomaly score

## Notes

- this service combines behaviour analysis and risk assessment
- keep risk labels stable for backend and dashboard use
- the required response contract is unchanged; `event_flags`, `artifact_paths`, and `vision_metrics` are backward-compatible extensions
- walking/running labels are current movement-state outputs derived from detections, tracking, motion features, and anomaly scoring
