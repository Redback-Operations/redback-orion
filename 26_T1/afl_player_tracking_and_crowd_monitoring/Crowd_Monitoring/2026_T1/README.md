# Crowd Monitoring Module (Orion Project)

## Overview

This repository contains the Crowd Monitoring module for the Orion project under Redback Operations.

The purpose of this module is to analyse stadium crowd behaviour and density using computer vision and data analytics. The expected outputs include:

- crowd heatmaps
- density metrics
- zone-based analytics
- behaviour insights for integration into the Orion analytics dashboard

## Objectives

- Detect and analyse spectators in stadium footage
- Estimate crowd density and distribution
- Generate zone-based crowd analytics
- Produce crowd heatmaps and visualisations
- Develop AI-based crowd behaviour analysis
- Optionally predict future attendance using machine learning models

## Proposed Pipeline

```text
Video Input
    |
    v
Frame Extraction (OpenCV)
    |
    v
Person Detection (YOLOv8)
    |
    v
Crowd Density Estimation
    |
    v
Zone-based Analysis
    |
    v
Heatmap Generation
    |
    v
Analytics Output (JSON / CSV)
    |
    v
Behaviour Analysis / Prediction
```

## Tech Stack

- Python
- YOLOv8 (Ultralytics)
- OpenCV
- NumPy
- Pandas

## 👥 Team Tasks (7 Members)

Each team member owns one task. Follow the README in each task folder for detailed objectives and deliverables.

| # | Task Folder | Team Member | Objective |
|---|-------------|-------------|-----------|
| 1 | **video_processing** | Member 1 | Extract frames and prepare video data |
| 2 | **crowd_detection** | Member 2 | Detect persons using YOLOv8 |
| 3 | **density_zoning** | Member 3 | Calculate density and zone-based analytics |
| 4 | **heatmap** | Member 4 | Generate crowd heatmaps |
| 5 | **analytics_output** | Member 5 | Create reports and output files (JSON/CSV) |
| 6 | **crowd_behaviour_analytics** | Member 6 | Analyze crowd movement and behavior patterns |
| 7 | **crowd_allocation_risk_zone** | Member 7 | Assess risk levels and crowd allocation strategy |

**Optional:** `prediction_optional/` - Attendance prediction (if time permits)

---

## Task Guidance

Each task folder contains its own `README.md` with:

- 🎯 Task objective
- 📥 Expected inputs and outputs
- 💡 Implementation notes
- ✅ Suggested deliverables

This keeps the semester plan split into smaller, easier-to-manage work packages.

---

## Project Structure

```text
2026_T1/
|-- data/                           # Sample videos and frames
|-- docs/                           # Documentation and notes
|-- shared/                         # Common utilities and configs
|-- requirements.txt                # Dependencies
|-- README.md                       # This file
|
|-- Task Folders (one per member):
|-- video_processing/               # Task 1: Video extraction & preparation
|-- crowd_detection/                # Task 2: Person detection (YOLOv8)
|-- density_zoning/                 # Task 3: Density & zone analysis
|-- heatmap/                        # Task 4: Heatmap generation
|-- analytics_output/               # Task 5: Report generation
|-- crowd_behaviour_analytics/      # Task 6: Behavior analysis
|-- crowd_allocation_risk_zone/     # Task 7: Risk assessment & allocation
|
|-- Optional:
`-- prediction_optional/            # Optional: Attendance prediction
```

---

## 🚀 Getting Started

1. **Find your task** in the table above
2. **Read the README** in your task folder
3. **Follow the implementation notes**
4. **Deliver outputs** as specified
5. **Update your README** with progress

---

## 📋 Integration Points

Tasks run in sequence:

```
video_processing (Task 1)
         ↓
crowd_detection (Task 2)
         ↓
density_zoning (Task 3)
         ↓
heatmap (Task 4) + analytics_output (Task 5)
         ↓
crowd_behaviour_analytics (Task 6)
crowd_allocation_risk_zone (Task 7)
         ↓
         ↓
Dashboard / Report Integration
```

---

## 💬 Collaboration

- **Shared utilities:** Use files in `shared/` folder
- **Input/Output:** Check task README for I/O specifications
- **Questions:** Document in docs/ folder
- **Results:** Save outputs to designated location in your task folder
