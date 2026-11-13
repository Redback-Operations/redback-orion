# Crowd Detection

## Objective

Detect spectators in stadium footage using a YOLOv8-based crowd detection pipeline.  
The module detects both faces and people from extracted video frames, saves annotated outputs, and returns structured results for later density and zone analysis.

## Current Implementation

The current implementation uses two YOLO models:

- Face detection model: `face_model.pt`
- People detection model: `yolov8n_crowdhuman.pt`

The people model is used for person-level crowd detection, while the face model is kept to support face-based crowd analysis where needed. The module loads both models and runs detection on each frame. :contentReference[oaicite:0]{index=0}

## Project Structure

```text
crowd_detection/
|- README.md
|- config.py
|- main.py
|- face_model.pt
|- yolov8n_crowdhuman.pt
```