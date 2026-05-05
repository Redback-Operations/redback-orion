# Crowd Pipeline Service Schema

## Endpoint

`POST /process-crowd-detection`

## Purpose

This frontend-facing service runs the full crowd monitoring flow in one request.

It combines:

- video processing
- crowd detection
- density zoning
- heatmap generation
- crowd behaviour analytics
- crowd allocation risk zone

The frontend should use this endpoint instead of calling the individual module endpoints.

## Input JSON

```json
{
  "video_id": "match_01",
  "video_path": "data/raw/match_01.mp4"
}
```

## Input Fields

- `video_id` - string - unique identifier for the video
- `video_path` - string - path to the source video file

## Output JSON

```json
{
  "video_id": "match_01",
  "crowd_detection": {
    "video_id": "match_01",
    "frames": [
      {
        "frame_id": 1,
        "timestamp": 0.04,
        "frame_path": "video_processing/data/extracted_frames/frame_0001.jpg",
        "annotated_frame_path": "crowd_detection_output/people_detection_results/frame_0001.jpg",
        "face_annotated_frame_path": "crowd_detection_output/face_detection_results/frame_0001.jpg",
        "people_annotated_frame_path": "crowd_detection_output/people_detection_results/frame_0001.jpg",
        "person_count": 2,
        "face_count": 1,
        "face_detections": [
          {
            "bbox": [120, 60, 155, 100],
            "confidence": 0.91
          }
        ],
        "people_detections": [
          {
            "bbox": [100, 50, 160, 180],
            "confidence": 0.93
          }
        ]
      }
    ]
  },
  "density_zoning": [
    {
      "zone_id": "A1",
      "person_count": 8,
      "density": 0.72
    }
  ],
  "heatmap": {
    "image_path": "output/heatmap_match_01.png"
  },
  "crowd_behaviour_analytics": {
    "video_id": "match_01",
    "crowd_state": "dispersing",
    "zones": [
      {
        "zone_id": "A1",
        "person_count": 8,
        "density": 0.72
      }
    ],
    "event_flags": [
      "walking_detection",
      "stationary_detection"
    ],
    "artifact_paths": [
      "output/heatmap_match_01.png",
      "crowd_behaviour_analytics/output/match_01/motion_frame_0001.jpg"
    ],
    "vision_metrics": {
      "vision_enabled": true,
      "avg_motion_magnitude": 0.4599,
      "peak_motion_magnitude": 0.5651,
      "reverse_flow_ratio": 0.0883,
      "motion_intensity": 0.5125,
      "tracking": {
        "track_count": 3,
        "stationary_track_count": 1,
        "stationary_track_ids": [1],
        "walking_track_count": 1,
        "walking_track_ids": [2],
        "running_track_count": 1,
        "running_track_ids": [3],
        "tracks": [
          {
            "track_id": 2,
            "history_length": 23,
            "avg_speed": 12.81,
            "max_speed": 32.17,
            "avg_normalized_speed": 0.064,
            "max_normalized_speed": 0.1429,
            "normalized_displacement": 0.8137,
            "height_variation": 0.3806,
            "is_stationary": false,
            "is_walking": true,
            "is_running": false,
            "movement_state": "walking"
          }
        ]
      },
      "anomaly_model": {
        "model_enabled": true,
        "anomaly_track_ids": [3],
        "running_track_ids": [3],
        "anomaly_count": 1,
        "track_scores": [
          {
            "track_id": 3,
            "history_length": 18,
            "avg_speed": 19.1,
            "avg_normalized_speed": 0.2079,
            "max_normalized_speed": 1.6892,
            "normalized_displacement": 0.1438,
            "anomaly_score": 0.0158,
            "is_anomaly": true
          }
        ]
      }
    }
  },
  "crowd_allocation_risk_zone": {
    "video_id": "match_01",
    "zones": [
      {
        "zone_id": "A1",
        "risk_level": "very_low",
        "flagged": false
      }
    ],
    "recommendations": [
      "All zones within safe thresholds - continue monitoring"
    ]
  }
}
```

## Top-Level Output Fields

- `video_id` - string - same video identifier from the request
- `crowd_detection` - object - people and face detection output for each processed frame
- `density_zoning` - list - zone-level person counts and density values
- `heatmap` - object - generated heatmap image path
- `crowd_behaviour_analytics` - object - crowd state, movement analytics, event flags, and artifact paths
- `crowd_allocation_risk_zone` - object - zone risk levels and recommendations

## Crowd Detection Fields

- `frames` - list - processed frame results
- `frame_id` - integer - frame number
- `timestamp` - number - time in seconds for the frame
- `frame_path` - string or null - extracted frame image path
- `annotated_frame_path` - string or null - default annotated frame path
- `face_annotated_frame_path` - string or null - face detection annotated image path
- `people_annotated_frame_path` - string or null - people detection annotated image path
- `person_count` - integer - number of detected people
- `face_count` - integer or null - number of detected faces
- `face_detections` - list - detected face bounding boxes
- `people_detections` - list - detected person bounding boxes
- `bbox` - list of 4 integers - bounding box as `[x1, y1, x2, y2]`
- `confidence` - number - detection confidence score

## Density And Heatmap Fields

- `density_zoning` - list - density result per zone
- `zone_id` - string - zone identifier such as `A1`, `A2`, `B1`, `B2`
- `person_count` - integer - people counted in the zone
- `density` - number - calculated density value for the zone
- `heatmap.image_path` - string - saved heatmap image path

## Behaviour Analytics Fields

- `crowd_state` - string - high-level crowd state such as `stable`, `dispersing`, or `increasing_density`
- `zones` - list - zone density data used for behaviour analysis
- `event_flags` - list - detected event labels such as `walking_detection`, `stationary_detection`, or `motion_anomaly`
- `artifact_paths` - list - generated image artifacts, including heatmap and motion annotated frames
- `vision_metrics` - object or null - motion and tracking metrics when annotated frames are available
- `tracking` - object - track counts and per-track movement state
- `anomaly_model` - object - anomaly scores and anomaly track identifiers

## Risk Zone Fields

- `zones` - list - risk assessment per zone
- `risk_level` - string - zone risk label such as `very_low`, `low`, `medium`, or `high`
- `flagged` - boolean - whether the zone needs attention
- `recommendations` - list - operational recommendations based on risk

## Notes

- This schema is the frontend contract for the combined route.
- The individual service schemas remain useful for testing each module separately.
- `crowd_allocation_risk_zone` is generated from the behaviour analytics result.
- `artifact_paths` includes motion frame images only when behaviour analytics receives valid annotated frame paths.
