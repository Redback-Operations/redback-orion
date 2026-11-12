# Crowd Monitoring Module (Orion Project)

## Overview

This folder contains the Crowd Monitoring module for the Orion project.

The module is organised into:

- task folders for implementation work
- a shared schema layer for agreed JSON contracts
- a shared service layer for FastAPI integration

The goal is to let team members work independently while keeping inputs and outputs consistent for backend integration.

## Objectives

- detect people in stadium footage
- estimate density across zones
- generate heatmaps
- analyse crowd behaviour
- identify risk zones
- keep JSON input and output formats clear for backend work

## Pipeline

```text
Video Input
    ->
Video Processing
    ->
Crowd Region Preprocessing (exclude mask)
    ->
Crowd Detection
    ->
Density Zoning
    ->
Heatmap
    ->
Crowd Behaviour Analytics
    ->
Crowd Allocation / Risk Zone
```

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
Frame Extraction + Tiling (OpenCV)
    |
    v
Crowd Region Masking (exclude polygons)
    |
    v
Person Detection (YOLO26m CrowdHuman, tiled)
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
- FastAPI
- Uvicorn
- Ultralytics YOLO (YOLO26m trained on CrowdHuman for people detection)
- Inference backends: ONNX Runtime + DirectML (AMD/Intel GPU), CUDA/TensorRT (NVIDIA), OpenVINO (CPU)
- OpenCV
- NumPy
- Pandas

## Task Folders

Each task folder is mainly for implementation.

Each member should use:

- `README.md` for task guidance
- `SCHEMA.md` for exact input and output format
- `main.py` for implementation
- `output/` for generated files

Current task folders:

- `video_processing/`
- `crowd_region_preprocessing/` - masks fixed non-crowd regions (roof, signage, rails); includes the `pick_region.py` polygon picker
- `crowd_detection/`
- `density_zoning/`
- `heatmap/`
- `analytics_output/`
- `crowd_behaviour_analytics/`
- `crowd_allocation_risk_zone/`
- `prediction_optional/`

Supporting folders:

- `benchmarking/` - compares detection models against ground-truth counts (see its README)
- `test_pipeline.py` - runs the pipeline end to end from the command line

## Shared Folder

### `shared/config/`

Contains shared JSON settings: `video_processing_config.json` (tiling grid) and `crowd_region_preprocessing_config.json` (exclude polygons).

### `shared/schemas/`

Contains the agreed request and response JSON contracts for the services, including the combined `crowd_pipeline_schema.md`.

### `shared/services/`

Contains the FastAPI service layer:

- `main.py` starts the app
- `routes.py` defines the endpoints
- `models.py` defines typed request and response models
- service files call functions from the task folders

### `shared/timing.py`

The `timed()` helper the service layer uses to record stage timings for the combined benchmark report.

## Current Structure

```text
crowd_monitoring/
|- README.md
|- requirements.txt
|- Dockerfile
|- test_pipeline.py
|- data/
|- docs/
|- benchmarking/
|- shared/
|  |- README.md
|  |- timing.py
|  |- config/
|  |- schemas/
|  `- services/
|- video_processing/
|- crowd_region_preprocessing/
|- crowd_detection/
|- density_zoning/
|- heatmap/
|- analytics_output/
|- crowd_behaviour_analytics/
|- crowd_allocation_risk_zone/
`- prediction_optional/
```

## Service Flow

```text
Frontend / Backend
    ->
FastAPI Routes
    ->
Shared Service Files
    ->
Task Folder Implementations
    ->
Schema-based JSON Response
```

## API Endpoints

The current service layer exposes:

- `POST /process-detection`
- `POST /process-analytics`
- `POST /process-intelligence`
- `POST /process-crowd-detection` - full pipeline in one call; this is the endpoint the frontend uses
- `GET /demo` - demo page for the full pipeline

These endpoints use typed FastAPI models so Swagger can show clear request and response formats.
Each full-pipeline run also prints one combined `PIPELINE BENCHMARK` report to the server console.

## Working Rule

- task folders contain implementation
- task `SCHEMA.md` files define internal handoff format
- `shared/schemas/` defines service-level contract
- `shared/services/models.py` defines typed API models for Swagger and validation
- service files should follow schema definitions exactly
- do not add extra JSON wrapper layers unless the team agrees

## Getting Started

1. Read this root `README.md`
2. Open your assigned task folder
3. Read `README.md` and `SCHEMA.md`
4. Implement your task in `main.py`
5. Save outputs in `output/`
6. Keep your input and output aligned with the agreed schema

## Install Dependencies

```bash
pip install -r requirements.txt
```

`requirements.txt` installs a CPU-only setup (crowd detection runs on OpenVINO). Crowd detection
automatically uses the fastest backend available (`CROWD_DEVICE=auto`), so installing
one of the following is enough to switch to the GPU:

- **NVIDIA** - install the CUDA build of torch *before* the base requirements:
  ```bash
  pip install -r requirements-nvidia.txt
  pip install -r requirements.txt
  ```
  If a CPU-only torch is already installed, add `--force-reinstall` to the first command.
- **AMD / Intel (DirectML, Windows)** - remove other onnxruntime builds, install, then export the ONNX model (it isn't in git):
  ```bash
  pip uninstall -y onnxruntime onnxruntime-gpu onnxruntime-directml
  pip install -r requirements-amd.txt
  yolo export model=crowd_detection/yolo26mcrowdpeoplefaces.pt format=onnx imgsz=640 dynamic=True opset=17
  ```

Each file's header comments explain the steps and how to check the GPU is being used.

See `crowd_detection/README.md` for all backend options.

## Run FastAPI Service

```bash
uvicorn shared.services.main:app --reload
```

## Open Swagger UI

After the server starts, open:

```text
http://127.0.0.1:8000/
```

In the current setup, Swagger UI is served on the root URL.

## Collaboration Notes

- backend team should use `shared/schemas/` as the source of truth
- FastAPI Swagger is generated from `shared/services/models.py`
- implementation teams should follow their task `SCHEMA.md`
- if a field name changes, update schema first and then update service and task code
## 👥 Team Tasks (7 Members)

Each team member owns one task. Follow the README in each task folder for detailed objectives and deliverables.

| # | Task Folder | Team Member | Objective |
|---|-------------|-------------|-----------|
| 1 | **video_processing** | Member 1 | Extract frames and prepare video data |
| 2 | **crowd_detection** | Member 2 | Detect persons using YOLO (tiled, crowd-masked) |
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
crowd_monitoring/
|-- data/                           # Sample videos and frames
|-- docs/                           # Documentation and notes
|-- shared/                         # Common utilities and configs
|-- benchmarking/                   # Detection model benchmarking
|-- requirements.txt                # Dependencies
|-- README.md                       # This file
|
|-- Task Folders (one per member):
|-- video_processing/               # Task 1: Video extraction & preparation
|-- crowd_region_preprocessing/     # Exclude-mask for non-crowd regions
|-- crowd_detection/                # Task 2: Person detection (YOLO26m, tiled)
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
crowd_region_preprocessing
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
