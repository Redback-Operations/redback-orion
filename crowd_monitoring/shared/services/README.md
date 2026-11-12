# Services Folder

This folder contains the shared service layer (FastAPI) for the Crowd Monitoring module.

## Structure

```text
services/
|- README.md
|- main.py                         # FastAPI app, /demo page, /artifacts static files
|- routes.py                       # API endpoints
|- models.py                       # Pydantic request/response models (Swagger)
|- crowd_detection_service.py      # video processing -> region preprocessing -> detection
|- crowd_analytics_service.py      # density zoning -> heatmap
|- crowd_intelligence_service.py   # behaviour analytics -> risk zones
`- crowd_pipeline_service.py       # full pipeline for the frontend
```

## Folder Purpose

This folder does not contain the full implementation of each task.

Instead, it provides the service flow:

- receive API request
- route the request
- call functions from task folders
- return structured JSON output

## Endpoints

| Endpoint | Service | Schema |
|----------|---------|--------|
| `POST /process-detection` | `crowd_detection_service.process_detection` | `shared/schemas/detection_schema.md` |
| `POST /process-analytics` | `crowd_analytics_service.process_analytics` | `shared/schemas/analytics_schema.md` |
| `POST /process-intelligence` | `crowd_intelligence_service.process_intelligence` | `shared/schemas/intelligence_schema.md` |
| `POST /process-crowd-detection` | `crowd_pipeline_service.process_crowd_detection` | `shared/schemas/crowd_pipeline_schema.md` |
| `GET /` | Swagger UI | |
| `GET /demo` | Demo page that calls `/process-crowd-detection` | |
| `GET /artifacts/<path>` | Serves generated images (paths relative to `crowd_monitoring/`) | |

Run it from `crowd_monitoring/`:

```bash
uvicorn shared.services.main:app --reload
```

## File Purpose

### `main.py`

- creates the FastAPI application and loads the routes
- mounts `crowd_monitoring/` at `/artifacts` so the demo page can show output images
- serves the `/demo` page

### `routes.py`

- contains the API endpoints
- calls the correct service file for each endpoint
- `/process-crowd-detection` catches pipeline errors and returns a 500 JSON body with `detail`, `error_type`, the last 8 `traceback` lines, `video_id` and `stage`. The full traceback is printed to the server console, and `detail` is never blank (it falls back to the exception type)

### `models.py`

- Pydantic models used as `response_model` for each route
- a route's response only contains fields declared on its model; anything else the service returns is dropped from the HTTP response. For example, `detected`, `detection_ms` and `detection_summary` from crowd detection are not returned by `/process-detection`
- `CrowdPipelineResponse` includes `stage_timings_ms`

### `crowd_detection_service.py`

- calls task implementations in order:
  - `video_processing/main.py` - `process_video`
  - `crowd_region_preprocessing/main.py` - `prepare_crowd_frames`
  - `crowd_detection/main.py` - `detect_crowd`
- times each stage using `shared/timing.py` and attaches the results as `stage_timings_ms`, along with `video_processing_timings` from `process_video`

### `crowd_analytics_service.py`

- calls task implementations from:
  - `density_zoning/main.py`
  - `heatmap/main.py`

### `crowd_intelligence_service.py`

- calls task implementations from:
  - `crowd_behaviour_analytics/main.py`
  - `crowd_allocation_risk_zone/main.py`

### `crowd_pipeline_service.py`

- runs detection -> analytics -> behaviour -> risk, then assembles the frontend payload (`summary`, `peak_crowd_frame`, `anomaly_visual`, `heatmap`, `time_series_chart`, `density_extremes`)
- times each stage (`detection`, `analytics`, `behaviour`, `risk`, `assemble`) and returns them as `stage_timings_ms`
- prints **one** combined `PIPELINE BENCHMARK` report to the console at the end of each run. The stages no longer print their own output while running, so this report is the only benchmark output:

```text
========== PIPELINE BENCHMARK ==========

VIDEO PROCESSING
-----------------------------------------------
Video stats / decoding / blur / CLAHE / tiling / JPEG writing timings, frame counts

CROWD DETECTION
-----------------------------------------------
Model (backend on device), model load, frame I/O, inference, peak people/frame, summary json

STAGE TIMINGS
-----------------------------------------------
video_processing, crowd_preprocessing, crowd_detection, detection, analytics, behaviour, risk, assemble
TOTAL
```

## Service Flow

```text
Request
-> routes.py
-> related service file
-> task folder implementation
-> result returned as JSON
```

## Important Rule

- task folders contain the implementation
- service files call task functions
- routes define endpoints
- `main.py` starts the API app

Keep this folder thin and simple. Do not duplicate business logic here if it already exists in a task folder.
