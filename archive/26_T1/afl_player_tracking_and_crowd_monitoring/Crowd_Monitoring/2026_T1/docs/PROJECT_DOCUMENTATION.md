# Crowd Monitoring Project Documentation

## Overview

This document provides a complete overview of the Crowd Monitoring module for the Orion project. It is based on the trimester plan provided in the team guidance document and summarises the project scope, task structure, pipeline, expected outputs, and implementation direction.

The main purpose of this project is to analyse stadium footage and generate crowd analytics that can be integrated into the Orion system. The module focuses on crowd density, crowd distribution, heatmap generation, structured analytics output, and crowd behaviour analysis. An optional extension is attendance prediction using machine learning.

## Project Objective

The objective of the Crowd Monitoring module is to develop a crowd analytics pipeline that can:

- analyse stadium footage
- detect spectators
- estimate crowd density and distribution
- generate heatmaps
- produce structured analytics outputs
- support crowd behaviour analysis
- optionally explore attendance prediction

## High-Level Pipeline

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
Behaviour Analysis / Optional Prediction
```

## Core Technology Stack

- Python
- OpenCV
- YOLOv8 (Ultralytics)
- NumPy
- Pandas
- Matplotlib
- Scikit-learn

## Task Breakdown

The project is organised into 7 main tasks.

### 1. Video Processing

#### Purpose

Prepare raw stadium footage for the rest of the pipeline.

#### Main Work

- load video files
- read and extract frames
- sample frames if needed
- collect metadata such as frame count, frame size, and FPS

#### Expected Output

- extracted frames
- frame metadata
- a reusable preprocessing script or notebook


### 2. Crowd Detection

#### Purpose

Detect spectators in stadium footage at the person level.

#### Main Work

- run YOLOv8 on extracted frames
- identify people in the scene
- store detections with coordinates and confidence values
- visualise sample detections

#### Expected Output

- person detections
- bounding boxes
- structured detection data


### 3. Density and Zoning

#### Purpose

Convert detections into measurable crowd density and zone-level analytics.

#### Main Work

- count detected people
- divide the scene into zones or grid regions
- calculate density per zone
- normalise density values for comparison

#### Expected Output

- zone counts
- density summaries
- tables for further analysis


### 4. Heatmap Generation

#### Purpose

Visualise where the crowd is concentrated in the stadium view.

#### Main Work

- generate heatmaps from detections or density values
- create overlay visualisations on video frames or images
- export visual examples

#### Expected Output

- heatmap images
- overlay outputs
- visual density summaries


### 5. Analytics Output

#### Purpose

Create structured outputs for integration with the Orion dashboard and related services.

#### Main Work

- export JSON files
- export CSV files
- define output schema
- keep results suitable for backend and frontend use

#### Expected Output

- analytics JSON
- analytics CSV
- schema documentation


### 6. Crowd Behaviour Analytics

#### Purpose

Analyse movement patterns in the crowd and identify unusual or risky behaviour.

#### Main Work

- analyse movement across frames
- detect sudden crowd movement
- detect abnormal behaviour
- detect crowd surges

#### Expected Output

- event flags
- movement summaries
- behaviour-oriented analytics

### 7. Attendance Prediction (Optional Extension)

#### Purpose

Explore a predictive analytics component if time permits.

#### Main Work

- gather historical match data
- build a basic machine learning model
- predict attendance based on features such as teams, venue, ladder position, and round

#### Expected Output

- predicted attendance values
- a baseline evaluation summary

## Task Dependencies

The tasks are connected in a practical sequence:

1. `video_processing` prepares usable input.
2. `crowd_detection` produces person-level detections.
3. `density_zoning` converts detections into measurable crowd metrics.
4. `heatmap` visualises density and distribution.
5. `analytics_output` packages the results for integration.
6. `crowd_behaviour_analytics` extends the pipeline with movement-based insights.
7. `prediction_optional` is independent from the core video pipeline and should only be attempted if time permits.

## Expected Deliverables

By the end of the trimester, the module should ideally provide:

- a working video-to-analytics pipeline
- sample processed video or frame outputs
- person detection results
- density and zoning metrics
- crowd heatmaps
- JSON and CSV analytics outputs
- prototype crowd behaviour analysis
- optional attendance prediction work if completed

## Suggested Repository Usage

- Keep reusable helper functions in `shared/`
- Keep planning notes or extended documentation in `docs/`
- Keep each task folder focused on one part of the project
- Add examples, scripts, notebooks, or small reports inside the relevant task folders

## Notes

- The attendance prediction task is optional and should not delay core crowd-monitoring work.
- The behaviour analytics task can begin with simple heuristics before moving to more advanced methods.
- The first stable milestone should be a clean pipeline from video input to structured crowd analytics output.
