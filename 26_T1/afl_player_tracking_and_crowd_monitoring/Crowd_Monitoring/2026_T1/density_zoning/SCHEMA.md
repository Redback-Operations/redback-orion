# Density Zoning Task Schema

## Purpose

This task receives detection results and calculates zone-level crowd counts and density values.

## Input JSON

```json
{
  "video_id": "match_01",
  "frames": [
    {
      "frame_id": 1,
      "timestamp": 0.04,
      "person_count": 2,
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
  ]
}
```

## Notes

- output of this task is used by `heatmap`
- `zones` must match the analytics service schema
