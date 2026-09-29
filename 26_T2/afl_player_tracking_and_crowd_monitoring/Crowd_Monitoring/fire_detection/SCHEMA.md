# Fire Detection Task Schema

## Purpose

This task receives extracted-frame metadata from Video Processing and
produces a per-frame fire/smoke detection result for each frame, for
handoff to Data Aggregation.

## Input JSON

```json
{
  "video_id": "VID_001",
  "video_path": "/videos/stadium_cam_01.mp4",
  "frame_width": 1920,
  "frame_height": 1080,
  "frames": [
    {
      "frame_id": 1,
      "timestamp": 0.0,
      "frame_path": "/frames/VID_001/frame_000001.jpg"
    }
  ]
}
```

`camera_id` / `zone_id` are not part of this input; they are passed
into `process_video(frame_metadata, camera_id, zone_id)` directly by
the caller (see Notes).

## Output JSON

```json
{
  "video_id": "VID_001",
  "detections": [
    {
      "frame_id": 25,
      "timestamp": 1.0,
      "camera_id": "CAM_02",
      "zone_id": "ZONE_B",
      "fire_detected": true,
      "smoke_detected": true,
      "confidence": 0.94,
      "severity": "HIGH",
      "bounding_box": {"x": 850, "y": 320, "width": 180, "height": 200}
    },
    {
      "frame_id": 26,
      "timestamp": 1.04,
      "camera_id": "CAM_02",
      "zone_id": "ZONE_B",
      "fire_detected": false,
      "smoke_detected": false,
      "confidence": 0.03,
      "severity": "NONE"
    }
  ]
}
```

## Field Notes

- `severity` is one of `NONE` / `LOW` / `MEDIUM` / `HIGH`, bucketed
  from `confidence`.
- `bounding_box` is present only when `fire_detected` is `true` (the
  single largest fire-colored region in the frame). It is omitted
  entirely, not set to `null`, when nothing is detected.
- `confidence` is derived from the detected blob's area relative to
  the frame, not a trained-model probability — it's a best-effort
  signal, not a calibrated score.
- A `"no detection"` frame still reports `confidence: 0.03` rather
  than `0.0`.

## Notes

- Output of this task is consumed by `data_aggregation` (joined onto
  a zone alongside `crowd_detection` and `stampede_detection`
  results).
- `camera_id` / `zone_id` must be supplied by the caller per video —
  see the Implementation Notes in `README.md`.
