# Crowd Pipeline Service Schema

## Endpoint

`POST /process-crowd-detection`

## Purpose

This frontend-facing service runs the full crowd monitoring flow in one request.

It combines:

- video processing
- crowd region preprocessing
- crowd detection
- density zoning
- heatmap generation
- crowd behaviour analytics
- crowd allocation risk zone

The frontend (and the `/demo` page) should use this endpoint instead of calling
the individual module endpoints. It returns a compact summary for display rather
than every module's full output. Use the individual service endpoints to see
per-module detail.

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
  "summary": {
    "total_frames_processed": 65,
    "peak_person_count": 557,
    "crowd_state": "increasing_density",
    "highest_density_zone": "A1",
    "highest_risk_zone": "A1"
  },
  "peak_crowd_frame": {
    "frame_id": 18,
    "timestamp": 12.4,
    "person_count": 557,
    "people_annotated_frame_path": "crowd_detection_output/people_detection_results/match_01/frame_0018.jpg"
  },
  "anomaly_visual": {
    "event_type": "running_activity",
    "image_path": "crowd_behaviour_analytics/output/match_01/motion_frame_0008.jpg"
  },
  "heatmap": {
    "image_path": "output/heatmap_match_01.png"
  },
  "time_series_chart": {
    "image_path": "analytics_output/charts/match_01_crowd_activity_chart.png"
  },
  "density_extremes": {
    "highest_density_zone": {
      "zone_id": "A1",
      "person_count": 20,
      "density": 0.82,
      "risk_level": "high",
      "flagged": true
    },
    "lowest_density_zone": {
      "zone_id": "B2",
      "person_count": 3,
      "density": 0.12,
      "risk_level": "very_low",
      "flagged": false
    }
  },
  "stage_timings_ms": {
    "detection": 31250.4,
    "analytics": 812.3,
    "behaviour": 2104.9,
    "risk": 1.2,
    "assemble": 356.7
  }
}
```

## Output Fields

- `video_id` - string - same video identifier from the request
- `summary` - object - headline numbers for the dashboard cards
  - `total_frames_processed` - integer - frames returned by crowd detection (detected and reused)
  - `peak_person_count` - integer - highest `person_count` across all frames
  - `crowd_state` - string - `stable`, `increasing_density` or `dispersing`, based on the trend in person count over the video (see `crowd_behaviour_analytics`)
  - `highest_density_zone` - string or null - zone with the highest density
  - `highest_risk_zone` - string or null - first flagged zone from risk assessment
- `peak_crowd_frame` - object - the frame with the highest `person_count`. Empty object when there are no frames. The count only changes on frames where the detector ran, so this is always a detected frame and its annotated path is set
- `anomaly_visual` - object - one motion-annotated frame to display
  - `event_type` - string - `running_activity`, `walking_or_running_activity`, or the first event flag / `movement_alert`
  - `image_path` - string - motion frame from `crowd_behaviour_analytics/output/<video_id>/`
  - empty object when no artifacts were produced
- `heatmap.image_path` - string - saved heatmap image path
- `time_series_chart.image_path` - string - person-count-over-time chart saved to `analytics_output/charts/`
- `density_extremes` - object - highest and lowest density zones, each with `zone_id`, `person_count`, `density`, `risk_level` and `flagged`
- `stage_timings_ms` - object - wall time in milliseconds for each pipeline stage (`detection`, `analytics`, `behaviour`, `risk`, `assemble`)

## Error Response (HTTP 500)

```json
{
  "detail": "Video file not found: data/raw/match_01.mp4",
  "error_type": "FileNotFoundError",
  "traceback": ["...last 8 lines of the traceback..."],
  "video_id": "match_01",
  "stage": "crowd_pipeline"
}
```

- `detail` - string - error message. If the exception has no message, the class name and repr are used instead, so this is never blank
- `error_type` - string - exception class name
- `traceback` - list of strings - last 8 traceback lines (the full traceback is printed to the server console)
- `video_id` - string - video from the request
- `stage` - string - always `crowd_pipeline`

## Notes

- This schema is the frontend contract for the combined route.
- The individual service schemas (`detection_schema.md`, `analytics_schema.md`, `intelligence_schema.md`) describe the full per-module outputs.
- Image paths are relative to `crowd_monitoring/` and served by the API under `/artifacts/<path>`.
- After each run the server console also prints one combined `PIPELINE BENCHMARK` report (video processing, crowd detection and stage timings).
