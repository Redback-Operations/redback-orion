# Video Processing Task Schema

## Purpose

This task receives the raw video reference and prepares frame data for the crowd detection task.

## Input JSON

```json
{
  "video_id": "match_01",
  "video_path": "data/raw/match_01.mp4"
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
      "frame_path": "output/frame_0001.jpg"
    }
  ]
}
```

## Notes

- output of this task becomes input to `crowd_detection`
- keep `video_id`, `frame_id`, and `timestamp` stable
