# Analytics Output Task Schema

## Purpose

This task exports results into files for reporting or dashboard use. It is separate from the current analytics service contract.

## Input JSON

```json
{
  "video_id": "match_01",
  "zones": [
    {
      "zone_id": "A1",
      "person_count": 8,
      "density": 0.72
    }
  ],
  "heatmap": {
    "image_path": "output/heatmap_match_01.png"
  },
  "crowd_state": "increasing_density"
}
```

## Output JSON

```json
{
  "video_id": "match_01",
  "json_path": "output/match_01_analytics.json",
  "csv_path": "output/match_01_analytics.csv"
}
```

## Notes

- this task is for export only
- it is not part of the current `crowd_analytics_service` flow
- backend team should not depend on this task for the live analytics service response right now
