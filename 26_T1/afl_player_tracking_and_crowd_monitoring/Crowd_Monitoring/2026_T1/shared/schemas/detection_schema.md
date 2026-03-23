# Detection Service Schema

## Endpoint

`POST /process-detection`

## Purpose

This service receives a video reference, runs video processing and crowd detection, and returns detection results per frame.

## Input JSON

```json
{
  "video_id": "match_01",
  "video_path": "data/raw/match_01.mp4"
}
```

## Input Fields

- `video_id` - string - unique identifier for the video
- `video_path` - string - local or project-relative path to the input video

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

## Output Fields

- `video_id` - string - same video identifier from the request
- `frames` - list - detection result for each processed frame
- `frame_id` - integer - frame number
- `timestamp` - number - time in seconds for the frame
- `person_count` - integer - number of detected people in the frame
- `detections` - list - detected people in the frame
- `bbox` - list of 4 integers - bounding box as `[x1, y1, x2, y2]`
- `confidence` - number - model confidence score

## Notes

- keep field names stable
- use the same `video_id` through all services
- `frames` from this output become the input for the analytics service
