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

## Tech Stack

- Python
- FastAPI
- Uvicorn
- YOLOv8 (Ultralytics)
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
- `crowd_detection/`
- `density_zoning/`
- `heatmap/`
- `analytics_output/`
- `crowd_behaviour_analytics/`
- `crowd_allocation_risk_zone/`
- `prediction_optional/`

## Shared Folder

### `shared/config/`

Contains shared settings such as thresholds, paths, and common configuration values.

### `shared/schemas/`

Contains the agreed request and response JSON contracts for the 3 services.

### `shared/services/`

Contains the FastAPI service layer:

- `main.py` starts the app
- `routes.py` defines the endpoints
- `models.py` defines typed request and response models
- service files call functions from the task folders

## Current Structure

```text
2026_T1/
|- README.md
|- requirements.txt
|- data/
|- docs/
|- shared/
|  |- README.md
|  |- config/
|  |- schemas/
|  `- services/
|- video_processing/
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

The current service layer exposes 3 main endpoints:

- `POST /process-detection`
- `POST /process-analytics`
- `POST /process-intelligence`

These endpoints use typed FastAPI models so Swagger can show clear request and response formats.

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
