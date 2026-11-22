# AFL Tackle Detection & Crowd Interaction System

## Project: Redback Orion Capstone  
Module: Player Tracking & Crowd Monitoring  
Component: Tackle Detection Pipeline  
Author: Shafqat Ullah  
Team Lead: Quan  
Validator Module: Apaar (external integration module)

---

# 1. Overview

This system detects **tackle-like interaction events** in AFL matches using structured player tracking data and generates:

- Event-level JSON (backend-ready)
- CSV summary
- Annotated MP4 video output
- Optional validation results (Apaar module)

It does NOT use deep learning or object detection. Instead, it uses **spatiotemporal clustering heuristics** on tracking data.

---

# 2. Key Features

- CLI-based pipeline (no notebooks)
- Tracking CSV processing
- Density + clustering-based event detection
- Event grouping from consecutive frames
- Player involvement extraction
- Bounding box estimation per event
- Video overlay generation (MP4)
- Backend-compatible JSON schema
- External validator integration support

---

# 3. Project Structure

tackle_detection_shafqat_ullah/

├── tackle_detection.py
├── config.py
├── validator_integration.py
│
├── validation/
│   └── apaar_validator.py
│
├── sample_data/
│   ├── tracking.csv
│   └── sample_video.mp4
│
├── outputs/
│   ├── tackle_events.json
│   ├── tackle_events.csv
│   ├── tackle_detection_output.mp4
│   ├── validation_results.csv
│
└── README.md

---

# 4. Requirements

## Python Version
- Python 3.8+

## Install Dependencies

pip install pandas numpy opencv-python

---

# 5. Input Data Format

frame_id  
player_id  
timestamps_s  
x1  
y1  
x2  
y2  
cx  
cy  
w  
h  
confidence  

Notes:
- Each row = one player detection in a frame
- Bounding box coordinates must be valid
- timestamps_s required for timing

---

# 6. How to Run (CLI)

## Windows

python tackle_detection.py ^
--tracking sample_data/tracking.csv ^
--video sample_data/sample_video.mp4 ^
--output outputs ^
--fps 29.97

## Linux/Mac

python tackle_detection.py ^
--tracking sample_data/tracking.csv ^
--video sample_data/sample_video.mp4 ^
--output outputs ^
--fps 29.97 ^
--clip-duration 40

---

# 7. Outputs

## JSON Output

outputs/tackle_events.json

Contains:
- event_id
- frames
- timestamps
- players involved
- bounding boxes
- metrics

## CSV Output

outputs/tackle_events.csv

## Video Output

outputs/tackle_detection_output.mp4

---

# 8. Validation Module

validation/apaar_validator.py

Outputs:
- validation_results.csv

Based on:
- event duration heuristic

---

# 9. Pipeline Flow

Tracking CSV → Detection → JSON → Validator → CSV

---

# 10. Limitations

- Heuristic-based system
- No ML model
- No ground truth evaluation
- Sensitive to tracking quality

---

# END
