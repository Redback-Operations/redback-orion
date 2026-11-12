# Analytics Output and Data Aggregation Schema

## Purpose

This task combines the current aggregated crowd result with fire and stampede detections. It exports unified JSON for backend/frontend integration and flattened CSV for statistics and reporting.

This remains a standalone prototype. The live backend currently obtains crowd results directly from `POST /process-crowd-detection`.

## Crowd Input

Crowd Detection supplies an aggregated object containing:

- `video_id`
- `summary`
- `peak_crowd_frame`
- `anomaly_visual`
- `heatmap`
- `time_series_chart`
- `density_extremes`

The current annotated-frame field is `people_annotated_frame_path`.

Crowd Detection does not currently expose raw detections, per-person data, or a complete per-zone result in its backend-facing response. The reported density extremes contain per-frame average counts for only the highest and lowest zones.

## Fire and Stampede Inputs

Fire and stampede services supply a `video_id` and a `detections` list. Each detection used for zone aggregation must contain `zone_id` and should contain `timestamp`.

## Unified Output

```json
{
  "stadium_id": "STADIUM_001",
  "video_id": "VID_001",
  "timestamp": "2026-08-31T17:30:10Z",
  "crowd": {
    "summary": {},
    "peak_crowd_frame": {},
    "anomaly_visual": {},
    "heatmap": {},
    "time_series_chart": {},
    "density_extremes": {},
    "stage_timings_ms": {
      "detection": 1320.5,
      "analytics": 244.8,
      "behaviour": 381.2,
      "risk": 18.6,
      "assemble": 205.4
    }
  },
  "zones": {
    "ZONE_B": {
      "fire": true,
      "smoke": true,
      "fire_confidence": 0.94,
      "fire_severity": "HIGH",
      "stampede": false,
      "stampede_confidence": null,
      "stampede_severity": "NONE",
      "crowd_count": null,
      "movement_direction": null,
      "movement_speed": null,
      "abnormal_movement": false,
      "status": "CRITICAL"
    }
  }
}
```

## Exported Files

- `<video_id>_monitoring.json` preserves the complete unified structure.
- `<video_id>_zones.csv` provides flattened summary and zone fields for statistics and reporting.

## Current Limitations

- `density_extremes.person_count` is a per-frame average for the reported highest and lowest zones, not a complete set of stadium-zone counts.
- Density is normalised relative to the busiest zone, so `1.0` is not a physical occupancy measurement and is not used to calculate the unified safety status.
- `summary.peak_person_count` is the authoritative crowd count for the current contract.
- `stage_timings_ms` is preserved in the unified JSON when Crowd Detection supplies it; it is not flattened into the zone CSV.
