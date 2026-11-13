# Analytics Service Schema

## Endpoint

`POST /process-analytics`

## Purpose

This service receives crowd detection output, calculates zone-based density, and generates heatmap results.

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
        },
        {
          "bbox": [220, 60, 275, 195],
          "confidence": 0.89
        }
      ]
    }
  ]
}
```

## Input Fields

- `video_id` - string - unique identifier for the video
- `frames` - list - detection result per frame from the detection service
- `frame_id` - integer - frame number
- `timestamp` - number - time in seconds for the frame
- `person_count` - integer - number of detected people
- `detections` - list - detection list for the frame
- `bbox` - list of 4 integers - bounding box as `[x1, y1, x2, y2]`
- `confidence` - number - model confidence score

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
  ],
  "heatmap": {
    "image_path": "output/heatmap_match_01.png"
  }
}
```

## Output Fields

- `video_id` - string - same video identifier from the request
- `zones` - list - zone-level density summary
- `zone_id` - string - zone identifier such as `A1`, `A2`, `B1`
- `person_count` - integer - people counted in the zone
- `density` - number - calculated density value for the zone
- `heatmap` - object - generated heatmap result
- `image_path` - string - saved output path for the heatmap image

## Notes

- this service currently covers density and heatmap only
- `analytics_output` is not included in this service for now
- this output becomes input for the intelligence service
