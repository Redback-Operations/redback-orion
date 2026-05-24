# Player Tracking Logic Pipeline

This folder contains the core workflow and supporting modules for the AFL player tracking and tactical analysis system developed in the `Player-Tracking` branch of the Orion project.

Repository Branch:

- https://github.com/lucastargett/redback-orion/tree/Player-Tracking

The system combines:

- YOLOv11 player detection
- ByteTrack multi-object tracking
- Jersey color clustering and team classification
- Tactical formation visualization
- Movement analytics
- Speed and acceleration estimation
- Player path analysis
- Tackle detection

---

# System Overview

The pipeline transforms a raw AFL match video into structured tracking and tactical analysis outputs.

The workflow is modular, meaning each component can be independently improved or replaced.

---

# Workflow Graph

```text
┌────────────────────────────┐
│ Input AFL Match Video      │
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
│ Optional Fine-Tuned YOLO   │
│ Model (.pt)                │
└────────────┬───────────────┘
             │
             ▼
┌──────────────────────────────────────────────┐
│ Yolov11_ByteTrack_Player_Tracking            │
│                                              │
│ - Player Detection                           │
│ - Multi-Object Tracking                      │
│ - Persistent Tracking IDs                    │
│ - Bounding Box Extraction                    │
└────────────┬─────────────────────────────────┘
             │
             │ Tracking JSON Output
             ▼
┌──────────────────────────────────────────────┐
│ 26T1_Re-Identification-Quan/                 │
│ JerseyColorDetection                         │
│                                              │
│ - Extract jersey colors                      │
│ - Team clustering                            │
│ - Referee classification                     │
│ - Assign team labels to tracked players      │
└────────────┬─────────────────────────────────┘
             │
             │ Clustered Team JSON Output
             ▼
 ┌────────────────────────────────────────────┐
 │ Tactical & Analytics Modules               │
 └────────────────────────────────────────────┘
             │
             ├───────────────────────────────►
             │    26T1-Formation_Visualization
             │
             │    - Team structure analysis
             │    - Formation connectivity
             │    - Spatial relationship mapping
             │
             ├───────────────────────────────►
             │    Speed & Acceleration
             │
             │    - Velocity estimation
             │    - Sprint analysis
             │    - Acceleration tracking
             │
             ├───────────────────────────────►
             │    Player Path Visualization
             │
             │    - Heatmap generation
             │    - Movement trajectories
             │    - Positional analysis
             │
             ▼
┌────────────────────────────┐
│ Final Tactical Insights    │
│ and Visual Analytics       │
└────────────────────────────┘


Independent Module
──────────────────────────────────────────────

┌────────────────────────────┐
│ tackle_detection_          │
│ shafqat_ullah              │
│                            │
│ - Direct tackle detection  │
│ - Uses fine-tuned model    │
│ - Does NOT require jersey  │
│   clustering JSON          │
└────────────────────────────┘
```

---

# Pipeline Stages

## 1. Video Input

The system begins with:

- An AFL match video
- Optionally, a fine-tuned YOLO model (`.pt`)

The fine-tuned model improves:

- Player detection accuracy
- Occlusion handling
- AFL-specific object recognition

---

# Core Modules

---

## Yolov11_ByteTrack_Player_Tracking

Primary tracking engine responsible for:

- Detecting players
- Assigning persistent tracking IDs
- Maintaining player identity across frames
- Exporting structured tracking results

### Input

- AFL video
- YOLOv11 model

### Output

Tracking JSON containing:

- Frame information
- Bounding boxes
- Tracking IDs
- Detection confidence
- Coordinates

### Purpose

This stage establishes the foundational player tracking data used by all downstream modules.

---

## 26T1_Re-Identification-Quan/JerseyColorDetection

This module performs player re-identification using jersey color clustering.

### Responsibilities

- Extract jersey color regions
- Cluster players into:
  - Team 1
  - Team 2
  - Referee
- Attach team labels to tracked players

### Input

Tracking JSON from:

```text
Yolov11_ByteTrack_Player_Tracking
```

### Output

Enhanced JSON containing:

- Tracking IDs
- Team classification
- Cluster labels
- Player positional data

### Importance

This module converts raw tracking data into semantically meaningful team information.

Without this step:

- Tactical formation analysis becomes unreliable
- Team-based analytics cannot be computed

---

# Tactical and Analytics Modules

These modules consume the clustered team JSON.

---

## 26T1-Formation_Visualization

Formation analysis and spatial connectivity visualization.

### Features

- Draws connections between teammates
- Detects formation structures
- Identifies disconnected formations
- Visualizes tactical spacing

### Planned Logic

- Lines connect same-team players
- Opponent obstruction can fade connections
- Dense crowd situations may suppress visualization to reduce noise

### Input

Clustered team JSON from:

```text
JerseyColorDetection
```

---

## Speed and Acceleration Estimation

Player movement analytics module.

### Features

- Speed estimation
- Acceleration computation
- Sprint intensity analysis
- Temporal movement tracking

### Planned Output

- Per-player movement statistics
- Speed graphs
- Motion overlays

---

## Player Path Visualization

Trajectory and movement visualization system.

### Features

- Player movement paths
- Positional heatmaps
- Zone occupation analysis
- Tactical movement trends

### Planned Output

- Path overlays
- Tactical heatmaps
- Movement summaries

---

# Independent Module

## tackle_detection_shafqat_ullah

This module operates independently from the jersey color clustering pipeline.

### Features

- Detects tackle events directly
- Uses the fine-tuned detection model
- Does not require:
  - Team clustering JSON
  - Jersey classification output

### Input

- AFL video
- Fine-tuned model

### Advantage

This allows tackle analysis to run separately from the complete tactical analysis pipeline.

---

# Folder Structure Overview

```text
Player-Tracking/
│
├── Yolov11_ByteTrack_Player_Tracking/
│   ├── Player detection
│   ├── Tracking
│   └── Tracking JSON generation
│
├── 26T1_Re-Identification-Quan/
│   │
│   ├── JerseyColorDetection/
│   │   ├── Jersey extraction
│   │   ├── Team clustering
│   │   └── Team JSON generation
│   │
│   └── 26T1-Formation_Visualization/
│       ├── Formation graphs
│       ├── Tactical connections
│       └── Spatial analysis
│
├── tackle_detection_shafqat_ullah/
│   ├── Tackle event detection
│   └── Direct model inference
│
├── colour_speed_detection_drew/
│   ├── 
│   └── 
│
├── 26T1_Tracking_Ethan/
│   ├── 
│   └── 
│
```

---

# Data Flow Summary

| Stage | Input | Output |
|---|---|---|
| Player Tracking | Video + YOLO model | Tracking JSON |
| Jersey Classification | Tracking JSON | Clustered Team JSON |
| Formation Visualization | Clustered Team JSON | Tactical visualization |
| Speed Analysis | Clustered Team JSON | Motion statistics |
| Path Visualization | Clustered Team JSON | Trajectory analytics |
| Tackle Detection | Video + model | Tackle events |

---

# Notes

- Most tactical modules depend on accurate tracking IDs.
- Team clustering quality directly increases tactical analysis accuracy significantly.
- Dense player occlusions remain one of the primary challenges in AFL analysis.
- Modular architecture allows independent experimentation and replacement of components.

---
