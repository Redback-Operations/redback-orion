# AFL Player Tracking with YOLO + ByteTrack

This project detects and tracks AFL players in match footage using a custom-trained YOLO model with ByteTrack for object tracking.

## Overview

The pipeline first uses YOLO to detect players in each video frame. ByteTrack then links detections across frames to assign consistent tracking IDs to players as they move through the footage.

This allows the project to produce player bounding boxes, tracking IDs, annotated videos, and optional CSV logs for further analysis.

## Files

- `best(CAR_vs_GCS).pt` — trained YOLO model weights for Carlton vs Gold Coast footage
- `run.py` — main script used to run the full detection and tracking pipeline
- `track.py` — handles player tracking using ByteTrack
- `draw.py` — draws bounding boxes, labels, and tracking IDs on video frames
- `video_io.py` — manages video reading and output video writing
- `csv_logger.py` — saves tracking results such as frame number, track ID, and bounding box coordinates
- `notebook(CAR_vs_GCS).ipynb` — notebook used for experimentation, training, or testing

## Usage

Place the input video in the project folder and run:

```bash
python run.py