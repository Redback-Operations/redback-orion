# Stampede Detection

## Overview

The Stampede Detection module analyses crowd video to identify abnormal crowd movement and potential stampede events.

The pipeline performs:

- Consecutive video-frame extraction
- YOLOv8 head detection
- BoT-SORT multi-object tracking
- Movement and acceleration analysis
- Farneback optical-flow analysis
- Crowd-density and movement analysis
- Risk scoring
- Abnormal movement detection
- Stampede event grouping
- JSON output generation

## Pipeline

```text
Video Input
    ↓
Consecutive Frame Extraction
    ↓
YOLOv8 Head Detection
    ↓
BoT-SORT Tracking
    ↓
Movement Analysis
    ↓
Optical Flow Analysis
    ↓
Risk Scoring
    ↓
Stampede Event Detection
    ↓
JSON Outputs
```

## Files

### `main.py`

Entry point for the Stampede Detection pipeline.

It accepts either:

- A raw video path
- A Video Processing result containing the original `video_path`

When receiving a Video Processing result, Stampede Detection uses the original video and performs its own consecutive-frame extraction.

### `stampede_detection.py`

Contains the core Stampede Detection implementation, including:

- YOLOv8 detection
- BoT-SORT tracking
- Optical-flow analysis
- Movement analysis
- Risk scoring
- Abnormal movement detection
- Event grouping
- JSON output generation

## Video Processing Integration

Stampede Detection can receive the result produced by the Video Processing pipeline:

```python
from video_processing.pipeline import process_input_video
from stampede_detection.main import analyze_stampede

video_result = process_input_video(
    video_path,
    "test_run"
)

result = analyze_stampede(
    video_result,
    camera_id="CAM_02",
    zone_id="ZONE_B"
)
```

The Video Processing frame list is not used directly by Stampede Detection.

Stampede Detection extracts and processes consecutive frames from the original video.

## Standalone Usage

Stampede Detection can also be run directly using a video path:

```python
from stampede_detection.main import analyze_stampede

result = analyze_stampede(
    "/path/to/video.avi",
    video_id="test_run",
    camera_id="CAM_02",
    zone_id="ZONE_B"
)
```

## Outputs

Outputs are generated under:

```text
data/output/stampede_runs/<video_id>/
```

### `stampede_events.json`

Contains grouped confirmed stampede events.

### `stampede_output.json`

Contains the complete frame-level detection output, including normal frames, together with grouped abnormal events.

Frame-level detections include fields such as:

- `frame_id`
- `timestamp`
- `camera_id`
- `zone_id`
- `stampede_detected`
- `confidence`
- `severity`
- `crowd_count`
- `movement_direction`
- `movement_speed`
- `abnormal_movement`

## Test Results

The pipeline was tested using:

```text
Crowd-Activity-All.avi
```

The test processed:

- 7,739 consecutive frames
- YOLOv8 + BoT-SORT tracking
- Optical flow across 7,739 frames
- 9 grouped events

Generated outputs:

```text
stampede_events.json
stampede_output.json
```
