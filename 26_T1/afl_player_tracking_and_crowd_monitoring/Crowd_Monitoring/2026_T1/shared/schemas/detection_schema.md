# Detection Service Schema

## Endpoint

`POST /process-detection`

## Purpose

This service receives a video reference, runs video processing and crowd detection, and returns face and people detection results per processed frame.

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

## Output Fields

- `video_id` - string - same video identifier from the request
- `frames` - list - detection result for each processed frame
- `frame_id` - integer - frame number
- `timestamp` - number - time in seconds for the frame
- `frame_path` - string - original extracted frame path from video processing
- `annotated_frame_path` - string - default annotated frame path for downstream use; currently same as `people_annotated_frame_path`
- `face_annotated_frame_path` - string - saved frame with face boxes
- `people_annotated_frame_path` - string - saved frame with people boxes
- `person_count` - integer - number of detected people in the frame
- `face_count` - integer - number of detected faces in the frame
- `face_detections` - list - detected faces in the frame
- `people_detections` - list - detected people in the frame
- `bbox` - list of 4 integers - bounding box as `[x1, y1, x2, y2]`
- `confidence` - number - model confidence score

## Notes

- use `people_detections` for explicit people-detection output
- use `face_detections` for explicit face-detection output
- `frames` from this output become the input for the analytics service
