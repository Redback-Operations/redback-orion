# Crowd Detection Task Schema

## Purpose

This task receives processed frame data and returns per-frame face and people detections.

## Input JSON

```json
{
  "video_id": "match_01",
  "frames": [
    {
      "frame_id": 1,
      "timestamp": 0.04,
      "frame_path": "video_processing/data/extracted_frames/frame_0001.jpg"
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
      "frame_path": "video_processing/data/extracted_frames/frame_0001.jpg",
      "annotated_frame_path": "crowd_detection_output/people_detection_results/frame_0001.jpg",
      "face_annotated_frame_path": "crowd_detection_output/face_detection_results/frame_0001.jpg",
      "people_annotated_frame_path": "crowd_detection_output/people_detection_results/frame_0001.jpg",
      "person_count": 2,
      "face_count": 1,
      "face_detections": [
        {
          "bbox": [110, 60, 145, 100],
          "confidence": 0.88
        }
      ],
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

## Notes

- output of this task becomes input to `density_zoning`
- this output must also match the detection service schema
- `face_detections` and `people_detections` are explicit task outputs
