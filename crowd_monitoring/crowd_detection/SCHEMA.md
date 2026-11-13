# Crowd Detection Task Schema

## Purpose

This task receives processed frame data (from `video_processing`, with the
`crowd_mask` attached by `crowd_region_preprocessing`) and returns per-frame
person detections plus a run summary.

## Input

`detect_crowd(processed_video)` takes the dict returned by
`crowd_region_preprocessing.prepare_crowd_frames()`:

```json
{
  "video_id": "match_01",
  "frame_width": 3840,
  "frame_height": 2160,
  "crowd_mask": "<numpy uint8 array, 255 = keep, 0 = excluded>",
  "frames": [
    {
      "frame_id": 1,
      "timestamp": 0.04,
      "frame_path": "video_processing/data/extracted_frames/frame_0001.jpg",
      "tiles": [
        { "row": 0, "column": 0, "x": 0, "y": 0, "width": 400, "height": 342 }
      ]
    }
  ]
}
```

- `crowd_mask` is optional; without it frames are not masked
- `tiles` is optional; frames without tile metadata are detected whole-frame

## Output JSON

```json
{
  "video_id": "match_01",
  "frame_width": 3840,
  "frame_height": 2160,
  "detection_summary": {
    "run": 12,
    "timestamp": "2026-09-16 14:02:11",
    "video_id": "match_01",
    "model": "yolo26mcrowdpeoplefaces.onnx",
    "backend": "onnx",
    "device": "dml",
    "openvino": false,
    "tiling": true,
    "frames_processed": 66,
    "frames_detected": 3,
    "detect_stride": 30,
    "detect_max_width": 1920,
    "skip_empty_tiles": true,
    "total_detection_seconds": 1.33,
    "ms_per_detected_frame": 443.3,
    "model_load_seconds": 1.8,
    "frame_io_seconds": 0.42,
    "peak_people_per_frame": 557,
    "summary_json_path": "crowd_detection_output/detection_summary_run_012.json"
  },
  "frames": [
    {
      "frame_id": 1,
      "timestamp": 0.04,
      "frame_path": "video_processing/data/extracted_frames/frame_0001.jpg",
      "face_annotated_frame_path": null,
      "people_annotated_frame_path": "crowd_detection_output/people_detection_results/match_01/frame_0001.jpg",
      "person_count": 2,
      "face_count": null,
      "detection_ms": 443.3,
      "detected": true,
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

## Frame Fields

- `detected` - boolean - `true` if the detector ran on this frame; `false` if the detections were reused from the last detected frame (only every `CROWD_DETECT_STRIDE`-th frame is detected)
- `detection_ms` - number - inference + tiling/NMS time for this frame; `0` for reused frames
- `people_annotated_frame_path` - string or null - only written for detected frames; `null` otherwise
- `face_annotated_frame_path`, `face_count` - null unless `USE_FACE_DETECTION` is on; `face_detections` is then `[]`
- `bbox` - `[x1, y1, x2, y2]` in full-frame pixel coordinates (tile boxes are already mapped back and de-duplicated)

## Notes

- output of this task becomes input to `density_zoning`; `crowd_behaviour_analytics` also reads `person_count` and `detected` to measure the crowd-state trend
- `detection_summary` is also written to `crowd_detection_output/detection_summary_run_NNN.json`, and the pipeline's combined benchmark report reads from it
- the `/process-detection` HTTP response only includes `video_id` and the frame fields in `shared/schemas/detection_schema.md`; `detected`, `detection_ms`, `detection_summary` and frame size are available to in-process callers only
