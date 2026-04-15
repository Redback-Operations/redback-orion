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
  }
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
  ]
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

## Notes

- this service combines behaviour analysis and risk assessment
- keep risk labels stable for backend and dashboard use
