# Heatmap Task Schema

## Purpose

This task receives zone density data and produces the heatmap result.

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
  ]
}
```

## Output JSON

```json
{
  "video_id": "match_01",
  "heatmap": {
    "image_path": "output/heatmap_match_01.png"
  }
}
```

## Notes

- output of this task is combined with `density_zoning` output in the analytics service
- keep `image_path` stable for backend use
