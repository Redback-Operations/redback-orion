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

## Output JSON

```json
{
  "video_id": "match_01",
  "crowd_state": "increasing_density"
}
```

## Notes

- output of this task is used by `crowd_allocation_risk_zone`
- keep `crowd_state` aligned with the intelligence service schema
