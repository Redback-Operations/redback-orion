# Detection Service Schema

## Endpoint

`POST /process-detection`

## Purpose

This service receives a video reference and runs three stages: video processing,
crowd region preprocessing (exclude-mask) and crowd detection. It returns people
(and optionally face) detections for each processed frame.

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
      "frame_path": "video_processing/data/extracted_frames/frame_0001.jpg",
      "annotated_frame_path": null,
      "face_annotated_frame_path": null,
      "people_annotated_frame_path": "crowd_detection_output/people_detection_results/match_01/frame_0001.jpg",
      "person_count": 2,
      "face_count": null,
      "face_detections": [],
      "people_detections": [
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
- `frame_path` - string - original extracted frame path from video processing
- `annotated_frame_path` - string or null - legacy field; not currently populated (always null). Use `people_annotated_frame_path`
- `face_annotated_frame_path` - string or null - saved frame with face boxes; null when face detection is off (the default) or on frames where the detector did not run
- `people_annotated_frame_path` - string or null - saved frame with people boxes, under `crowd_detection_output/people_detection_results/<video_id>/`; null on frames where the detector did not run (detections are reused from an earlier frame and not redrawn)
- `person_count` - integer - number of detected people in the frame
- `face_count` - integer or null - number of detected faces; null when face detection is off
- `face_detections` - list - detected faces in the frame (empty when face detection is off)
- `people_detections` - list - detected people in the frame
- `bbox` - list of 4 integers - bounding box as `[x1, y1, x2, y2]` in full-frame pixels
- `confidence` - number - model confidence score

## Internal-Only Fields

`process_detection()` returns more than the endpoint does. FastAPI's
`response_model` (`DetectionResponse`) drops these fields from the HTTP
response, but in-process callers such as the full pipeline service can use them:

- `frames[].detected` - boolean - `true` if the detector ran on this frame; `false` if the detections were reused from the previous detected frame (see `CROWD_DETECT_STRIDE`)
- `frames[].detection_ms` - number - inference time for this frame (0 for reused frames)
- `frame_width` / `frame_height` - integer - source frame size
- `detection_summary` - object - per-run model/backend/device, timings and peak count (also written to `crowd_detection_output/detection_summary_run_NNN.json`)
- `stage_timings_ms` - object - wall time in ms for `video_processing`, `crowd_preprocessing` and `crowd_detection`
- `video_processing_timings` - object - detailed timing breakdown from `process_video`

## Notes

- use `people_detections` for explicit people-detection output
- use `face_detections` for explicit face-detection output (only populated when `USE_FACE_DETECTION` is on)
- `frames` from this output become the input for the analytics service
- detections are carried forward between detected frames, so every frame has a `person_count` even if the detector didn't run on it
