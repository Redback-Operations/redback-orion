# Crowd Detection Task Schema

## Purpose

This task receives processed frame data and returns per-frame person detections.

## Input JSON

```json
{
  "video_id": "match_01",
  "frames": [
    {
      "frame_id": 1,
      "timestamp": 0.04,
      "frame_path": "output/frame_0001.jpg"
    }
  ]
}
```

## Output JSON

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

## Notes

- output of this task becomes input to `density_zoning`
- this output must also match the detection service schema
